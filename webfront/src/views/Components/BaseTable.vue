<template>
  <div class="base-table">
    <el-table
      :data="tableData"
      border
      :header-cell-style="headerStyle"
      style="width: 100%"
    >
      <el-table-column prop="date" label="日期"></el-table-column>
      <el-table-column prop="name" label="名称"></el-table-column>
      <el-table-column prop="address" label="地址"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button type="text" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button type="text" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  name: 'BaseTable',
  data() {
    return {
      // 模拟表格数据
      tableData: [
        {
          date: '2023-01-01',
          name: '王小虎',
          address: '上海市普陀区金沙江路 1518 弄'
        },
        {
          date: '2023-01-02',
          name: '李小龙',
          address: '北京市朝阳区幸福街道'
        },
        {
          date: '2023-01-03',
          name: '赵铁柱',
          address: '广州市天河区员村'
        },
        {
          date: '2023-01-04',
          name: 'Lucy',
          address: '深圳市南山区科技园'
        },
        {
          date: '2023-01-05',
          name: 'Tom',
          address: '杭州市西湖区文三路'
        }
      ]
    }
  },
  methods: {
    // 设置表头底色
    headerStyle() {
      return {
        background: '#40c9c6', // 示例颜色
        color: '#fff'
      }
    },
    handleEdit(row) {
      console.log('编辑操作:', row)
    },
    handleDelete(row) {
      console.log('删除操作:', row)
    }
  }
}
</script>
