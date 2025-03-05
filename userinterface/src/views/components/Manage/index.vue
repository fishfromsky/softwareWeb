<template>
    <div>
        <el-table :data="tableData" style="width: 100%">
            <el-table-column prop="name" label="软著名称" ></el-table-column>
            <el-table-column prop="time" label="创建时间"></el-table-column>
            <el-table-column prop="language" label="后端代码语言"></el-table-column>
            <el-table-column label="说明文档下载">
                <template slot-scope="scope">
                    <el-button v-if="scope.row.introduce_status" @click="handleDownload(scope.row.introduce_download)" type="primary" size="mini">下载</el-button>
                    <div v-else>正在生成中</div>
                </template>
            </el-table-column>
            <el-table-column label="操作手册下载">
                <template slot-scope="scope">
                    <el-button v-if="scope.row.pdf_status" @click="handleDownload(scope.row.pdf_download)" type="primary" size="mini">下载</el-button>
                    <div v-else>正在生成中</div>
                </template>
            </el-table-column>
            <el-table-column label="代码文档下载">
                <template slot-scope="scope">
                    <el-button v-if="scope.row.code_status" @click="handleDownload(scope.row.code_download)" type="primary" size="mini">下载</el-button>
                    <div v-else>正在生成中</div>
                </template>
            </el-table-column>
            <el-table-column label="操作">
                <template slot-scope="scope">
                    <el-button  @click="handleDelete(scope.$index, scope.row)" type="danger" size="mini">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script>
import Cookies from 'js-cookie'
import { MessageBox } from 'element-ui'

export default {
    name: 'manage',
    data() {
        return {
            tableData: [
               
            ]
        };
    },
    methods: {
        handleDownload(url) {
            window.open(url, '_blank');
        },
        handleEdit(index, row) {
            console.log('Edit:', index, row);
        },
        handleDelete(index, row) {
            MessageBox.confirm('此操作将永久删除该记录, 是否继续?', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                var record_id = row.id
                var params = {
                    'record_id': record_id
                }
                this.$http({
                    url: 'api/deleterecord',
                    method: 'get',
                    params: params
                }).then(res=>{
                    this.$message.success('删除记录成功')
                    this.getMetadata()
                })
            }).catch(() => {
                this.$message({
                    type: 'info',
                    message: '已取消删除'
                });          
            });
        },
        getMetadata(){
            var userId = Cookies.get('user_id')
            var params = {
                'user_id': userId
            }
            this.$http({
                url: 'api/getuserrecord',
                method: 'get',
                params: params
            }).then(res=>{
                console.log(res.data.data)
                this.tableData = res.data.data
            })
        }
    },
    mounted(){
        this.getMetadata()
    }
};
</script>

<style scoped>
</style>
