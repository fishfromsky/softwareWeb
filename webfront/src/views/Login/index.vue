<template>
  <div class="login">
    <h2>用户登录</h2>
    <el-form :model="loginForm" :rules="rules" ref="loginForm" label-width="100px" class="demo-loginForm">
      <el-form-item label="姓名" prop="name">
        <el-input v-model="loginForm.name"></el-input>
      </el-form-item>
      <el-form-item label="年龄" prop="age">
        <el-input v-model.number="loginForm.age"></el-input>
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="loginForm.phone"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input type="password" v-model="loginForm.password" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input type="password" v-model="loginForm.confirmPassword" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('loginForm')">确认登录</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        name: '',
        age: '',
        phone: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        age: [
          { required: true, message: '请输入年龄', trigger: 'change' },
          { type: 'number', message: '年龄必须为数字值', trigger: 'blur' }
        ],
        phone: [
          { required: true, message: '请输入手机号', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: this.validatePass, trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          alert('提交成功!');
        } else {
          console.log('错误提交!!');
          return false;
        }
      });
    },
    validatePass(rule, value, callback) {
      if (value === '') {
        callback(new Error('请再次输入密码'));
      } else if (value !== this.loginForm.password) {
        callback(new Error('两次输入密码不一致!'));
      } else {
        callback();
      }
    }
  }
}
</script>

<style scoped>
.login {
  width: 30%;
  min-height: 50vh;
  background-color: #fff;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 0.5vh;
  box-shadow: 0 0 5px 5px rgba(83, 83, 83, 0.1);
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>
