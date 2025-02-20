import Vue from 'vue/dist/vue.esm';

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
    // 动态编译Vue代码
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

export { createComponentFromString }