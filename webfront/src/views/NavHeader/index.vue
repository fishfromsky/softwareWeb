<template>
  <div class="main" :style="dynamicStyle">
    <div class="text-box">
      {{ headerName }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'navheader',
  props: {
    headerName: {
      type: String,
      required: true
    }
  },
  computed: {
    dynamicStyle() {
      const colors = this.$store.state.colors
      if (!colors || colors.length === 0) {
        return {
          backgroundColor: '#40c9c6'
        }
      }
      return {
        backgroundColor: colors[0]
      }
    }
  },
  mounted() {
    window.myColors = this.$store.state.colors
    window.userName = this.$store.state.username
    console.log('已将 colors 挂载到 window.myColors:', window.myColors)
  },
}
</script>

<style scoped>
.main {
  width: 100%;
  height: 8vh;
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
}
.text-box {
  font-size: 3vh;
  font-weight: bolder;
  color: #fff;
  margin-left: 20px;
}
</style>
