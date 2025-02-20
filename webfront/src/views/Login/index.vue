<template>
  <el-card class="login" v-loading="card_loading">
    <component v-if="dynamicComp" :is="dynamicComp"/>
  </el-card>
</template>

<script>
import { createComponentFromString } from '@/utils/utils';
export default {
  name: 'Login',
  data() {
    return {
      dynamicComp: null,
      card_loading: true,
    }
  },
  methods: {
    getPageCode(){
      this.$http({
        url: 'api/getlogin',
        method: 'get'
      }).then(res=>{
          var content = res.data.content
          var templateStr = content.replace(/<\/script>/g, '<\\/script>')
          var comp = createComponentFromString(templateStr)
          this.dynamicComp = comp
          this.card_loading = false
          window.dispatchEvent(new Event('data-loaded_0-0'))
      })
    }
  },
  mounted(){
    this.getPageCode()
  }
}
</script>

<style scoped>
.login {
  width: 20%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
</style>
