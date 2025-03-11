<template>
  <el-container style="height: 100vh;">
    <el-header class="header">
      <div class="header-text">软件著作权生成系统</div>
      <div class="username">
        <div class="text">欢迎你, {{ username }}</div>
        <div class="divider"></div>
        <div class="logout" @click="logout">退出登录</div>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" style="background-color: #D3DCE6;">
        <el-menu :default-active="active_index.toString()" style="height: 100%;">
          <el-menu-item v-for="(item, idx) in itemList" :index="item.index" :key="idx" @click="handleClick(idx, item.path)">
            <i :class="item.icon"></i>
            <span slot="title">{{ item.name }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import Cookies from 'js-cookie'
export default {
  name: 'HomeView',
  components: {
    
  },
  data(){
    return{
      username: '',
      active_index: localStorage.getItem('active_index') || '0',
      itemList: [
        {name: '软著生成', index: '0', icon: 'el-icon-s-order', path: '/generate'},
        {name: '项目管理', index: '1', icon: 'el-icon-menu', path: '/manage'},
        {name: '个人信息', index: '2', icon: 'el-icon-s-custom', path: 'person'}
      ]
    }
  },
  methods: {
    clearActiveIndex() {
      localStorage.removeItem('active_index');
    },
    handleClick(idx, pagepath){
      if (this.active_index != idx){
        this.$router.push({path: pagepath})
        this.active_index = idx
        localStorage.setItem('active_index', idx)
      }
    },
    logout(){
      Cookies.remove('username')
      Cookies.remove('user_id')
      localStorage.removeItem('active_index')
      window.location.reload()
    }
  },
  mounted() {
    this.username = Cookies.get('username')
    window.addEventListener('beforeunload', this.clearActiveIndex);
  },
  beforeDestroy() {
    window.removeEventListener('beforeunload', this.clearActiveIndex);
  }
}
</script>
<style>
.header{
  background-color: #0074e5; 
  color: white; 
  font-weight: bolder;
  text-align: left;
  line-height: 60px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.username{
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
}
.divider{
  width: 1px;
  height: 20px;
  background-color: #fff;
  margin-left: 20px;
}
.logout{
  margin-left: 20px;
  cursor: pointer;
}
.logout:hover{
  transform: scale(1.05);
}
.header-text{
  margin-left: 40px;
  font-size: 2vh;
}

.el-aside {
  background-color: #D3DCE6;
  color: #333;
  text-align: center;
  line-height: 200px;
}

.el-main {
  background-color: #E9EEF3;
  color: #333;
  text-align: center;
  line-height: 160px;
}

body > .el-container {
  margin-bottom: 40px;
}

.el-container:nth-child(5) .el-aside,
.el-container:nth-child(6) .el-aside {
  line-height: 260px;
}

.el-container:nth-child(7) .el-aside {
  line-height: 320px;
}
</style>
