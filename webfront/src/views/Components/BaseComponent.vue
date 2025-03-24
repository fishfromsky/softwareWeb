<template>
  <div class="base-component">
    <el-input v-model="inputValue" placeholder="请输入内容"></el-input>
    <el-button type="primary" @click="handleSubmit">提交</el-button>
  </div>
</template>

<script>
export default {
  name: 'BaseComponent',
  data() {
    return {
      inputValue: ''
    }
  },
  methods: {
    handleSubmit() {
      // 这里写提交逻辑
      console.log('输入内容:', this.inputValue)
    }
  }
}
</script>
