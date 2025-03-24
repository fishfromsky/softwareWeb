<template>
  <div class="home">
    <NavBar class="navBar" v-loading="loading" :itemList="itemList" @menu="handleMenuChange"></NavBar>
    <Info class="info" :card_loading="card_loading" :pagecode="page_code"></Info>
  </div>
</template>

<script>
import NavBar from '@/views/NavBar/index.vue'
import Info from '@/views/Info/index.vue'
import * as echarts from 'echarts';
export default {
  name: 'HomeView',
  components: {
    NavBar,
    Info
  },
  data(){
    return{
      current_index: '',
      itemList: {},
      page_code: '',
      loading: true,
      card_loading: true,
      env: {}
    }
  },
  methods: {
    handleMenuChange(index) {
  if (index !== this.current_index) {
    this.current_index = index
    this.card_loading = true

    let colorStr = ''
    if (this.$store.state.colors && this.$store.state.colors.length > 0) {
      colorStr = this.$store.state.colors.join(',')
    }

    this.$http({
      url: 'api/getpageinfo',
      method: 'get',
      params: {
        index: index,
        username: this.$store.state.username,
        datetime: this.$store.state.datetime,
        colors: colorStr ,
      }
    }).then(res => {
      const content = res.data.content
      const replacedString = content.replace(/<\/script>/g, '<\\/script>')
      this.page_code = replacedString
      this.card_loading = false
      window.dispatchEvent(new Event('data-loaded_' + index))
    })
  }
},
    getMenu(){
      var params = {
        'username': this.$store.state.username,
        'datetime': this.$store.state.datetime
      }
      this.$http({
        url: 'api/getmenu',
        method: 'get',
        params: params
      }).then(res=>{
        this.index = '1-1'
        this.itemList = res.data.menu
        this.loading = false
        this.handleMenuChange('1-1')
      })
    }
  },
  mounted(){
    this.getMenu()
  }
}
</script>

<style scoped>
.home{
  display: flex;
  flex-direction: row;
}
.navBar{
  width: 200px;
}
.info{
  flex: 1;
}
</style>
