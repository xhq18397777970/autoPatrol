<template>
  <div id="app">
    <div class="cpu-analyzer-container">
      <h1>
        <el-icon><TrendCharts /></el-icon>
        CPU数据分析系统
      </h1>
      <CpuAnalyzer />
    </div>
  </div>
</template>

<script setup>
import { TrendCharts } from '@element-plus/icons-vue'
import CpuAnalyzer from './components/CpuAnalyzer.vue'
</script>

<style scoped>
h1 {
  color: #409eff;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 2rem;
  font-weight: bold;
}

.el-icon {
  font-size: 2rem;
}
</style>