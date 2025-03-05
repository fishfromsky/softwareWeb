<template>
  <div class="login-container">
    <div class="title">软件著作权自动化生成系统</div>
    <el-card class="box-card">
      <div slot="header" class="clearfix">
        <span>用户登录</span>
      </div>
      <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="100px" class="demo-loginForm">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input type="password" v-model="loginForm.password" autocomplete="off" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm('loginForm')">登录</el-button>
          <el-button @click="resetForm('loginForm')">重置</el-button>
        </el-form-item>
        <el-form-item>
          <div style="text-align: center;">
            <span>没有账户？</span>
            <el-button type="text" @click="goToRegister">立即注册</el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import Cookies from 'js-cookie'
export default {
  name: 'login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
          if (valid) {
          this.$http.post('api/login', this.loginForm).then(res=>{
            let data = res.data.code
            if (data == 1){
              this.$message.error('该用户名尚未注册')
            }
            else if (data == 2){
              this.$message.error('密码错误')
            }
            else{
              let data = res.data.data
              Cookies.set('username', data.username)
              Cookies.set('user_id', data.id)
              this.$message.success('登录成功')
              this.$router.push('/')
            }
        }).catch(e=>{
          this.$message.error(e)
        })
        } else {
          console.log('error submit!!');
          return false;
        }
      });
    },
    resetForm(formName) {
      this.$refs[formName].resetFields();
    },
    goToRegister() {
      this.$router.push('/register')
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #4C5A89
}
.title{
  color: #fff;
  font-weight: bolder;
  font-size: 4vh;
  margin-bottom: 60px;
}
.box-card {
  width: 480px;
  background-color: #ffffff; /* White background for card */
  border-radius: 8px; /* Rounded corners */
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); /* Subtle shadow */
}
</style>
