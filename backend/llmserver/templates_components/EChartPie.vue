<template>
  <div class="pie-chart" ref="pieChart" style="width: 100%; height: 300px;">
    <!-- 这是饼状图的容器 -->
  </div>
</template>

<script>
export default {
  name: 'PieChart',
  data() {
    return {
      chartInstance: null
    }
  },
  mounted() {
    this.chartInstance = echarts.init(this.$refs.pieChart)
    const option = {
      title: { text: '饼状图' },
      tooltip: { trigger: 'item' },
      legend: { orient: 'horizontal', bottom: 0 },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: [] // 自行添加 { name: '', value: '' } 数组
        }
      ]
    }
    this.chartInstance.setOption(option)
  }
}
</script>

<style scoped>
.pie-chart {
  padding: 16px;
}
</style>
