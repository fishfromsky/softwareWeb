<template>
  <div>
    <el-card class="box-card">
      <el-table :data="[userInfo]" style="width: 100%">
        <el-table-column prop="username" label="用户名"></el-table-column>
        <el-table-column prop="password" label="密码"></el-table-column>
        <el-table-column prop="phone_number" label="手机号"></el-table-column>
        <el-table-column prop="email" label="邮箱"></el-table-column>
      </el-table>
      <div style="text-align: right; margin-top: 20px;">
        <el-button type="primary" @click="editUser">编辑</el-button>
      </div>
    </el-card>

    <!-- Edit Dialog -->
    <el-dialog title="编辑个人信息" :visible.sync="dialogVisible" width="40%">
      <el-form :model="editedUserInfo" :rules="rules" ref="editForm" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editedUserInfo.username"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="editedUserInfo.password" type="password"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone_number">
          <el-input v-model="editedUserInfo.phone_number"></el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editedUserInfo.email"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="resetForm">重置</el-button>
        <el-button type="primary" @click="submitForm">提交</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import Cookies from 'js-cookie'

export default {
  name: 'person',
  data() {
    return {
      userInfo: {},
      dialogVisible: false,
      editedUserInfo: {},
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ],
        phone_number: [
          { required: true, message: '请输入手机号', trigger: 'blur' },
          { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      }
    };
  },
  methods: {
    editUser() {
      this.editedUserInfo = { ...this.userInfo };
      this.dialogVisible = true;
    },
    submitForm() {
      this.$refs.editForm.validate((valid) => {
        if (valid) {
          if (JSON.stringify(this.editedUserInfo) === JSON.stringify(this.userInfo)) {
            this.$message.warning('您未做任何修改');
            return false;
          }
          this.$http.post('api/edituserinfo', this.editedUserInfo).then(res=>{
            this.$message.success('修改信息成功')
            this.getUserInfo()
          })
          this.dialogVisible = false;
        } else {
          this.$message.error('请输入正确格式信息');
          return false;
        }
      });
    },
    resetForm() {
      this.$refs.editForm.resetFields();
      this.editedUserInfo = { ...this.userInfo };
    },
    getUserInfo() {
      var user_id = Cookies.get('user_id')
      var param = {
        'user_id': user_id
      }
      this.$http({
        url: 'api/getuserinfo',
        method: 'get',
        params: param
      }).then(res => {
        this.userInfo = res.data.data
      })
    }
  },
  mounted() {
    this.getUserInfo()
  }
};
</script>

<style scoped>
.box-card {
  width: 100%;
}
.el-table {
  margin-top: 20px;
}
.el-row {
  padding: 20px;
}
.el-col {
  padding: 10px;
}
</style>
