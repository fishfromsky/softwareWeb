<template>
  <div id="app">
    <navHeader :headerName="headername"></navHeader>
    <router-view/>
  </div>
</template>

<script>
import navHeader from '@/views/NavHeader/index.vue'
export default {
  name: 'App',
  components: {
    navHeader
  },
  data(){
    return{
      headername: '',
    }
  },
  methods: {
    getPlatformName(){
      this.$http({
        url: 'api/getname',
        method: 'get'
      }).then(res=>{
        this.headername = res.data.name
      })
    }
  },
  created(){
    this.getPlatformName()
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body{
  margin: 0px;
  background-color: rgb(240, 242, 245);
}

</style>
