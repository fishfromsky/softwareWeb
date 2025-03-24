<template>
  <div className="line-chart" ref="lineChart" style="width: 100%; height: 300px;">
    <!-- 这是折线图的容器 -->
  </div>
</template>

<script>
export default {
  name: 'LineChart',
  data() {
    return {
      chartInstance: null
    }
  },
  mounted() {
    // 假设 echarts 已全局引入
    this.chartInstance = echarts.init(this.$refs.lineChart)
    const option = {
      title: {text: '折线图'},
      tooltip: {trigger: 'axis'},
      xAxis: {
        type: 'category',
        data: [] // 这里自行添加真实横坐标
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          type: 'line',
          data: [] // 这里自行添加真实纵坐标数据
        }
      ]
    }
    this.chartInstance.setOption(option)
  }
}
</script>

<style scoped>
.line-chart {
  padding: 16px;
}
</style>
