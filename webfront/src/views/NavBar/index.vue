<template>
  <el-menu
    class="sidebar"
    :unique-opened="true"
    :background-color="computedBackground"
    :text-color="computedTextColor"
    :style="{
      '--active-text-color': computedActiveTextColor,
      '--active-bg-color': computedActiveBgColor
    }"
    id="menu"
    @select="handleSelect"
  >
    <el-submenu
      v-for="(name, index) in Object.keys(itemList)"
      class="parent-menu"
      :key="index"
      :index="String(index + 1)"
      style="width: 100%"
    >
      <template slot="title">{{ name }}</template>
      <el-menu-item
        v-for="(subname, idx) in itemList[name]"
        :key="idx"
        :index="String(index + 1) + '-' + String(idx + 1)"
      >
        {{ subname }}
      </el-menu-item>
    </el-submenu>
  </el-menu>
</template>

<script>
export default {
  name: 'SidebarMenu',
  props: {
    itemList: {
      type: Object,
      required: true
    }
  },
  computed: {
    computedBackground() {
      return '#fff'
    },
    computedTextColor() {
      return '#000'
    },
    computedActiveTextColor() {
      const colors = this.$store.state.colors
      return colors && colors.length >= 1 ? colors[0] : '#409EFF'
    },
    computedActiveBgColor() {
      const colors = this.$store.state.colors
      return colors && colors.length >= 4 ? colors[3] : '#fff'
    }
  },
  mounted() {
    window.myColors = this.$store.state.colors
    window.userName = this.$store.state.username
    console.log('已将 colors 挂载到 window.myColors:', window.myColors)
  },
  methods: {
    handleSelect(index) {
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

/* 当前选中的子菜单，背景色和文字颜色 */
::v-deep .el-menu-item.is-active {
  background-color: var(--active-bg-color) !important;
  color: var(--active-text-color) !important;
}

/* 父菜单选中状态，高亮标题 */
::v-deep .el-submenu.is-active > .el-submenu__title {
  color: var(--active-text-color) !important;
}

</style>
