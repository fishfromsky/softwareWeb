<template>
    <el-card v-loading="card_loading" class="main">
        <component v-if="dynamicComp" :is="dynamicComp"/>
    </el-card>
</template>

<script>
import { createComponentFromString } from '@/utils/utils';
export default {
    name: 'register',
    data() {
        return {
            dynamicComp: null,
            card_loading: true,
        }
        
    },
    methods: {
        getPageCode(){
            this.$http({
                url: 'api/getregister',
                method: 'get'
            }).then(res=>{
                var content = res.data.content
                var templateStr = content.replace(/<\/script>/g, '<\\/script>')
                var comp = createComponentFromString(templateStr)
                this.dynamicComp = comp
                this.card_loading = false
                window.dispatchEvent(new Event('data-loaded_0-1'))
            })
        }
    },
    mounted(){
        this.getPageCode()
    }
}
</script>

<style scoped>
.main {
    width: 20%;
    background-color: #fff;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}
</style>
