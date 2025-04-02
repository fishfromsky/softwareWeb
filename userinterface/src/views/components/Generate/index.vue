<template>
  <div class="container">
    <div class="title">欢迎使用软件著作权生成系统</div>

    <el-form :model="form" class="demo-form-inline">

      <el-row type="flex" justify="center" align="middle">
        <el-col>
          <el-form-item label="">
            <el-input
              v-model="form.name"
              placeholder="请输入您想生成的软著的名称"
              style="width: 500px;"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row type="flex" justify="center" align="middle">
        <el-col>
          <el-form-item label="">
            <el-select
              v-model="form.language"
              style="width: 200px;"
              placeholder="请选择编程语言"
            >
              <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
                :value="item.label"
              />
            </el-select>
          </el-form-item>
        </el-col>

        <el-col>
          <el-form-item label="">
            <el-select
              v-model="form.color"
              style="width: 200px;"
              placeholder="请选择颜色"
              :popper-class="'color-dropdown-popper'"
            >
              <el-option
                v-for="(item, index) in colorOptions"
                :key="index"
                :label="item.label"
                :value="item.colors"
              >
                <div class="color-option">
                  <span
                    class="color-circle"
                    :style="{ backgroundColor: item.representColor }"
                  ></span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row type="flex" justify="center" align="middle">
        <el-col>
          <el-form-item>
            <el-button type="primary" @click="onSubmit">立即生成</el-button>
          </el-form-item>
        </el-col>
      </el-row>

    </el-form>
  </div>
</template>

<script>
import Cookies from 'js-cookie'
export default {
  name: 'Generate',
  data() {
    return {
      options: [
        { value: '1', label: 'Python' },
        { value: '2', label: 'Java' },
        { value: '3', label: 'php' },

      ],
      colorOptions: [
  {
    label: '红色系',
    representColor: '#FF4444',
    colors: ['#F44336', '#FF4444', '#FF6666', '#FFA8A8']
  },
  {
    label: '蓝色系',
    representColor: '#3F51B5',
    colors: ['#3F51B5', '#2196F3', '#03A9F4', '#00BCD4']
  },
  {
    label: '绿色系',
    representColor: '#4CAF50',
    colors: ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B']
  },
  {
    label: '橙色系',
    representColor: '#FFC107',
    colors: ['#795548', '#FF5722', '#FF9800', '#FFC107']
  },
  {
    label: '灰色系',
    representColor: '#607D8B',
    colors: ['#607D8B', '#9E9E9E', '#BDBDBD', '#E0E0E0']
  },
  {
    label: '紫色系',
    representColor: '#9C27B0',
    colors: ['#6A1B9A', '#7B1FA2', '#8E24AA', '#9C27B0']
  },
  {
    label: '粉色系',
    representColor: '#E91E63',
    colors: ['#E91E63', '#F06292', '#F48FB1', '#F8BBD0']
  },
{
  label: '棕色系',
  representColor: '#795548',
  colors: ['#4E342E', '#5D4037', '#6D4C41', '#8D6E63']
}
  {
    label: '靛青系',
    representColor: '#009688',
    colors: ['#009688', '#26A69A', '#80CBC4', '#B2DFDB']
  },
  {
    label: '黑白系',
    representColor: '#000000',
    colors: ['#000000', '#444444', '#888888', '#FFFFFF']
  }
],
      form: {
        name: '',
        language: '',
        color: ''
      },
      lastClickTime: null
    }
  },
  methods: {
  onSubmit() {
  const currentTime = new Date().getTime();
  if (this.lastClickTime && (currentTime - this.lastClickTime < 1000)) {
    this.$message.error('请勿频繁点击');
    return;
  }
  this.lastClickTime = currentTime;

  let time = this.getTime();
  if (this.form.language === '') {
    this.$message.error('请输入编程语言');
  } else if (this.form.name === '') {
    this.$message.error('请输入软著名称!');
  } else if (!this.form.color || this.form.color.length === 0) {
    // 如果 this.form.color 是数组，就判断长度是否为 0
    this.$message.error('请选择颜色!');
  } else {
    // 检查服务器线程状态
    this.$http({
      url: 'api/getthreadstatus',
      method: 'get'
    }).then(res => {
      const status = res.data.status;
      if (status === 1) {
        const dataForm = {
              'id': Cookies.get('user_id'),
              'username': Cookies.get('username'),
              'platform': this.form.name,
              'language': this.form.language,
              'color': this.form.color,
              'time': time
        };

        this.$http.post('api/runprogram', dataForm).then(res => {
          this.$message.success('运行成功, 请耐心等待');
        });
      } else {
        this.$message.error('服务器任务已满，请稍后尝试');
      }
    });
  }
},

    getTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth() + 1;
      const day = now.getDate();
      const hours = now.getHours();
      const minutes = now.getMinutes();
      const seconds = now.getSeconds();
      const formattedTime = `${year}-${String(month).padStart(2, '0')}-${String(
        day
      ).padStart(2, '0')} ${String(hours).padStart(2, '0')}-${String(
        minutes
      ).padStart(2, '0')}-${String(seconds).padStart(2, '0')}`;
      return formattedTime;
    }
  }
};
</script>

<style>
.title {
  font-size: 4vh;
  color: dimgray;
  font-weight: bolder;
}
.container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.color-dropdown-popper .el-select-dropdown {
  width: 330px !important;
}

.color-dropdown-popper .el-select-dropdown__list {
  display: grid;
  grid-template-columns: repeat(5, 40px);
  gap: 8px;
  padding: 8px 20px;
  box-sizing: border-box;
}

.color-dropdown-popper .el-select-dropdown__item {
  line-height: normal !important;
  padding: 4px 8px !important;
  min-height: auto !important;
}

.color-dropdown-popper .el-select-dropdown__item:hover,
.color-dropdown-popper .el-select-dropdown__item.is-selected {
  background-color: transparent !important;
}


.color-option {
  display: flex;
  align-items: center;
}
.color-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 4px;
}
</style>
