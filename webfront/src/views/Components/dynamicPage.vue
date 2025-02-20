<template>
  <div>
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="设备ID">
        <el-input v-model="searchForm.deviceId" placeholder="请输入设备ID"></el-input>
      </el-form-item>
      <el-form-item label="设备状态">
        <el-select v-model="searchForm.status" placeholder="请选择设备状态">
          <el-option label="在线" value="online"></el-option>
          <el-option label="离线" value="offline"></el-option>
          <el-option label="维修中" value="maintenance"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="deviceList" style="width: 100%">
      <el-table-column prop="deviceId" label="设备ID"></el-table-column>
      <el-table-column prop="status" label="设备状态"></el-table-column>
      <el-table-column prop="location" label="位置"></el-table-column>
      <el-table-column prop="batteryLevel" label="电池电量"></el-table-column>
      <el-table-column label="操作">
        <template slot-scope="scope">
          <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div id="chart-container" style="display: flex; justify-content: space-between;">
      <div id="chart1" style="width: 48%; height: 400px;"></div>
      <div id="chart2" style="width: 48%; height: 400px;"></div>
    </div>
  </div>
</template>

<script>
import echarts from 'echarts'

export default {
  data() {
    return {
      searchForm: {
        deviceId: '',
        status: ''
      },
      deviceList: [
        { deviceId: 'D001', status: '在线', location: 'A区', batteryLevel: '80%' },
        { deviceId: 'D002', status: '在线', location: 'B区', batteryLevel: '90%' },
        { deviceId: 'D003', status: '离线', location: 'C区', batteryLevel: '20%' },
        { deviceId: 'D004', status: '维修中', location: 'D区', batteryLevel: '50%' },
        { deviceId: 'D005', status: '在线', location: 'E区', batteryLevel: '70%' }
      ]
    };
  },
  mounted() {
    this.initCharts();
  },
  methods: {
    onSearch() {
      // 查询逻辑
    },
    resetForm() {
      this.searchForm = {
        deviceId: '',
        status: ''
      };
    },
    handleEdit(index, row) {
      // 编辑逻辑
    },
    handleDelete(index, row) {
      // 删除逻辑
    },
    initCharts() {
      const chart1 = echarts.init(document.getElementById('chart1'));
      const chart2 = echarts.init(document.getElementById('chart2'));

      const option1 = {
        title: {
          text: '设备在线情况'
        },
        tooltip: {},
        xAxis: {
          data: ["在线", "离线", "维修中"]
        },
        yAxis: {},
        series: [{
          name: '数量',
          type: 'bar',
          data: [5, 2, 1]
        }]
      };

      const option2 = {
        title: {
          text: '设备电池电量分布'
        },
        tooltip: {},
        xAxis: {
          data: ["0%-20%", "20%-40%", "40%-60%", "60%-80%", "80%-100%"]
        },
        yAxis: {},
        series: [{
          name: '数量',
          type: 'bar',
          data: [1, 1, 2, 1, 1]
        }]
      };

      chart1.setOption(option1);
      chart2.setOption(option2);
    }
  }
};
</script>