<template>
  <div class="chart-container" ref="chart" style="width: 100%; height: 400px;"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'EChartLine',
  data() {
    return {
      chartInstance: null
    }
  },
  mounted() {
    this.initChart()
  },
  methods: {
    initChart() {
      this.chartInstance = echarts.init(this.$refs.chart)
      const option = {
        title: {
          text: '折线图示例'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '示例数据',
            type: 'line',
            data: [150, 230, 224, 218, 135, 147, 260],
            smooth: true
          }
        ]
      }
      this.chartInstance.setOption(option)
    }
  }
}
</script>
