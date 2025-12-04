from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Annotated, Sequence, List, Literal ,TypedDict
from pydantic import BaseModel, Field 
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage,SystemMessage
from langchain_core.tools import tool
from langgraph.types import Command 
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent 
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
from langchain_openai import ChatOpenAI
import json
import asyncio
from langchain_core.tools import StructuredTool
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 启用CORS支持

def create_sync_tool_wrapper(async_tool):
    """创建同步工具包装器，将异步 MCP 工具转换为同步工具"""
    
    def sync_func(**kwargs):
        """同步包装函数，使用 asyncio.run 调用异步工具"""
        try:
            # 调用异步工具的 coroutine 函数
            result = asyncio.run(async_tool.coroutine(**kwargs))
            return result
        except Exception as e:
            logger.error(f"同步包装器执行异常: {e}")
            raise e
    
    # 创建新的同步 StructuredTool
    sync_tool = StructuredTool.from_function(
        func=sync_func,
        name=async_tool.name,
        description=async_tool.description,
        args_schema=async_tool.args_schema,
        return_direct=getattr(async_tool, 'return_direct', False)
    )
    
    logger.info(f"创建同步工具包装器: {async_tool.name}")
    return sync_tool

def convert_async_tools_to_sync(async_tools):
    """将异步工具列表转换为同步工具列表"""
    sync_tools = []
    for tool in async_tools:
        if hasattr(tool, 'coroutine') and tool.coroutine is not None:
            # 这是一个异步工具，需要包装
            sync_tool = create_sync_tool_wrapper(tool)
            sync_tools.append(sync_tool)
            logger.info(f"转换异步工具: {tool.name} -> 同步工具")
        else:
            # 这已经是同步工具，直接使用
            sync_tools.append(tool)
            logger.info(f"保持同步工具: {tool.name}")
    
    return sync_tools

def get_deepseek_model(temperature=0.3):
    """
    配置并返回 DeepSeek 模型实例
    
    Returns:
        ChatOpenAI: 配置好的 DeepSeek 模型实例
    """
    model = ChatOpenAI(
        model="deepseek-chat",
        api_key="sk-7ce2292c26e546f78aaff58c4bf55fac",
        base_url="https://api.deepseek.com",
        temperature=temperature,
    )
    return model

class OverallState(TypedDict):
    messages: Annotated[list, "LangGraph standard messages"]
    deeplog_node_tool_results: str  #存储工具调用原始结果
    deeplog_analysis_result: str  # 用于存储模型的最终分析结果

def deeplog_node(state: OverallState) ->Command:
    llm = get_deepseek_model(0.5)
 
    logger.info("创建 MCP 客户端...")
    client = MultiServerMCPClient(
        {
            "monitor-service": {
                "url": "http://127.0.0.1:10027/sse",
                "transport": "sse",
            }
        }
    )
    logger.info("获取 MCP 工具...")
    async_tools = asyncio.run(client.get_tools())
    logger.info("转换异步工具为同步工具...")
    sync_tools = convert_async_tools_to_sync(async_tools)
    
    deeplog_agent = create_react_agent(
        llm,
        tools=sync_tools,
    )
 
    result = deeplog_agent.invoke(state)

    logger.info(f"Agent 最终输出: {result['messages'][-1].content}")
    
    # 提取模型的最终回答
    final_analysis = None
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage) and not isinstance(message, ToolMessage):
            final_analysis = message.content
            break
    
    if final_analysis:
        logger.info(f"模型分析结果: {final_analysis}")
    else:
        logger.warning("未找到模型的分析结果")
        final_analysis = "未生成分析结果"
        
    # --- 更健壮地提取原始工具结果 ---
    raw_tool_result = None
    # 从消息历史中倒序查找，确保找到的是最后一次工具调用的结果
    for message in reversed(result["messages"]):
        if isinstance(message, ToolMessage):
            raw_tool_result = message.content
            break  # 找到后立即退出循环
 
    if not raw_tool_result:
        raise ValueError("Agent 没有成功调用任何工具或未找到工具结果。")
    
    return Command(
            update={
                # 原始工具结果字符串存入一个独立的字段
                "deeplog_node_tool_results": raw_tool_result,
                # 模型的最终分析结果也存入state
                "deeplog_analysis_result": final_analysis
            },
            goto="__end__",
        )

# 创建LangGraph工作流
graph = StateGraph(OverallState)
graph.add_node("deeplog", deeplog_node)  
graph.add_edge(START, "deeplog")  
workflow_app = graph.compile()

def parse_simple(returned_string):
    """
    简化的解析方法，假设格式固定为 ["{...}", null]
    """
    # 去除开头的 [" 和结尾的 ", null]
    if returned_string.startswith('["') and returned_string.endswith('", null]'):
        json_string = returned_string[2:-8]  # 去除 [" 和 ", null]
        # 处理转义字符
        json_string = json_string.replace('\\"', '"')
        return json.loads(json_string)
    return None

@app.route('/api/analyze', methods=['POST'])
def analyze_cpu_data():
    """
    CPU数据分析API端点
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': '请求数据格式错误，需要包含query字段'
            }), 400
        
        query = data['query']
        logger.info(f"收到查询请求: {query}")
        
        # 构建初始状态
        initial_state = {
            "messages": [
                HumanMessage(content=query)
            ]
        }
        
        # 执行工作流
        final_state = workflow_app.invoke(initial_state)
        
        # 解析结果
        cpu_data = parse_simple(final_state.get("deeplog_node_tool_results"))
        llm_analysis_result = final_state.get("deeplog_analysis_result")
        
        if not cpu_data:
            return jsonify({
                'success': False,
                'error': '无法解析CPU数据'
            }), 500
        
        # 返回成功结果
        return jsonify({
            'success': True,
            'data': {
                'chart_data': cpu_data,
                'analysis': llm_analysis_result
            }
        })
        
    except Exception as e:
        logger.error(f"处理请求时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器内部错误: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    """
    return jsonify({
        'success': True,
        'message': 'CPU分析服务运行正常'
    })

if __name__ == '__main__':
    logger.info("启动CPU分析Flask服务器...")
    app.run(host='0.0.0.0', port=8000, debug=True)