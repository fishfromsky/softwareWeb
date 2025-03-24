<template>
  <div class="table-with-pagination">
    <el-table :data="tableData" border style="width: 100%;">
      <!-- 根据 columns 动态生成列（示例保留空数组，可自行添加列） -->
      <el-table-column
        v-for="(col, idx) in columns"
        :key="idx"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
      />

      <!-- 固定操作列示例 -->
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="mini" type="primary">
            操作
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrap">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @size-change="onSizeChange"
        @current-change="onPageChange"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'TableWithPagination',
  data() {
    return {
      columns: [],     // 可自行添加 [{ prop: 'name', label: '姓名', width: '120' }, ...]
      tableData: [],   // 可自行添加 [{ name: '张三', ...}, ...]
      total: 0,
      pageSize: 10,
      currentPage: 1
    }
  },
  methods: {
    onSizeChange(newSize) {
      this.pageSize = newSize
    },
    onPageChange(newPage) {
      this.currentPage = newPage
    }
  }
}
</script>

<style scoped>
.table-with-pagination {
  padding: 16px;
}
.pagination-wrap {
  margin-top: 16px;
  text-align: right;
}
</style>
