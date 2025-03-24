<template>
  <div class="dashboard-card">
    <el-card shadow="always">
      <div slot="header">
        <span>{{ title }}</span>
      </div>
      <div class="card-content">
        <h2>{{ count }}</h2>
        <p>{{ description }}</p>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'DashboardCard',
  props: {
    title: {
      type: String,
      default: ''
    },
    count: {
      type: Number,
      default: 0
    },
    description: {
      type: String,
      default: ''
    }
  }
}
</script>
