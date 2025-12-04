<template>
  <div class="cpu-analyzer">
    <!-- 查询输入区域 -->
    <el-card class="query-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Search /></el-icon>
          <span>CPU数据查询</span>
        </div>
      </template>
      
      <el-form @submit.prevent="handleAnalyze">
        <el-form-item>
          <el-input
            v-model="query"
            type="textarea"
            :rows="3"
            placeholder="请输入您的查询，例如：查询集群lf-lan-ha1在时间范围2025-12-04 14:00:00到2025-12-04 14:10:10的CPU指标数据"
            :disabled="loading"
            @keyup.ctrl.enter="handleAnalyze"
          />
          <div class="input-tip">
            💡 提示：支持自然语言查询，按 Ctrl+Enter 快速提交
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleAnalyze"
            :loading="loading"
            :disabled="!query.trim()"
            size="large"
            style="width: 100%;"
          >
            <el-icon v-if="!loading"><TrendCharts /></el-icon>
            {{ loading ? '分析中...' : '开始分析' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果展示区域 -->
    <div v-if="hasResults" class="results-section">
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
    </div>

    <!-- 空状态 -->
    <el-empty 
      v-if="!hasResults && !loading" 
      description="请输入查询条件开始分析"
      :image-size="200"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, TrendCharts, DataLine, Document, Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { cpuApi } from '../utils/api.js'

// 响应式数据
const query = ref('')
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
  max-width: 1200px;
  margin: 0 auto;
}

.query-card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: bold;
  color: #409eff;
}

.input-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.results-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.chart-card {
  margin-bottom: 1rem;
}

.chart-container {
  width: 100%;
  height: 400px;
  min-height: 400px;
}

.analysis-card {
  margin-bottom: 1rem;
}

.analysis-result {
  max-height: 400px;
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
}

@media (max-width: 768px) {
  .cpu-analyzer {
    padding: 0 1rem;
  }
  
  .chart-container {
    height: 300px;
    min-height: 300px;
  }
}
</style>