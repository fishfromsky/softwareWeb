<template>
    <div class="main-body">
        <el-card class="box" v-loading="card_loading">
            <component v-if="dynamicComp" :is="dynamicComp" @mounted="handleMounted"/>
             <!-- <Dynamic></Dynamic> -->
        </el-card>
    </div>
</template>

<script>
import Vue from 'vue/dist/vue.esm';
import Dynamic from '@/views/Components/dynamicPage.vue'
function extractOuterTemplateContent(sfcString, open, close) {
    /// 通过嵌套统计提取最外层template中间的内容
	const openTag = open;
	const closeTag = close;
	const startIndex = sfcString.indexOf(openTag);
	if (startIndex === -1) return '';
	const startTagEnd = sfcString.indexOf('>', startIndex);
	if (startTagEnd === -1) return '';

	let level = 1;
	let currentIndex = startTagEnd + 1;
	let endIndex = -1;

	while (level > 0 && currentIndex < sfcString.length) {
		const nextOpen = sfcString.indexOf(openTag, currentIndex);
		const nextClose = sfcString.indexOf(closeTag, currentIndex);

		if (nextClose === -1) break;

		if (nextOpen !== -1 && nextOpen < nextClose) {
		level++;
		currentIndex = nextOpen + openTag.length;
		} else {
		level--;
		currentIndex = nextClose + closeTag.length;
		if (level === 0) {
			endIndex = nextClose;
		}
		}
	}

	if (endIndex !== -1) {
		return sfcString.substring(startTagEnd + 1, endIndex).trim();
	}

	return '';
}
function parseSFC(sfcString) {
	const templateMatch = extractOuterTemplateContent(sfcString, '<template', '</template>')
	const scriptMatch = extractOuterTemplateContent(sfcString, '<script', '<\\/script>')

	const templateCode = templateMatch
	const scriptCode = scriptMatch

	return { templateCode, scriptCode }
}
function transformScript(scriptCode) {
  	return scriptCode.replace(/export\s+default/, 'return')
}
function createComponentFromString(sfcString) {
	const { templateCode, scriptCode } = parseSFC(sfcString)
	const transformCode = transformScript(scriptCode)

	const { render, staticRenderFns } = Vue.compile(templateCode)

  	const scriptObj = eval(`
        (function(){
            ${transformCode}
        })()
    `)
  	scriptObj.render = render
  	scriptObj.staticRenderFns = staticRenderFns

  	return scriptObj
}

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
        handleMounted(){
            console.log('动态组件已经渲染完毕')
        }
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