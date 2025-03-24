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
    <!-- 右侧注册卡片 -->
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
      <!-- 标题 -->
      <h2
        style="
          text-align: center;
          margin-bottom: 30px;
          font-size: 24px;
          font-weight: bold;
        "
      >
        欢迎注册
      </h2>

      <!-- 注册表单 -->
      <form @submit.prevent="onRegister" style="display: flex; flex-direction: column; justify-content: space-around;">
        <!-- 用户名 -->
        <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <label
              for="username"
              style="
                width: 80px;
                text-align: right;
                margin-right: 10px;
                font-weight: 600;
                margin-bottom: 0;
              "
            >
              用户名
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              style="
                flex: 1;
                height: 38px;
                padding: 0 10px;
                box-sizing: border-box;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 14px;
              "
            />
          </div>
          <small style="color: #999;">请填写正确的用户名</small>
        </div>

        <!-- 密码 -->
        <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <label
              for="password"
              style="
                width: 80px;
                text-align: right;
                margin-right: 10px;
                font-weight: 600;
                margin-bottom: 0;
              "
            >
              密码
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              style="
                flex: 1;
                height: 38px;
                padding: 0 10px;
                box-sizing: border-box;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 14px;
              "
            />
          </div>
          <small style="color: #999;">请填写6位以上密码</small>
        </div>

        <!-- 确认密码 -->
        <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <label
              for="confirmPassword"
              style="
                width: 80px;
                text-align: right;
                margin-right: 10px;
                font-weight: 600;
                margin-bottom: 0;
              "
            >
              确认
            </label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              placeholder="再次输入密码"
              style="
                flex: 1;
                height: 38px;
                padding: 0 10px;
                box-sizing: border-box;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 14px;
              "
            />
          </div>
          <small style="color: #999;">请再次输入密码</small>
        </div>

        <!-- 邮箱 -->
        <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <label
              for="email"
              style="
                width: 80px;
                text-align: right;
                margin-right: 10px;
                font-weight: 600;
                margin-bottom: 0;
              "
            >
              邮箱
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱"
              style="
                flex: 1;
                height: 38px;
                padding: 0 10px;
                box-sizing: border-box;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 14px;
              "
            />
          </div>
          <small style="color: #999;">例如：example@mail.com</small>
        </div>

        <!-- 电话号码 -->
        <div style="display: flex; flex-direction: column; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <label
              for="phone"
              style="
                width: 80px;
                text-align: right;
                margin-right: 10px;
                font-weight: 600;
                margin-bottom: 0;
              "
            >
              电话
            </label>
            <input
              id="phone"
              v-model="form.phone"
              type="text"
              placeholder="请输入电话号码"
              style="
                flex: 1;
                height: 38px;
                padding: 0 10px;
                box-sizing: border-box;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 14px;
              "
            />
          </div>
          <small style="color: #999;">请填写正确的电话号码</small>
        </div>

        <!-- 注册按钮 -->
        <div style="display: flex; flex-direction: column; justify-content: center; margin-top: 10px;">
          <el-button
            type="primary"
            style="
              width: 100%;
              background: #409EFF;
            "
            @click="onRegister"
          >
            注册
          </el-button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "Register",
  data() {
    return {
      form: {
        username: "",
        password: "",
        confirmPassword: "",
        email: "",
        phone: ""
      }
    };
  },
  methods: {
    onRegister() {
      alert(
        `用户名：${this.form.username}\n` +
        `密码：${this.form.password}\n` +
        `确认密码：${this.form.confirmPassword}\n` +
        `邮箱：${this.form.email}\n` +
        `电话：${this.form.phone}`
      );
    }
  }
};
</script>
