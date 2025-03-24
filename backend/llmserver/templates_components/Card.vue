<template>
  <div class="card-layout">
    <el-row :gutter="16">
      <!-- 示例：一行放四张卡片，可自行复制/删除 -->
      <el-col span="6">
        <el-card shadow="hover" class="card-item">
          <div class="card-content">
            <h3>卡片标题1</h3>
            <p>卡片数据1</p>
          </div>
          <el-button type="primary" size="small">
            操作
          </el-button>
        </el-card>
      </el-col>

      <el-col span="6">
        <el-card shadow="hover" class="card-item">
          <div class="card-content">
            <h3>卡片标题2</h3>
            <p>卡片数据2</p>
          </div>
          <el-button type="primary" size="small">
            操作
          </el-button>
        </el-card>
      </el-col>

      <el-col span="6">
        <el-card shadow="hover" class="card-item">
          <div class="card-content">
            <h3>卡片标题3</h3>
            <p>卡片数据3</p>
          </div>
          <el-button type="primary" size="small">
            操作
          </el-button>
        </el-card>
      </el-col>

      <el-col span="6">
        <el-card shadow="hover" class="card-item">
          <div class="card-content">
            <h3>卡片标题4</h3>
            <p>卡片数据4</p>
          </div>
          <el-button type="primary" size="small">
            操作
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'CardLayout',
  data() {
    return {}
  },
  methods: {}
}
</script>

<style scoped>
.card-layout {
  padding: 16px;
}
.card-item {
  margin-bottom: 16px;
}
.card-content {
  margin-bottom: 12px;
}
</style>
