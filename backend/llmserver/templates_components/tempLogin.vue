<template>
  <div
    style="
      width: 100%;
      height: 100vh;
      margin: 0;
      padding: 0;
      background: url('http://127.0.0.1:8000/static/LYA/2025-03-23 18-10-25/background.jpg') no-repeat center center;
      background-size: cover;
      display: flex;
      align-items: center;
      justify-content: flex-end;
    "
  >
    <!-- 右侧登录卡片 -->
    <div
      style="
        width: 360px;
        margin-right: 80px;
        background: #ffffff;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        padding: 40px;
        display: flex;
        flex-direction: column;
      "
    >
      <h2
        style="
          text-align: center;
          margin-bottom: 30px;
          font-size: 24px;
        "
      >
      </h2>
      <el-form @submit.native.prevent="onSubmit">
        <!-- 用户名 -->
        <el-form-item>
          <el-input
            v-model="form.username"
            prefix-icon="el-icon-user"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <!-- 密码 -->
        <el-form-item>
          <el-input
            v-model="form.password"
            prefix-icon="el-icon-lock"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <!-- 登录按钮：用动态样式模拟 hover 效果 -->
        <el-form-item>
          <el-button
            type="primary"
            :style="loginButtonStyle"
            @mouseover="isHovered = true"
            @mouseleave="isHovered = false"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: "Login",
  data() {
    return {
      form: {
        username: "",
        password: ""
      },
      isHovered: false
    };
  },
  computed: {
    loginButtonStyle() {
      if (this.isHovered) {
        return {
          width: '100%',
          height: '45px',
          border: 'none',
          outline: 'none',
          borderRadius: '6px',
          fontSize: '16px',
          color: '#ffffff',
          cursor: 'pointer',
          background: 'linear-gradient(to right, #66b1ff, #409eff)',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
          transform: 'translateY(-1px)',
          transition: 'all 0.3s ease'
        };
      } else {
        return {
          width: '100%',
          height: '45px',
          border: 'none',
          outline: 'none',
          borderRadius: '6px',
          fontSize: '16px',
          color: '#ffffff',
          cursor: 'pointer',
          background: 'linear-gradient(to right, #409eff, #66b1ff)',
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
          transition: 'all 0.3s ease'
        };
      }
    }
  },
  methods: {
    onSubmit() {
      alert(`用户名：${this.form.username}\n密码：${this.form.password}`);
    }
  }
};
</script>
