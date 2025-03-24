<template>
   
        <component v-if="dynamicComp" :is="dynamicComp"/>
   
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
            var params = {
                'username': this.$store.state.username,
                'datetime': this.$store.state.datetime
            }
            this.$http({
                url: 'api/getpagevice',
                method: 'get',
                params: params
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

