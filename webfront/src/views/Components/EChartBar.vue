<template>
  <div class="chart-container" ref="chart" style="width: 100%; height: 400px;"></div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'EChartBar',
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
          text: '柱状图示例'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['A', 'B', 'C', 'D', 'E']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '数量',
            type: 'bar',
            data: [12, 20, 15, 8, 25],
            itemStyle: {
              color: '#40c9c6'
            }
          }
        ]
      }
      this.chartInstance.setOption(option)
    }
  }
}
</script>
