<template>
  <div class="cpu-analyzer">
    <!-- 对话框容器 -->
    <div class="dialog-container">
      <!-- 标题 -->
      <div class="dialog-title">
        <el-icon><TrendCharts /></el-icon>
        应用、集群、主机维度指标查询
      </div>

      <!-- 预备阶段：输入区域 -->
      <div v-if="!hasResults && !loading" class="input-section">
        <div class="input-wrapper">
          <el-input
            v-model="query"
            type="textarea"
            :rows="3"
            placeholder="发送待查询的集群、时间段、指标"
            :disabled="loading"
            @keyup.ctrl.enter="handleAnalyze"
            class="query-input"
          />
          <el-button
            type="primary"
            @click="handleAnalyze"
            :loading="loading"
            :disabled="!query.trim()"
            class="send-button"
            :icon="TrendCharts"
            circle
          />
        </div>
        <div class="input-tip">
          💡 提示：支持自然语言查询，按 Ctrl+Enter 快速提交
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <el-icon class="loading-icon"><Loading /></el-icon>
        <div class="loading-text">正在分析CPU数据，请稍候...</div>
      </div>

      <!-- 结果展示阶段 -->
      <div v-if="hasResults" class="results-section">
        <!-- 用户原始问题 -->
        <div class="user-question">
          <div class="question-label">您的查询：</div>
          <div class="question-content">{{ userQuestion }}</div>
        </div>

        <!-- 图表展示 -->
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataLine /></el-icon>
              <span>CPU指标图表</span>
              <el-button
                v-if="chartData"
                @click="refreshChart"
                :icon="Refresh"
                circle
                size="small"
                style="margin-left: auto;"
              />
            </div>
          </template>
          
          <div
            ref="chartContainer"
            class="chart-container"
            v-loading="loading"
            element-loading-text="正在生成图表..."
          ></div>
        </el-card>

        <!-- 分析结果 -->
        <el-card class="analysis-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Document /></el-icon>
              <span>AI分析结果</span>
            </div>
          </template>
          
          <div class="analysis-result">
            <pre v-if="analysisResult">{{ analysisResult }}</pre>
            <el-empty v-else description="暂无分析结果" />
          </div>
        </el-card>

        <!-- 重新查询按钮 -->
        <div class="new-query-section">
          <el-button @click="resetQuery" type="primary" plain>
            <el-icon><Search /></el-icon>
            新查询
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, TrendCharts, DataLine, Document, Refresh, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { cpuApi } from '../utils/api.js'

// 响应式数据
const query = ref('')
const userQuestion = ref('')
const loading = ref(false)
const chartData = ref(null)
const analysisResult = ref('')
const chartContainer = ref(null)
const chartInstance = ref(null)

// 计算属性
const hasResults = ref(false)

// 生命周期
onMounted(() => {
  // 组件挂载后初始化图表容器
  initChart()
})

// 方法
const initChart = () => {
  if (chartContainer.value) {
    chartInstance.value = echarts.init(chartContainer.value)
    
    // 监听窗口大小变化
    window.addEventListener('resize', () => {
      if (chartInstance.value) {
        chartInstance.value.resize()
      }
    })
  }
}

const handleAnalyze = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  // 保存用户问题
  userQuestion.value = query.value
  loading.value = true
  
  try {
    ElMessage.info('正在分析CPU数据，请稍候...')
    
    const result = await cpuApi.analyzeCpuData(query.value)
    
    if (result.success) {
      console.log('API返回的完整数据:', result)
      console.log('chartData:', result.chartData)
      console.log('analysis:', result.analysis)
      
      chartData.value = result.chartData
      analysisResult.value = result.analysis
      hasResults.value = true
      
      // 等待DOM更新后渲染图表
      await nextTick()
      
      // 确保图表容器存在且有尺寸
      if (chartContainer.value) {
        console.log('图表容器尺寸:', {
          width: chartContainer.value.offsetWidth,
          height: chartContainer.value.offsetHeight
        })
        
        // 重新初始化图表实例（如果需要）
        if (!chartInstance.value) {
          console.log('重新初始化图表实例')
          initChart()
        }
        
        // 调整图表尺寸
        if (chartInstance.value) {
          chartInstance.value.resize()
        }
      }
      
      renderChart(result.chartData)
      
      ElMessage.success('分析完成！')
    }
  } catch (error) {
    console.error('分析失败:', error)
    ElMessage.error('分析失败，请检查网络连接或稍后重试')
  } finally {
    loading.value = false
  }
}

const resetQuery = () => {
  query.value = ''
  userQuestion.value = ''
  hasResults.value = false
  chartData.value = null
  analysisResult.value = ''
  if (chartInstance.value) {
    chartInstance.value.clear()
  }
}

const renderChart = (apiData) => {
  if (!chartInstance.value || !apiData) {
    console.error('图表实例或数据不存在:', { chartInstance: chartInstance.value, apiData })
    return
  }

  // 调试日志
  console.log('渲染图表数据:', apiData)

  // 兼容不同的数据结构
  const data = apiData.data || apiData
  if (!data) {
    console.error('数据结构错误:', apiData)
    return
  }

  const { title, x_data, legend_data, series_data, unit } = data

  // 转换数据格式为ECharts需要的格式
  const chartDataFormatted = x_data.map((time, index) => {
    const item = { time }
    series_data.forEach(series => {
      item[series.name] = series.value[index]
    })
    return item
  })

  // 创建series配置
  const series = legend_data.map(name => ({
    name: name,
    type: 'line',
    showSymbol: false,
    lineStyle: {
      width: 3
    },
    endLabel: {
      show: true,
      formatter: function(params) {
        return params.seriesName
      }
    },
    labelLayout: {
      moveOverlap: 'shiftY'
    },
    emphasis: {
      focus: 'series'
    },
    encode: {
      x: 'time',
      y: name,
      tooltip: name
    }
  }))

  const option = {
    animationDuration: 1000,
    title: {
      text: title,
      top: 10,
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      order: 'valueDesc',
      trigger: 'axis',
      confine: true,
      backgroundColor: 'rgba(50, 50, 50, 0.9)',
      borderColor: 'rgba(50, 50, 50, 0.9)',
      textStyle: {
        color: '#fff'
      },
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        },
        label: {
          backgroundColor: '#283b56'
        }
      },
      extraCssText: 'min-width: 180px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);',
      padding: [10, 12],
      formatter: function(params) {
        let result = params[0].axisValue.substring(11, 19) + '<br/>'
        params.forEach(param => {
          result += param.marker + param.seriesName + ': ' + param.value[param.seriesName] + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: legend_data,
      top: 40,
      icon: 'roundRect',
      itemGap: 25,
      textStyle: {
        fontSize: 12,
        fontWeight: 'bold'
      }
    },
    xAxis: {
      type: 'category',
      name: '时间',
      nameLocation: 'middle',
      nameGap: 30,
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#A9A9A9'
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        color: '#666',
        fontWeight: 'bold',
        formatter: function(value) {
          return value.substring(11, 19)
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#f0f0f0',
          type: 'dashed'
        }
      }
    },
    yAxis: {
      name: `单位 (${unit})`,
      nameGap: 50,
      nameLocation: 'middle',
      type: 'value',
      axisLine: {
        show: true,
        lineStyle: {
          color: '#A9A9A9'
        }
      }
    },
    grid: {
      right: 140,
      left: 80,
      top: 100,
      bottom: 60
    },
    dataset: {
      source: chartDataFormatted
    },
    series: series
  }

  chartInstance.value.setOption(option, true)
}

const refreshChart = () => {
  if (chartData.value) {
    renderChart(chartData.value)
    ElMessage.success('图表已刷新')
  }
}

// 组件卸载时清理
const cleanup = () => {
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
  window.removeEventListener('resize', () => {})
}

// 监听组件卸载
import { onUnmounted } from 'vue'
onUnmounted(cleanup)
</script>

<style scoped>
.cpu-analyzer {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.dialog-container {
  width: 100%;
  max-width: 900px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  min-height: 400px;
}

.dialog-title {
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.dialog-title .el-icon {
  font-size: 1.8rem;
}

/* 预备阶段样式 */
.input-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.input-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px;
}

.query-input {
  width: 100%;
}

.query-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 2px solid #e4e7ed;
  padding: 16px 60px 16px 16px;
  font-size: 14px;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.query-input :deep(.el-textarea__inner):focus {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.send-button {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 10;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #409eff;
  border: none;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.send-button:hover {
  background: #66b1ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.4);
}

.input-tip {
  font-size: 12px;
  color: #909399;
  text-align: center;
}

/* 加载状态样式 */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem 0;
}

.loading-icon {
  font-size: 2rem;
  color: #409eff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #666;
}

/* 结果展示样式 */
.results-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.user-question {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1rem;
  border-left: 4px solid #409eff;
}

.question-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 0.5rem;
}

.question-content {
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.5;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  color: #409eff;
}

.chart-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.chart-container {
  width: 100%;
  height: 400px;
  min-height: 400px;
}

.analysis-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.analysis-result {
  max-height: 300px;
  overflow-y: auto;
}

.analysis-result pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Fira Mono', 'Roboto Mono', monospace;
  line-height: 1.6;
  color: #2c3e50;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  margin: 0;
}

.new-query-section {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cpu-analyzer {
    padding: 1rem;
  }
  
  .dialog-container {
    padding: 1.5rem;
    border-radius: 16px;
  }
  
  .dialog-title {
    font-size: 1.2rem;
  }
  
  .chart-container {
    height: 300px;
    min-height: 300px;
  }
}

@media (max-width: 480px) {
  .dialog-container {
    padding: 1rem;
  }
  
  .input-wrapper {
    max-width: 100%;
  }
}
</style>