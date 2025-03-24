<template>

    <component v-if="dynamicComp" :is="dynamicComp"/>
 
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
      // 构建 colors 字符串
      let colorStr = ''
      if (this.$store.state.colors && this.$store.state.colors.length > 0) {
        colorStr = this.$store.state.colors.join(',')
      }

      var params = {
        'username': this.$store.state.username,
        'datetime': this.$store.state.datetime,
        'colors': colorStr  // 添加 colors 参数
      }
      this.$http({
        url: 'api/getpagemain',
        method: 'get',
        params: params
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

