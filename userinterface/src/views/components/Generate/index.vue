<template>
  <div class="container">
    <div class="title">欢迎使用软件著作权生成系统</div>
      <el-form :model="form" class="demo-form-inline">
        <el-form-item label="">
          <el-input v-model="form.name" placeholder="请输入您想生成的软著的名称" style="width: 500px;"></el-input>
        </el-form-item>
        <el-form-item label="">
        <el-select v-model="form.language" style="width: 200px;">
          <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.label"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">立即生成</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import Cookies from 'js-cookie'
export default {
  name: 'Generate',
data() {
  return {
    options: [{
      value: '1',
      label: 'Python'
    }, {
      value: '2',
      label: 'Java'
    }, {
      value: '3',
      label: 'C'
    }, {
      value: '4',
      label: 'C++'
    }],
    form: {
      name: '',
      language: ''
    },
    lastClickTime: null // Add lastClickTime to track the last click time
  }
},
methods: {
  onSubmit() {
    const currentTime = new Date().getTime();
    if (this.lastClickTime && (currentTime - this.lastClickTime < 1000)) {
      this.$message.error('请勿频繁点击');
      return;
    }
    this.lastClickTime = currentTime;

    let time = this.getTime()
    if (this.form.language == ''){
      this.$message.error('请输入编程语言')
    }
    else if (this.form.name == ''){
      this.$message.error('请输入软著名称!')
    }
    else{
      this.$http({
        url: 'api/getthreadstatus',
        method: 'get'
      }).then(res=>{
        var status = res.data.status
        if (status == 1){
          var dataForm = {
          'id': Cookies.get('user_id'),
          'username': Cookies.get('username'),
          'platform': this.form.name,
          'language': this.form.language,
          'time': time
          }
          this.$http.post('api/runprogram', dataForm).then(res=>{
            this.$message.success('运行成功, 请耐心等待')
          })
        }
        else{
          this.$message.error('服务器任务已满，请稍后尝试')
        }
      })
    }
  },
    getTime(){
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth() + 1;
      const day = now.getDate();
      const hours = now.getHours();
      const minutes = now.getMinutes();
      const seconds = now.getSeconds();
      const formattedTime = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
                          + ` ${hours.toString().padStart(2, '0')}-${minutes.toString().padStart(2, '0')}-${seconds.toString().padStart(2, '0')}`;
      return formattedTime
    }
  }
};
</script>

<style scoped>
.title{
  font-size: 4vh;
  color: dimgray;
  font-weight: bolder;
}
.container{
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
.demo-form-inline {

}
</style>
