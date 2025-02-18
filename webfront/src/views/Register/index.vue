<template>
    <div class="main">
        <h2>用户注册</h2>
        <el-form :model="form" :rules="rules" ref="registerForm" label-width="80px" class="demo-loginForm">
            <el-form-item label="姓名" prop="name">
                <el-input v-model="form.name"></el-input>
            </el-form-item>
            <el-form-item label="年龄" prop="age">
                <el-input v-model.number="form.age"></el-input>
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
                <el-input v-model="form.phone" style="width: calc(100% - 100px); margin-right: 10px;"></el-input>
                <el-button type="primary">获取验证码</el-button>
            </el-form-item>
            <el-form-item label="验证码" prop="verificationCode">
                <el-input v-model="form.verificationCode"></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
                <el-input type="password" v-model="form.password"></el-input>
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
                <el-input type="password" v-model="form.confirmPassword"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitForm('registerForm')">确认登录</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
export default {
    name: 'register',
    data() {
        const validatePass = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请输入密码'));
            } else if (value !== this.form.password) {
                callback(new Error('两次输入密码不一致'));
            } else {
                callback();
            }
        };

        const validatePhone = (rule, value, callback) => {
            const phoneRegex = /^[0-9]{10}$/;
            if (value === '') {
                callback(new Error('请输入手机号'));
            } else if (!phoneRegex.test(value)) {
                callback(new Error('手机号格式不正确'));
            } else {
                callback();
            }
        };

        return {
            form: {
                name: '',
                age: null,
                phone: '',
                verificationCode: '',
                password: '',
                confirmPassword: ''
            },
            rules: {
                name: [
                    { required: true, message: '请输入姓名', trigger: 'blur' }
                ],
                age: [
                    { required: true, message: '请输入年龄', trigger: 'blur' },
                    { type: 'number', message: '年龄必须为数字', trigger: 'blur' }
                ],
                phone: [
                    { required: true, validator: validatePhone, trigger: 'blur' }
                ],
                verificationCode: [
                    { required: true, message: '请输入验证码', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' }
                ],
                confirmPassword: [
                    { required: true, validator: validatePass, trigger: 'blur' }
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
                    console.log('验证失败!');
                    return false;
                }
            });
        }
    }
}
</script>

<style scoped>
.main {
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
