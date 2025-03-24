<template>
  <div class="search-box">
    <!-- 使用 Element UI 的 Form + Select + Input 等组合 -->
    <el-form :inline="true" :model="formData" label-width="80px">
      <!-- 下拉筛选1 -->
      <el-form-item label="选项A">
        <el-select v-model="formData.selectA" placeholder="请选择" clearable>
          <el-option label="选项A1" value="A1" />
          <el-option label="选项A2" value="A2" />
        </el-select>
      </el-form-item>

      <!-- 下拉筛选2 -->
      <el-form-item label="选项B">
        <el-select v-model="formData.selectB" placeholder="请选择" clearable>
          <el-option label="选项B1" value="B1" />
          <el-option label="选项B2" value="B2" />
        </el-select>
      </el-form-item>

      <!-- 下拉筛选3 -->
      <el-form-item label="选项C">
        <el-select v-model="formData.selectC" placeholder="请选择" clearable>
          <el-option label="选项C1" value="C1" />
          <el-option label="选项C2" value="C2" />
        </el-select>
      </el-form-item>

      <!-- 下拉筛选4 -->
      <el-form-item label="选项D">
        <el-select v-model="formData.selectD" placeholder="请选择" clearable>
          <el-option label="选项D1" value="D1" />
          <el-option label="选项D2" value="D2" />
        </el-select>
      </el-form-item>

      <!-- 输入框筛选（可选） -->
      <el-form-item label="关键词">
        <el-input
          v-model="formData.keyword"
          placeholder="请输入关键词"
          clearable
          @keyup.enter="onSearch"
        />
      </el-form-item>

      <!-- 操作按钮 -->
      <el-form-item>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="onReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'SearchBox',
  data() {
    return {
      // 用于存储各个筛选项的值
      formData: {
        selectA: '',
        selectB: '',
        selectC: '',
        selectD: '',
        keyword: ''
      }
    }
  },
  methods: {
    onSearch() {
      // 查询逻辑：此处仅 console.log，实际可调用接口或做路由跳转等
      console.log('查询参数：', this.formData)
    },
    onReset() {
      // 重置表单
      this.formData.selectA = ''
      this.formData.selectB = ''
      this.formData.selectC = ''
      this.formData.selectD = ''
      this.formData.keyword = ''
    }
  }
}
</script>

<style scoped>
.search-box {
  padding: 16px;
}

/* 根据需要自定义样式，如控制行间距、列间距等 */
</style>
