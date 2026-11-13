<template>
  <main class="evaluation">
    <div class="page-inner">
      <header class="page-header">
        <div><div class="eyebrow">QUALITY WORKSPACE <span>RAGAS</span></div><h1>知识库评测</h1><p>把真实问答变成评测样本，持续了解知识库的回答质量。</p></div>
        <div class="header-actions"><t-button theme="default" variant="outline" :disabled="!rows.length || busy" @click="download"><template #icon><t-icon name="download" /></template>导出报告</t-button><t-button :disabled="!rows.length || !judgeModelId || busy" :loading="busy" @click="run"><template #icon><t-icon name="play" /></template>{{ busy ? '评测中' : '开始评测' }}</t-button></div>
      </header>
      <div class="judge-settings"><div><strong>评判模型</strong><span>复用问答模型的 API 配置，无需重复填写密钥</span></div><t-select v-model="judgeModelId" :disabled="busy" placeholder="选择已配置的问答模型" style="width:300px;max-width:100%"><t-option v-for="model in judgeModels" :key="model.id" :value="model.id" :label="model.display_name || model.name" /></t-select><router-link to="/platform/settings?section=models">管理模型</router-link></div>
      <section class="stats-grid">
        <div class="stat-card"><span>评测样本</span><div>{{ rows.length }}<small>条问答</small></div><p>从对话导入或上传文件</p></div>
        <div class="stat-card"><span>已完成</span><div>{{ rows.filter(r => r.result).length }}<small>/ {{ rows.length }}</small></div><p>逐题评分，保留失败详情</p></div>
        <div class="stat-card"><span>上下文覆盖</span><div>{{ rows.filter(r => r.retrieved_contexts.length).length }}<small>条有上下文</small></div><p>缺少上下文的样本无法评分</p></div>
        <div class="stat-card"><span>参考答案</span><div>{{ rows.filter(r => r.reference?.trim()).length }}<small>条已补充</small></div><p>用于评估上下文召回率</p></div>
      </section>
      <section class="workspace">
        <div class="workspace-tabs"><button :class="{ selected: activeTab === 'samples' }" @click="activeTab = 'samples'">评测样本 <span>{{ rows.length }}</span></button><button :class="{ selected: activeTab === 'report' }" @click="activeTab = 'report'">评测报告</button><span class="save-hint"><t-icon name="info-circle" />离开前请导出保存</span></div>
        <template v-if="activeTab === 'samples'">
          <div class="import-bar"><div class="section-heading"><strong>准备评测数据</strong><span>选择历史对话，或导入已有问答</span></div><div class="import-actions"><t-button theme="default" variant="outline" :disabled="busy" @click="loadSessions"><template #icon><t-icon name="chat" /></template>历史对话</t-button><t-button theme="default" variant="outline" :disabled="busy" @click="fileInput?.click()"><template #icon><t-icon name="upload" /></template>导入文件</t-button><input ref="fileInput" hidden type="file" accept=".json,.jsonl" :disabled="busy" @change="importFile"></div></div>
          <div v-if="sessions.length" class="session-picker"><t-select v-model="sessionId" filterable placeholder="搜索并选择最近的对话" :disabled="busy" style="flex:1"><t-option v-for="s in sessions" :key="s.id" :value="s.id" :label="s.title || s.id" /></t-select><t-button :disabled="!sessionId || busy" @click="importSession">导入问答</t-button></div>
          <div v-if="!rows.length" class="empty-state"><div class="empty-icon"><t-icon name="chart-bar" size="32px" /></div><h3>从一组真实问答开始</h3><p>导入对话中的问题、回答与上下文<br>了解回答是否有据可依，检索内容是否有效</p><t-button variant="outline" :disabled="busy" @click="loadSessions">选择历史对话</t-button><span class="format-hint">支持 JSON / JSONL · 无参考答案也可评测</span></div>
          <div v-else class="samples-list"><article v-for="(row, index) in rows" :key="index" class="sample-card"><div class="sample-top"><div><span class="sample-number">{{ String(index + 1).padStart(2, '0') }}</span><strong>问答样本</strong><span class="source-tag">{{ row.context_source?.startsWith('历史') ? '历史对话' : '文件导入' }}</span></div><t-button theme="default" variant="text" size="small" :disabled="busy" @click="rows.splice(index, 1)"><template #icon><t-icon name="delete" /></template>移除</t-button></div><div class="fields"><label>问题<t-textarea v-model="row.user_input" :disabled="busy" :autosize="{ minRows: 2, maxRows: 6 }" @change="invalidate(row)" /></label><label>实际回答<t-textarea v-model="row.response" :disabled="busy" :autosize="{ minRows: 2, maxRows: 8 }" @change="invalidate(row)" /></label></div><label class="reference-field">参考答案 <span>选填 · 补充后可计算召回率</span><t-textarea v-model="row.reference" :disabled="busy" placeholder="填写经过确认的答案或应包含的关键信息" :autosize="{ minRows: 1, maxRows: 5 }" @change="invalidate(row)" /></label><details><summary>查看上下文 <span>{{ row.retrieved_contexts.length }} 段</span></summary><div class="context-note">{{ row.context_source || '请确认上下文完整性' }}</div><pre v-for="(context, n) in row.retrieved_contexts" :key="n">{{ context }}</pre><p v-if="!row.retrieved_contexts.length" class="error">缺少上下文，该样本将跳过评分</p></details><div v-if="row.result" class="result-line">{{ formatResult(row.result) }}</div><div v-if="row.error" class="error">{{ row.error }}</div></article></div>
        </template>
        <div v-else class="report-panel"><template v-if="rows.some(r => r.result || r.error)"><h3>评测结果</h3><div class="summary">{{ summary || '暂无有效分数' }}</div><article v-for="(row, n) in rows" :key="n" class="report-row"><strong>{{ n + 1 }}. {{ row.user_input }}</strong><p :class="{error: row.error}">{{ row.error || (row.result ? formatResult(row.result) : '等待评测') }}</p></article></template><div v-else class="empty-state"><div class="empty-icon"><t-icon name="chart" size="32px" /></div><h3>报告将在评测后生成</h3><p>先准备样本，再点击「开始评测」<br>失败指标会单独记录，不计为零分</p></div></div>
        <div class="workspace-footer"><span><i :class="{ running: busy }" />{{ status }}</span><t-button v-if="busy" size="small" variant="text" @click="stop = true">本题结束后停止</t-button><span v-else>Ragas · 逐题评测</span></div>
      </section>
      <section class="metric-guide"><div><t-icon name="verified" /><strong>回答忠实度</strong><p>回答中的内容是否得到上下文支持</p></div><div><t-icon name="filter" /><strong>上下文精度</strong><p>以回答为依据，衡量上下文相关性与排序</p></div><div><t-icon name="search" /><strong>上下文召回率</strong><p>需要参考答案，判断关键信息是否检索完整</p></div></section>
      <p class="footnote">历史导入使用已保存的引用片段，不代表完整模型输入。多轮问题请补全语义；报告暂存于当前页面。</p>
    </div>
  </main>
</template>
<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { listModels, type ModelConfig } from '@/api/model/index'
import { getMessageList, getSessionsList } from '@/api/chat/index'
import { post } from '@/utils/request'

type Row = { user_input: string; response: string; retrieved_contexts: string[]; reference?: string; context_source?: string; session_id?: string; message_id?: string; result?: any; error?: string }
const judgeModels = ref<ModelConfig[]>([]), judgeModelId = ref('')
onMounted(async () => {
 try { judgeModels.value = (await listModels('KnowledgeQA')).filter(m => m.status === 'active'); judgeModelId.value = judgeModels.value.find(m => m.is_default)?.id || judgeModels.value[0]?.id || '' } catch { status.value = '模型列表读取失败，请刷新重试' }
})
const activeTab = ref('samples'), fileInput = ref<HTMLInputElement | null>(null)
const rows = ref<Row[]>([]), sessions = ref<any[]>([]), sessionId = ref(''), status = ref('尚未开始'), busy = ref(false), stop = ref(false)
const names: Record<string, string> = { faithfulness: '回答忠实度', llm_context_precision_without_reference: '上下文精度（以回答为依据）', context_recall: '上下文召回率' }
const summary = computed(() => {
  const values: Record<string, number[]> = {}
  for (const row of rows.value) for (const [key, value] of Object.entries(row.result?.scores || {})) {
    if (typeof value === 'number' && Number.isFinite(value)) (values[key] ||= []).push(value)
  }
  return Object.entries(values).map(([key, list]) => `${names[key] || key}：${(list.reduce((a,b) => a+b,0)/list.length).toFixed(3)}（${list.length} 个有效样本）`).join(' · ')
})
function invalidate(row: Row) { delete row.result; delete row.error }
async function loadSessions() {
  try { const res: any = await getSessionsList(1, 100); sessions.value = res.data || []; status.value = '显示最近 100 个对话' }
  catch { status.value = '读取对话失败' }
}
async function importSession() {
  busy.value = true
  try {
    const res: any = await getMessageList({ session_id: sessionId.value, limit: 200, created_at: '' })
    const messages: any[] = res.data || []
    const imported: Row[] = []
    for (const m of messages) {
      if (m.role !== 'assistant' || !m.is_completed || !m.content || !m.request_id) continue
      const user = messages.find(u => u.role === 'user' && u.request_id === m.request_id)
      if (!user?.content || rows.value.some(r => r.message_id === m.id && r.session_id === sessionId.value)) continue
      imported.push({ user_input: user.content, response: m.content, retrieved_contexts: Array.from(new Set<string>((m.knowledge_references || []).map((r: any) => r.content).filter((c: any) => typeof c === 'string' && c.trim()))), context_source: '历史引用片段（非完整输入）', session_id: sessionId.value, message_id: m.id })
    }
    rows.value.push(...imported); status.value = `导入 ${imported.length} 条；本次读取最近 200 条消息，仅匹配同一 request_id 的完整问答`
  } catch { status.value = '导入失败' } finally { busy.value = false }
}
async function importFile(event: Event) {
  const input = event.target as HTMLInputElement, file = input.files?.[0]
  if (!file) return
  try {
    if (file.size > 10 * 1024 * 1024) throw Error('文件不能超过 10MB')
    const text = await file.text()
    const data = text.trim().startsWith('[') ? JSON.parse(text) : text.split(/\r?\n/).filter(l => l.trim()).map(l => JSON.parse(l))
    if (!Array.isArray(data) || data.length > 1000) throw Error('最多导入 1000 条样本')
    const imported = data.map((r: any): Row => {
      if (typeof r.user_input !== 'string' || !r.user_input.trim() || typeof r.response !== 'string' || !r.response.trim() || !Array.isArray(r.retrieved_contexts) || !r.retrieved_contexts.every((c: any) => typeof c === 'string') || (r.reference != null && typeof r.reference !== 'string')) throw Error('字段格式错误：需要问题、回答和字符串数组 retrieved_contexts')
      return { user_input: r.user_input, response: r.response, retrieved_contexts: r.retrieved_contexts, reference: r.reference || '', context_source: '文件导入（完整性待确认）' }
    })
    rows.value.push(...imported); status.value = `导入 ${imported.length} 条`
  } catch (e: any) { status.value = e.message || '文件格式错误' } finally { input.value = '' }
}
async function run() {
  if (!judgeModelId.value) { status.value = "请先选择评判模型"; return }
  busy.value = true; stop.value = false
  try {
    for (const [i, row] of rows.value.entries()) {
      if (stop.value) break
      invalidate(row); status.value = `正在评测 ${i + 1} / ${rows.value.length}`
      if (!row.retrieved_contexts.length || !row.user_input.trim() || !row.response.trim()) { row.error = '缺少问题、回答或上下文'; continue }
      try { row.result = await post('/api/v1/evaluation/ragas', { model_id: judgeModelId.value, user_input: row.user_input, response: row.response, retrieved_contexts: row.retrieved_contexts, reference: row.reference || null }, { timeout: 180000 }) }
      catch (e: any) { row.error = e.response?.data?.error || e.response?.data?.detail || e.detail || (typeof e.error === 'string' ? e.error : e.error?.message) || e.message || '评分失败，请稍后重试' }
    }
    status.value = stop.value ? '已停止，请导出保存' : '评测结束，请导出保存'
  } finally { busy.value = false }
}
function formatResult(result: any) {
  const scores = Object.entries(result.scores || {}).map(([key, value]) => `${names[key] || key}：${typeof value === 'number' ? value.toFixed(3) : value}`)
  const errors = Object.entries(result.errors || {}).map(([key, value]) => `${names[key] || key}：${value}`)
  return [...scores, ...errors, `评判模型：${result.judge_model || '未知'} · Ragas ${result.ragas_version || ''}`].join('；')
}
function download() {
  const url = URL.createObjectURL(new Blob([JSON.stringify(rows.value, null, 2)], { type: 'application/json' }))
  const a = document.createElement('a'); a.href = url; a.download = `weknora-evaluation-${Date.now()}.json`; a.click(); URL.revokeObjectURL(url)
}
</script>

<style scoped>
.judge-settings{display:flex;align-items:center;gap:18px;padding:18px 22px;background:var(--td-bg-color-container,#fff);border:1px solid var(--td-component-border,#e8ebee);border-radius:12px;margin-bottom:18px;flex-wrap:wrap}.judge-settings>div:first-child{flex:1;min-width:180px}.judge-settings strong{display:block;font-size:12px;font-weight:500}.judge-settings span{display:block;font-size:11px;color:var(--td-text-color-secondary);margin-top:5px}.judge-settings a{font-size:12px;color:#15986a;text-decoration:none}

.evaluation{height:100%;overflow-y:auto;background:var(--td-bg-color-page,#f7f8fa);color:var(--td-text-color-primary,#20272e)}.page-inner{max-width:1200px;margin:auto;padding:38px 40px 32px}.page-header{display:flex;justify-content:space-between;align-items:center;gap:24px;margin-bottom:28px}.eyebrow{font-size:10px;letter-spacing:1.6px;color:var(--td-text-color-secondary,#7b8590);font-weight:600}.eyebrow span{color:#15986a;background:rgba(21,152,106,.08);border-radius:4px;padding:3px 6px;margin-left:8px;letter-spacing:1px}h1{font-size:26px;letter-spacing:-.6px;margin:10px 0 8px;font-weight:600}.page-header p{font-size:13px;color:var(--td-text-color-secondary);margin:0}.header-actions,.import-actions{display:flex;gap:10px;flex-shrink:0}.stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:24px}.stat-card{background:var(--td-bg-color-container,#fff);border:1px solid var(--td-component-border,#e8ebee);border-radius:12px;padding:20px 22px}.stat-card>span{font-size:12px;color:var(--td-text-color-secondary)}.stat-card>div{font-size:30px;font-weight:600;margin:10px 0;line-height:1.2;font-variant-numeric:tabular-nums}.stat-card small{font-size:11px;font-weight:400;color:var(--td-text-color-placeholder,#98a1aa);margin-left:9px}.stat-card p{margin:0;font-size:11px;color:var(--td-text-color-secondary)}.workspace{background:var(--td-bg-color-container,#fff);border:1px solid var(--td-component-border,#e8ebee);border-radius:14px;overflow:hidden}.workspace-tabs{height:60px;display:flex;align-items:stretch;gap:24px;padding:0 24px;border-bottom:1px solid var(--td-component-border,#e8ebee)}.workspace-tabs button{background:none;border:0;border-bottom:2px solid transparent;padding:0 2px;color:var(--td-text-color-secondary);font:inherit;font-size:13px;cursor:pointer}.workspace-tabs button.selected{color:#15986a;border-bottom-color:#15986a;font-weight:600}.workspace-tabs button span{font-size:10px;padding:2px 6px;background:rgba(21,152,106,.08);border-radius:5px;margin-left:5px}.save-hint{margin-left:auto;display:flex;align-items:center;gap:6px;font-size:11px;color:var(--td-text-color-placeholder,#98a1aa)}.import-bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px 24px}.section-heading strong{display:block;font-size:13px;font-weight:500}.section-heading>span{display:block;font-size:11px;color:var(--td-text-color-secondary);margin-top:5px}.session-picker{display:flex;gap:10px;padding:0 24px 20px}.empty-state{text-align:center;padding:40px 20px 52px}.empty-icon{width:70px;height:70px;background:rgba(21,152,106,.06);border:1px solid rgba(21,152,106,.08);border-radius:20px;color:#15986a;display:grid;place-items:center;margin:0 auto 20px;transform:rotate(-5deg)}.empty-icon>*{transform:rotate(5deg)}.empty-state h3{font-size:16px;font-weight:500;margin:0 0 12px}.empty-state p{font-size:12px;line-height:1.9;color:var(--td-text-color-secondary);margin:0 0 22px}.format-hint{display:block;font-size:10px;color:var(--td-text-color-placeholder,#98a1aa);margin-top:14px}.workspace-footer{border-top:1px solid var(--td-component-border,#e8ebee);padding:12px 24px;display:flex;align-items:center;justify-content:space-between;font-size:11px;color:var(--td-text-color-secondary);gap:15px}.workspace-footer i{display:inline-block;width:6px;height:6px;border-radius:50%;background:#a8b0b8;margin-right:7px}.workspace-footer i.running{background:#15986a}.metric-guide{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:26px;padding:0 6px}.metric-guide strong{font-size:12px;font-weight:500;margin-left:7px}.metric-guide .t-icon{color:#15986a;vertical-align:middle}.metric-guide p{font-size:11px;color:var(--td-text-color-secondary);margin:8px 0 0 23px;line-height:1.6}.footnote{font-size:10px;color:var(--td-text-color-placeholder,#98a1aa);line-height:1.8;margin:22px 6px 0}.samples-list{padding:0 24px 24px;display:grid;gap:16px}.sample-card{border:1px solid var(--td-component-border,#e8ebee);border-radius:10px;padding:18px}.sample-top,.sample-top>div{display:flex;align-items:center;gap:10px}.sample-top{justify-content:space-between;margin-bottom:16px}.sample-top strong{font-size:12px;font-weight:500}.sample-number{color:#15986a;font-size:11px;font-variant-numeric:tabular-nums}.source-tag{font-size:10px;background:var(--td-bg-color-secondarycontainer,#f3f5f6);padding:3px 7px;border-radius:4px;color:var(--td-text-color-secondary)}.fields{display:grid;grid-template-columns:1fr 1fr;gap:16px}label{display:block;font-size:11px;color:var(--td-text-color-secondary);line-height:2.3}label>span{font-size:10px;color:var(--td-text-color-placeholder)}.reference-field{margin-top:12px}details{margin-top:14px;font-size:11px}summary{cursor:pointer;color:var(--td-text-color-secondary)}summary span{margin-left:5px;color:#15986a}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--td-bg-color-secondarycontainer,#f7f8fa);border-radius:6px;padding:12px;line-height:1.8;max-height:250px;overflow:auto;font:inherit}.context-note{color:var(--td-text-color-placeholder);margin:10px 0}.result-line,.error{font-size:11px;line-height:1.8;margin-top:12px;overflow-wrap:anywhere}.result-line{color:#15986a}.error{color:var(--td-error-color,#c33)}.report-panel{padding:24px}.report-panel h3{font-size:15px}.summary{background:rgba(21,152,106,.06);padding:16px;border-radius:8px;font-size:12px;line-height:1.8;color:#15986a}.report-row{padding:18px 0;border-bottom:1px solid var(--td-component-border,#e8ebee)}.report-row strong{font-size:12px;font-weight:500}.report-row p{font-size:11px;line-height:1.8;color:var(--td-text-color-secondary)}@media(max-width:900px){.page-inner{padding:24px}.page-header{align-items:flex-start;flex-direction:column}.stats-grid{grid-template-columns:repeat(2,1fr)}.metric-guide{gap:12px}.fields{grid-template-columns:1fr}.save-hint{display:none}}@media(max-width:600px){.import-bar{align-items:flex-start;flex-direction:column}.metric-guide{grid-template-columns:1fr}.workspace-tabs{padding:0 18px}.stat-card{padding:16px}.page-inner{padding:18px}}
</style>
