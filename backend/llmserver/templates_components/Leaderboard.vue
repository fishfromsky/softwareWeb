<template>
  <div class="leaderboard">
    <el-card shadow="hover">
      <!-- 示例：两条排行榜数据，可自行复制/删除 -->
      <el-row class="leaderboard-item">
        <el-col :span="4">
          <strong>1</strong>
        </el-col>
        <el-col :span="10">
          <span>用户A</span>
        </el-col>
        <el-col :span="6">
          <span>1000</span>
        </el-col>
        <el-col :span="4" class="text-right">
          <el-button size="mini">
            查看详情
          </el-button>
        </el-col>
      </el-row>

      <el-row class="leaderboard-item">
        <el-col :span="4">
          <strong>2</strong>
        </el-col>
        <el-col :span="10">
          <span>用户B</span>
        </el-col>
        <el-col :span="6">
          <span>800</span>
        </el-col>
        <el-col :span="4" class="text-right">
          <el-button size="mini">
            查看详情
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'Leaderboard',
  data() {
    return {}
  }
}
</script>

<style scoped>
.leaderboard-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.leaderboard-item:last-child {
  border-bottom: none;
}
</style>
