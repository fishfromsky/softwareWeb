<template>
  <div className="bar-chart" ref="barChart" style="width: 100%; height: 300px;">
    <!-- 这是柱状图的容器 -->
  </div>
</template>

<script>
export default {
  name: 'BarChart',
  data() {
    return {
      chartInstance: null
    }
  },
  mounted() {
    this.chartInstance = echarts.init(this.$refs.barChart)
    const option = {
      title: {text: '柱状图'},
      tooltip: {trigger: 'axis'},
      xAxis: {
        type: 'category',
        data: [] // 自行添加
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          type: 'bar',
          data: [] // 自行添加
        }
      ]
    }
    this.chartInstance.setOption(option)
  }
}
</script>

<style scoped>
.bar-chart {
  padding: 16px;
}
</style>
