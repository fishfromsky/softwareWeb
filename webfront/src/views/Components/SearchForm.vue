<template>
  <div class="search-form">
    <el-form :inline="true" :model="searchForm" label-width="80px">
      <el-form-item label="关键词">
        <el-input
          v-model="searchForm.keyword"
          placeholder="请输入关键字"
          clearable
        ></el-input>
      </el-form-item>

      <el-form-item label="类型">
        <el-select v-model="searchForm.type" placeholder="请选择类型" clearable>
          <el-option label="类型一" value="type1" />
          <el-option label="类型二" value="type2" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'SearchForm',
  data() {
    return {
      searchForm: {
        keyword: '',
        type: ''
      }
    }
  },
  methods: {
    handleSearch() {
      // 触发搜索逻辑
      console.log('搜索表单:', this.searchForm)
      // 也可以通过 emit 通知父组件
      // this.$emit('on-search', { ...this.searchForm })
    },
    resetForm() {
      this.searchForm = {
        keyword: '',
        type: ''
      }
    }
  }
}
</script>
