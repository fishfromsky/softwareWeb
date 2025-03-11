<template>
    <div class="main-body">
        <el-card class="box" v-loading="card_loading">
            <component v-if="dynamicComp" :is="dynamicComp"/>
             <!-- <Dynamic></Dynamic> -->
        </el-card>
    </div>
</template>

<script>
import Dynamic from '@/views/Components/dynamicPage.vue'
import { createComponentFromString } from '@/utils/utils.js'
export default{
    name: 'Info',
    components: {
        Dynamic
    },
    props: {
        card_loading: {
            type: Boolean,
            required: true
        },
        pagecode: {
            type: String,
            required: true
        }
    },
    data(){
        return{
            dynamicComp: null
        }
    },
    methods: {
       
    },
    watch: {
        pagecode(val){
            var templateStr = val 
            var comp = createComponentFromString(templateStr)
            this.dynamicComp = comp
        }
    },
    mounted(){
        
    }
}
</script>

<style scoped>
.main-body{
    box-sizing: border-box;
    padding: 40px;
}
.box{
    width: 100%;
    min-height: 30vh;
    box-sizing: border-box;
    padding: 20px;
}
</style>