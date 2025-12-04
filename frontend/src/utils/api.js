import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000, // 30秒超时，因为AI分析可能需要较长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    
    // 检查业务状态码
    if (data.success === false) {
      ElMessage.error(data.error || '请求失败')
      return Promise.reject(new Error(data.error || '请求失败'))
    }
    
    return data
  },
  error => {
    console.error('响应错误:', error)
    
    let errorMessage = '网络错误'
    
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response
      switch (status) {
        case 400:
          errorMessage = data.error || '请求参数错误'
          break
        case 500:
          errorMessage = data.error || '服务器内部错误'
          break
        case 502:
          errorMessage = '网关错误，请检查后端服务是否启动'
          break
        case 503:
          errorMessage = '服务暂时不可用'
          break
        default:
          errorMessage = `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '无法连接到服务器，请检查网络连接'
    }
    
    ElMessage.error(errorMessage)
    return Promise.reject(error)
  }
)

// API方法
export const cpuApi = {
  /**
   * 分析CPU数据
   * @param {string} query - 用户查询语句
   * @returns {Promise} 返回分析结果
   */
  async analyzeCpuData(query) {
    try {
      const response = await api.post('/analyze', {
        query: query.trim()
      })
      
      return {
        success: true,
        chartData: response.data.chart_data,
        analysis: response.data.analysis
      }
    } catch (error) {
      console.error('CPU数据分析失败:', error)
      throw error
    }
  },

  /**
   * 健康检查
   * @returns {Promise} 返回服务状态
   */
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response
    } catch (error) {
      console.error('健康检查失败:', error)
      throw error
    }
  }
}

export default api