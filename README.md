# CPU数据分析系统

一个基于Vue3 + Flask的CPU数据分析系统，支持自然语言查询CPU指标数据，并通过ECharts图表和AI分析结果进行可视化展示。

## 系统架构

### 后端 (Flask + LangGraph)
- **Flask API服务器**: 提供RESTful API接口
- **LangGraph工作流**: 集成DeepSeek AI模型进行数据分析
- **MCP客户端**: 连接监控服务获取CPU数据
- **数据解析**: 将原始数据转换为ECharts格式

### 前端 (Vue3 + Element Plus)
- **Vue3 Composition API**: 现代化的响应式框架
- **Element Plus**: 企业级UI组件库
- **ECharts**: 专业的数据可视化图表库
- **Axios**: HTTP客户端进行API调用

## 功能特性

### 🔍 自然语言查询
- 支持中文自然语言输入
- 智能解析时间范围和集群信息
- 示例：`查询集群lf-lan-ha1在时间范围2025-12-04 14:00:00到2025-12-04 14:10:10的CPU指标数据`

### 📊 数据可视化
- 交互式时序图表展示
- 多指标对比分析
- 响应式图表设计
- 支持图表缩放和数据点悬停

### 🤖 AI智能分析
- 基于DeepSeek模型的专业分析
- 异常检测和趋势分析
- 性能建议和运维洞察
- 结构化分析报告

### 💡 用户体验
- 现代化界面设计
- 加载状态和错误处理
- 移动端适配
- 快捷键支持 (Ctrl+Enter)

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 后端启动

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 启动Flask服务器：
```bash
python app.py
```

服务器将在 `http://localhost:5000` 启动

### 前端启动

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

前端将在 `http://localhost:3000` 启动

## API接口

### POST /api/analyze
分析CPU数据

**请求体：**
```json
{
  "query": "查询集群lf-lan-ha1在时间范围2025-12-04 14:00:00到2025-12-04 14:10:10的CPU指标数据"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "chart_data": {
      "data": {
        "title": "CPU指标图表",
        "x_data": ["2025-12-04 14:00:00", "..."],
        "legend_data": ["cpu_usage", "cpu_load"],
        "series_data": [...],
        "unit": "%"
      }
    },
    "analysis": "AI分析结果文本..."
  }
}
```

### GET /api/health
健康检查

**响应：**
```json
{
  "success": true,
  "message": "CPU分析服务运行正常"
}
```

## 项目结构

```
├── app.py                      # Flask应用入口
├── main.py                     # 原始LangGraph实现
├── requirements.txt            # Python依赖
├── echart.js                  # ECharts配置参考
├── README.md                  # 项目说明
└── frontend/                  # 前端项目
    ├── package.json           # 项目配置
    ├── vite.config.js         # Vite配置
    ├── index.html             # 入口HTML
    └── src/
        ├── main.js            # 应用入口
        ├── App.vue            # 主应用组件
        ├── style.css          # 全局样式
        ├── components/
        │   └── CpuAnalyzer.vue # CPU分析组件
        └── utils/
            └── api.js         # API调用封装
```

## 技术栈

### 后端技术
- **Flask 2.3.3**: Web框架
- **LangGraph**: AI工作流编排
- **LangChain**: AI应用开发框架
- **DeepSeek API**: 大语言模型
- **MCP客户端**: 模型上下文协议

### 前端技术
- **Vue 3.3.4**: 渐进式JavaScript框架
- **Element Plus 2.4.1**: Vue3组件库
- **ECharts 5.4.3**: 数据可视化
- **Axios 1.5.0**: HTTP客户端
- **Vite 4.4.5**: 构建工具

## 开发说明

### 代码规范
- 后端遵循PEP 8 Python代码规范
- 前端使用ESLint + Prettier格式化
- 组件采用Composition API写法
- 使用TypeScript类型注解（可选）

### 错误处理
- 统一的API错误响应格式
- 前端全局错误拦截和提示
- 网络超时和重试机制
- 用户友好的错误信息

### 性能优化
- 图表懒加载和按需渲染
- API请求防抖和缓存
- 组件级别的代码分割
- 响应式图表自适应

## 部署指南

### 生产环境部署

1. **后端部署**：
   - 使用Gunicorn作为WSGI服务器
   - 配置Nginx反向代理
   - 设置环境变量和日志

2. **前端部署**：
   - 执行 `npm run build` 构建生产版本
   - 将dist目录部署到Web服务器
   - 配置路由和静态资源

### Docker部署（可选）

```dockerfile
# 后端Dockerfile示例
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 故障排除

### 常见问题

1. **后端服务无法启动**
   - 检查Python版本和依赖安装
   - 确认MCP服务是否运行在端口10027
   - 验证DeepSeek API密钥配置

2. **前端无法连接后端**
   - 检查Vite代理配置
   - 确认后端服务运行状态
   - 查看浏览器网络请求日志

3. **图表显示异常**
   - 检查数据格式是否正确
   - 确认ECharts容器尺寸
   - 查看浏览器控制台错误

## 贡献指南

1. Fork项目到个人仓库
2. 创建功能分支 `git checkout -b feature/新功能`
3. 提交更改 `git commit -m '添加新功能'`
4. 推送分支 `git push origin feature/新功能`
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue到GitHub仓库
- 发送邮件到项目维护者
- 参与项目讨论区交流

---

**注意**: 本系统需要配置有效的DeepSeek API密钥和MCP监控服务才能正常运行。请确保相关服务已正确配置并运行。