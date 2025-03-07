<template>
  <el-menu
    default-active="1-1"
    class="sidebar"
    :unique-opened="true"
    background-color="#304156"
    text-color="#fff"
    id="menu"
    @select="handleSelect"
  >
    <el-submenu v-for="(name, index) in Object.keys(itemList)" class="parent-menu" :key="index" :index="String(index+1)" style="width: 100%">
      <template slot="title">{{ name }}</template>
      <el-menu-item v-for="(subname, idx) in itemList[name]" :key="idx" :index="String(index+1)+'-'+String(idx+1)">
        {{ subname }}
      </el-menu-item>
    </el-submenu>
  </el-menu>
</template>

<script>
export default {
  data(){
    return{

    }
  },
  props: {
    itemList: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleSelect(index, indexPath){
      this.$emit('menu', index)
    }
  }
}
</script>

<style scoped>
.sidebar {
  height: calc(100vh - 8vh);
  width: 100%;
  position: relative;
  margin-top: 0;
}
</style>
