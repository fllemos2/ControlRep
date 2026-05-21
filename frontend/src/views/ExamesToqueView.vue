<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { examesToque, toquesMatrizes, matrizes, chat, type ExameToque, type ToqueMatriz, type Matriz, type ChatMessage, type ChatAction } from '@/api/client'

const GESTACAO = 285

const listaExames  = ref<ExameToque[]>([])
const exameAtual   = ref<ExameToque | null>(null)
const toques       = ref<ToqueMatriz[]>([])
const allMatrizes  = ref<Matriz[]>([])
const loading      = ref(true)
const error        = ref('')
const gerandoPdf   = ref(false)
const expandido    = ref<'cheia' | 'parida' | 'vazia' | null>(null)

// --- Modal criar/editar exame ---
type Modo = 'criar' | 'editar'
const modalAberto  = ref(false)
const modalModo    = ref<Modo>('criar')
const salvando     = ref(false)
const erroModal    = ref('')
const form = ref({ id: 0, periodo_inicio: '', periodo_fim: '', veterinario: '', data_realizacao: '' })

onMounted(async () => {
  try {
    const [eRes, mRes] = await Promise.all([
      examesToque.list(),
      matrizes.list({ limit: 500 }),
    ])
    listaExames.value  = eRes.data
    allMatrizes.value  = mRes.data
    if (listaExames.value.length) exameAtual.value = listaExames.value[0] ?? null
  } catch {
    error.value = 'Erro ao carregar dados.'
  } finally {
    loading.value = false
  }
})

watch(exameAtual, async (ex) => {
  if (!ex) { toques.value = []; return }
  const res = await toquesMatrizes.list({ id_exame_toque: ex.id })
  toques.value = res.data
}, { immediate: true })

// ── computed ──────────────────────────────────────────────────────────────────

const toqueMap = computed(() => {
  const m: Record<number, ToqueMatriz> = {}
  toques.value.forEach(t => { m[t.id_matriz] = t })
  return m
})

const ativas = computed(() =>
  allMatrizes.value.filter(m => m.status === 'ativa' || m.status === 'inativa')
)

const cheias = computed(() => {
  if (!exameAtual.value) return []
  const dataExame = exameAtual.value.data_realizacao
  return ativas.value.filter(m => {
    const t = toqueMap.value[m.id]
    if (!t || t.resultado !== 'Cheia') return false
    if (m.ultima_cria_data && m.ultima_cria_data > dataExame) return false
    return true
  })
})

const paridas = computed(() => {
  if (!exameAtual.value) return []
  const dataExame = exameAtual.value.data_realizacao
  return ativas.value.filter(m => {
    const t = toqueMap.value[m.id]
    return t?.resultado === 'Cheia' && m.ultima_cria_data && m.ultima_cria_data > dataExame
  })
})

const vazias = computed(() => {
  if (!exameAtual.value) return []
  return ativas.value.filter(m => {
    const t = toqueMap.value[m.id]
    return !t || t.resultado === 'Vazia'
  })
})

// ── helpers ───────────────────────────────────────────────────────────────────

function formatDate(d: string | null | undefined) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

function previstoParto(m: Matriz): string {
  const t    = toqueMap.value[m.id]
  const exame = exameAtual.value
  if (!t?.dias_estimados_fecundacao || !exame) return '—'
  const restantes = GESTACAO - t.dias_estimados_fecundacao
  const base      = new Date(exame.data_realizacao + 'T00:00:00')
  const prev      = new Date(base.getTime() + restantes * 86400000)
  const min       = new Date(prev.getTime() - 30 * 86400000)
  const max       = new Date(prev.getTime() + 30 * 86400000)
  return `${min.toLocaleDateString('pt-BR')} – ${max.toLocaleDateString('pt-BR')}`
}

function corParto(m: Matriz): 'green' | 'yellow' | 'red' | 'gray' {
  const t     = toqueMap.value[m.id]
  const exame = exameAtual.value
  if (!t?.dias_estimados_fecundacao || !exame) return 'gray'
  const hoje      = new Date()
  const restantes = GESTACAO - t.dias_estimados_fecundacao
  const base      = new Date(exame.data_realizacao + 'T00:00:00')
  const previsto  = new Date(base.getTime() + restantes * 86400000)
  const ini       = new Date(previsto.getTime() - 30 * 86400000)
  const fim       = new Date(previsto.getTime() + 30 * 86400000)
  if (hoje > fim)  return 'red'
  if (hoje >= ini) return 'yellow'
  return 'green'
}

function toggleExpandido(cat: 'cheia' | 'parida' | 'vazia') {
  expandido.value = expandido.value === cat ? null : cat
}

// ── modal ─────────────────────────────────────────────────────────────────────

function abrirCriar() {
  modalModo.value = 'criar'; erroModal.value = ''
  form.value = { id: 0, periodo_inicio: '', periodo_fim: '', veterinario: '', data_realizacao: '' }
  modalAberto.value = true
}

function abrirEditar() {
  if (!exameAtual.value) return
  modalModo.value = 'editar'; erroModal.value = ''
  form.value = {
    id: exameAtual.value.id,
    periodo_inicio:  exameAtual.value.periodo_inicio,
    periodo_fim:     exameAtual.value.periodo_fim,
    veterinario:     exameAtual.value.veterinario ?? '',
    data_realizacao: exameAtual.value.data_realizacao,
  }
  modalAberto.value = true
}

function fecharModal() { modalAberto.value = false; erroModal.value = '' }

async function salvar() {
  erroModal.value = ''
  if (!form.value.periodo_inicio)  { erroModal.value = 'Data início obrigatória.'; return }
  if (!form.value.periodo_fim)     { erroModal.value = 'Data fim obrigatória.'; return }
  if (!form.value.data_realizacao) { erroModal.value = 'Data de realização obrigatória.'; return }
  salvando.value = true
  try {
    const payload = {
      periodo_inicio:  form.value.periodo_inicio,
      periodo_fim:     form.value.periodo_fim,
      veterinario:     form.value.veterinario || undefined,
      data_realizacao: form.value.data_realizacao,
    }
    if (modalModo.value === 'criar') {
      const res = await examesToque.create(payload)
      listaExames.value.unshift(res.data)
      exameAtual.value = res.data
    } else {
      const res = await examesToque.update(form.value.id, payload)
      const idx = listaExames.value.findIndex(x => x.id === form.value.id)
      if (idx !== -1) listaExames.value[idx] = res.data
      exameAtual.value = res.data
    }
    fecharModal()
  } catch { erroModal.value = 'Erro ao salvar.' }
  finally  { salvando.value = false }
}

async function excluir() {
  if (!exameAtual.value) return
  if (!confirm(`Excluir exame de ${formatDate(exameAtual.value.data_realizacao)}?`)) return
  try {
    await examesToque.delete(exameAtual.value.id)
    listaExames.value = listaExames.value.filter(x => x.id !== exameAtual.value!.id)
    exameAtual.value  = listaExames.value[0] ?? null
  } catch { alert('Erro ao excluir.') }
}

// ── IA / Chat ─────────────────────────────────────────────────────────────────

const chatScrollEl = ref<HTMLElement | null>(null)
const chatInput    = ref('')
const chatLoading  = ref(false)
const chatHistory  = ref<ChatMessage[]>([])
const chatActions  = ref<ChatAction[]>([])
const executando   = ref(false)
const execResults  = ref<string[]>([])

async function enviarMensagem() {
  const texto = chatInput.value.trim()
  if (!texto || chatLoading.value) return

  chatInput.value = ''
  chatActions.value = []
  execResults.value = []
  chatHistory.value.push({ role: 'user', content: texto })
  chatLoading.value = true
  await scrollChat()

  try {
    const res = await chat.send(texto, chatHistory.value.slice(0, -1))
    chatHistory.value.push({ role: 'assistant', content: res.data.message })
    chatActions.value = res.data.actions ?? []
  } catch {
    chatHistory.value.push({ role: 'assistant', content: 'Erro ao conectar com a IA. Verifique a chave ANTHROPIC_API_KEY nas configurações.' })
  } finally {
    chatLoading.value = false
    await scrollChat()
  }
}

async function confirmarAcoes() {
  if (!chatActions.value.length) return
  executando.value = true
  try {
    const res = await chat.execute(chatActions.value)
    execResults.value = res.data.results
    chatActions.value = []
    chatHistory.value.push({ role: 'assistant', content: 'Registros salvos com sucesso.' })
    // recarrega dados
    const [eRes, mRes] = await Promise.all([examesToque.list(), matrizes.list({ limit: 500 })])
    listaExames.value = eRes.data
    allMatrizes.value = mRes.data
  } catch {
    execResults.value = ['Erro ao executar as ações.']
  } finally {
    executando.value = false
    await scrollChat()
  }
}

function cancelarAcoes() {
  chatActions.value = []
}

async function scrollChat() {
  await nextTick()
  if (chatScrollEl.value) chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight
}

function onEnter(e: KeyboardEvent) {
  if (!e.shiftKey) { e.preventDefault(); enviarMensagem() }
}

async function emitirRelatorio() {
  gerandoPdf.value = true
  try {
    const res = await fetch('/api/v1/relatorios/desempenho-reprodutivo')
    if (!res.ok) throw new Error('Falha ao gerar PDF')
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'desempenho-reprodutivo.pdf'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch {
    alert('Erro ao gerar relatório PDF.')
  } finally {
    gerandoPdf.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Exame de Toque</h1>
      <div style="display:flex;gap:10px">
        <button class="btn btn-ghost" @click="emitirRelatorio" :disabled="gerandoPdf">
          {{ gerandoPdf ? 'Gerando...' : '📄 Relatório PDF' }}
        </button>
        <button class="btn btn-primary" @click="abrirCriar">+ Novo Exame</button>
      </div>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <template v-else>
      <div class="dois-col">

        <!-- ── Coluna esquerda: dados ── -->
        <div class="col-dados">

          <!-- Seletor de exame -->
          <div class="exame-selector card" v-if="listaExames.length">
            <div class="exame-selector-row">
              <div class="selector-label">Exame de Toque:</div>
              <select v-model="exameAtual" class="exame-select">
                <option v-for="e in listaExames" :key="e.id" :value="e">
                  {{ new Date(e.data_realizacao + 'T00:00:00').toLocaleDateString('pt-BR') }}
                  {{ e.veterinario ? '— ' + e.veterinario : '' }}
                </option>
              </select>
              <div class="exame-acoes">
                <button class="btn-edit-sm" @click="abrirEditar" title="Editar">✎</button>
                <button class="btn-del-sm"  @click="excluir"     title="Excluir">✕</button>
              </div>
            </div>

            <div v-if="exameAtual" class="exame-detalhes">
              <span class="det-item"><span class="det-label">Período</span>
                {{ formatDate(exameAtual.periodo_inicio) }} – {{ formatDate(exameAtual.periodo_fim) }}
              </span>
              <span class="det-item"><span class="det-label">Realização</span>
                <strong>{{ formatDate(exameAtual.data_realizacao) }}</strong>
              </span>
              <span class="det-item" v-if="exameAtual.veterinario">
                <span class="det-label">Veterinário</span> {{ exameAtual.veterinario }}
              </span>
            </div>
          </div>

          <div v-else class="card vazio-msg">Nenhum exame cadastrado. Clique em "+ Novo Exame".</div>

          <!-- Resumo quantitativo -->
          <div v-if="exameAtual" class="card resumo-card">
            <h3 class="resumo-titulo">Resumo do Exame</h3>

            <table class="resumo-table">
              <thead>
                <tr>
                  <th>Situação</th>
                  <th class="col-n">Qtd</th>
                  <th class="col-pct">%</th>
                </tr>
              </thead>
              <tbody>
                <tr class="resumo-row clickable"
                    :class="{ ativo: expandido === 'cheia' }"
                    @click="toggleExpandido('cheia')">
                  <td><span class="ic">☑️</span> Cheias — parto previsto</td>
                  <td class="col-n"><strong>{{ cheias.length }}</strong></td>
                  <td class="col-pct text-muted">{{ ativas.length ? Math.round(cheias.length / ativas.length * 100) : 0 }}%</td>
                </tr>
                <tr v-if="expandido === 'cheia'" class="detalhe-row">
                  <td colspan="3">
                    <table class="detalhe-table">
                      <thead><tr><th class="col-semaforo"></th><th>Matriz</th><th>Dias fec.</th><th>Previsão de parto (± 30 dias)</th></tr></thead>
                      <tbody>
                        <tr v-for="m in cheias" :key="m.id">
                          <td class="col-semaforo">
                            <span class="semaforo-dot" :class="corParto(m)"></span>
                          </td>
                          <td><strong>{{ m.numero_registro }}</strong></td>
                          <td class="text-muted">{{ toqueMap[m.id]?.dias_estimados_fecundacao ?? '—' }} dias</td>
                          <td>{{ previstoParto(m) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>

                <tr class="resumo-row clickable"
                    :class="{ ativo: expandido === 'parida' }"
                    @click="toggleExpandido('parida')">
                  <td><span class="ic">✅</span> Paridas após o toque</td>
                  <td class="col-n"><strong>{{ paridas.length }}</strong></td>
                  <td class="col-pct text-muted">{{ ativas.length ? Math.round(paridas.length / ativas.length * 100) : 0 }}%</td>
                </tr>
                <tr v-if="expandido === 'parida'" class="detalhe-row">
                  <td colspan="3">
                    <table class="detalhe-table">
                      <thead><tr><th>Matriz</th><th>Data do parto</th></tr></thead>
                      <tbody>
                        <tr v-for="m in paridas" :key="m.id">
                          <td><strong>{{ m.numero_registro }}</strong></td>
                          <td>{{ formatDate(m.ultima_cria_data) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>

                <tr class="resumo-row clickable"
                    :class="{ ativo: expandido === 'vazia' }"
                    @click="toggleExpandido('vazia')">
                  <td><span class="ic">❌❎</span> Vazias</td>
                  <td class="col-n"><strong>{{ vazias.length }}</strong></td>
                  <td class="col-pct text-muted">{{ ativas.length ? Math.round(vazias.length / ativas.length * 100) : 0 }}%</td>
                </tr>
                <tr v-if="expandido === 'vazia'" class="detalhe-row">
                  <td colspan="3">
                    <table class="detalhe-table">
                      <thead><tr><th>Matriz</th><th>Resultado toque</th><th>Último parto</th></tr></thead>
                      <tbody>
                        <tr v-for="m in vazias" :key="m.id">
                          <td><strong>{{ m.numero_registro }}</strong></td>
                          <td class="text-muted">{{ toqueMap[m.id]?.resultado ?? 'Sem registro' }}</td>
                          <td>{{ formatDate(m.ultima_cria_data) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>

                <tr class="resumo-total">
                  <td>Total de matrizes ativas</td>
                  <td class="col-n"><strong>{{ ativas.length }}</strong></td>
                  <td class="col-pct text-muted">100%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── Coluna direita: Assistente IA ── -->
        <div class="col-ia">
          <div class="ia-card card">
            <div class="ia-header">
              <span class="ia-icon">🤖</span>
              <div>
                <div class="ia-titulo">Assistente</div>
                <div class="ia-subtitulo">Escreva sobre o rebanho em linguagem natural</div>
              </div>
            </div>

            <!-- Histórico de mensagens -->
            <div class="ia-chat" ref="chatScrollEl">
              <div v-if="chatHistory.length === 0" class="ia-placeholder">
                <p>Olá! Posso ajudá-lo a registrar dados e analisar o rebanho.</p>
                <p>Exemplos:</p>
                <ul>
                  <li>"A matriz 1045 pariu ontem, foi macho"</li>
                  <li>"Quais matrizes cheias estão perto do parto?"</li>
                  <li>"Registrar toque: matriz 980 cheia, 60 dias"</li>
                </ul>
              </div>

              <div v-for="(msg, i) in chatHistory" :key="i"
                   class="ia-msg" :class="msg.role === 'user' ? 'ia-msg-user' : 'ia-msg-bot'">
                <div class="ia-msg-bubble">{{ msg.content }}</div>
              </div>

              <div v-if="chatLoading" class="ia-msg ia-msg-bot">
                <div class="ia-msg-bubble ia-digitando">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>

            <!-- Ações sugeridas -->
            <div v-if="chatActions.length" class="ia-acoes">
              <div class="ia-acoes-titulo">Confirmar ações:</div>
              <div v-for="(a, i) in chatActions" :key="i" class="ia-acao-item">
                {{ a.label }}
              </div>
              <div class="ia-acoes-btns">
                <button class="btn btn-ghost btn-sm" @click="cancelarAcoes" :disabled="executando">Cancelar</button>
                <button class="btn btn-primary btn-sm" @click="confirmarAcoes" :disabled="executando">
                  {{ executando ? 'Salvando…' : 'Confirmar e Salvar' }}
                </button>
              </div>
            </div>

            <!-- Resultados da execução -->
            <div v-if="execResults.length" class="ia-exec-results">
              <div v-for="(r, i) in execResults" :key="i" class="ia-exec-item"
                   :class="r.startsWith('ERRO') ? 'ia-exec-err' : 'ia-exec-ok'">
                {{ r }}
              </div>
            </div>

            <!-- Input -->
            <div class="ia-input-area">
              <textarea
                v-model="chatInput"
                class="ia-textarea"
                placeholder="Escreva aqui… (Enter para enviar)"
                rows="3"
                @keydown.enter="onEnter"
                :disabled="chatLoading"
              ></textarea>
              <button class="ia-send-btn" @click="enviarMensagem" :disabled="chatLoading || !chatInput.trim()">
                Enviar
              </button>
            </div>
          </div>
        </div>

      </div><!-- .dois-col -->
    </template>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="modalAberto" class="modal-overlay" @click.self="fecharModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ modalModo === 'criar' ? 'Novo Exame de Toque' : 'Editar Exame' }}</h2>
            <button class="modal-close" @click="fecharModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>Período — início <span class="req">*</span></label>
                <input v-model="form.periodo_inicio" type="date" />
              </div>
              <div class="form-group">
                <label>Período — fim <span class="req">*</span></label>
                <input v-model="form.periodo_fim" type="date" />
              </div>
              <div class="form-group">
                <label>Data de Realização <span class="req">*</span></label>
                <input v-model="form.data_realizacao" type="date" />
              </div>
              <div class="form-group">
                <label>Veterinário</label>
                <input v-model="form.veterinario" type="text" placeholder="Nome do veterinário" />
              </div>
            </div>
            <p v-if="erroModal" class="erro-modal">{{ erroModal }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="fecharModal" :disabled="salvando">Cancelar</button>
            <button class="btn btn-primary" @click="salvar" :disabled="salvando">
              {{ salvando ? 'Salvando…' : (modalModo === 'criar' ? 'Criar' : 'Salvar') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
/* Layout duas colunas */
.dois-col {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 20px;
  align-items: start;
}
.col-dados { min-width: 0; }
.col-ia    { position: sticky; top: 20px; }

@media (max-width: 900px) {
  .dois-col { grid-template-columns: 1fr; }
  .col-ia   { position: static; }
}

/* ── Painel IA ─────────────────────────────────────────────── */
.ia-card {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0;
  overflow: hidden;
  height: calc(100vh - 140px);
  min-height: 420px;
}

.ia-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #f8fdf8;
}
.ia-icon    { font-size: 1.6rem; line-height: 1; }
.ia-titulo  { font-size: 0.95rem; font-weight: 700; color: #2c3e50; }
.ia-subtitulo { font-size: 0.75rem; color: #888; margin-top: 2px; }

.ia-chat {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ia-placeholder {
  color: #aaa;
  font-size: 0.85rem;
  line-height: 1.7;
}
.ia-placeholder p { margin: 0 0 6px; }
.ia-placeholder ul { margin: 0; padding-left: 18px; }
.ia-placeholder li { margin-bottom: 4px; }

.ia-msg { display: flex; }
.ia-msg-user { justify-content: flex-end; }
.ia-msg-bot  { justify-content: flex-start; }

.ia-msg-bubble {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 0.88rem;
  line-height: 1.55;
  white-space: pre-wrap;
}
.ia-msg-user .ia-msg-bubble {
  background: #2c5f2e;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.ia-msg-bot .ia-msg-bubble {
  background: #f0f0f0;
  color: #2c3e50;
  border-bottom-left-radius: 4px;
}

/* Animação "digitando" */
.ia-digitando {
  display: flex;
  gap: 5px;
  padding: 12px 16px;
  align-items: center;
}
.ia-digitando span {
  width: 7px; height: 7px;
  background: #888;
  border-radius: 50%;
  animation: dot-bounce 1.2s infinite;
}
.ia-digitando span:nth-child(2) { animation-delay: 0.2s; }
.ia-digitando span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot-bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40%           { transform: translateY(-6px); }
}

/* Ações sugeridas */
.ia-acoes {
  border-top: 1px solid #e0f0e0;
  padding: 12px 20px;
  background: #f0faf0;
}
.ia-acoes-titulo { font-size: 0.78rem; font-weight: 700; color: #2c5f2e; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.04em; }
.ia-acao-item { font-size: 0.85rem; color: #444; padding: 4px 0; border-bottom: 1px dashed #d4edda; }
.ia-acao-item:last-of-type { border-bottom: none; }
.ia-acoes-btns { display: flex; gap: 8px; justify-content: flex-end; margin-top: 10px; }

.btn-sm { padding: 6px 14px; font-size: 0.82rem; }

/* Resultados execução */
.ia-exec-results { padding: 8px 20px; border-top: 1px solid #f0f0f0; }
.ia-exec-item { font-size: 0.82rem; padding: 3px 0; }
.ia-exec-ok  { color: #2c5f2e; }
.ia-exec-err { color: #c62828; }

/* Input */
.ia-input-area {
  border-top: 1px solid #f0f0f0;
  padding: 12px 16px;
  display: flex;
  gap: 10px;
  align-items: flex-end;
  background: #fafafa;
}
.ia-textarea {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.5;
  transition: border-color 0.15s;
}
.ia-textarea:focus { border-color: #2c5f2e; }
.ia-textarea:disabled { background: #f5f5f5; color: #aaa; }
.ia-send-btn {
  padding: 10px 18px;
  background: #2c5f2e;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}
.ia-send-btn:hover:not(:disabled) { background: #1e4220; }
.ia-send-btn:disabled { background: #a5c8a6; cursor: default; }

/* Seletor */
.exame-selector { margin-bottom: 20px; }
.exame-selector-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.selector-label { font-size: 0.85rem; font-weight: 600; color: #555; white-space: nowrap; }
.exame-select {
  padding: 7px 10px; border: 1px solid #ddd; border-radius: 7px;
  font-size: 0.875rem; font-family: inherit; outline: none; flex: 1; min-width: 200px;
}
.exame-select:focus { border-color: #2c5f2e; }
.exame-acoes { display: flex; gap: 6px; }
.btn-edit-sm, .btn-del-sm {
  background: none; border: 1px solid #ddd; border-radius: 5px;
  padding: 4px 10px; cursor: pointer; font-size: 0.85rem;
}
.btn-edit-sm { color: #555; }
.btn-edit-sm:hover { background: #f5f5f5; }
.btn-del-sm { color: #c62828; border-color: #f5c6c6; }
.btn-del-sm:hover { background: #fde8e8; }

.exame-detalhes {
  display: flex; flex-wrap: wrap; gap: 20px;
  margin-top: 12px; padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.det-item { font-size: 0.875rem; color: #555; }
.det-label { font-size: 0.75rem; font-weight: 600; color: #aaa; display: block; margin-bottom: 2px; }

.vazio-msg { color: #aaa; text-align: center; padding: 32px; }

/* Resumo */
.resumo-card { }
.resumo-titulo { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin-bottom: 16px; }

.resumo-table { width: 100%; border-collapse: collapse; }
.resumo-table th {
  background: #f8f9fa; padding: 8px 14px;
  text-align: left; font-size: 0.82rem; color: #666;
  border-bottom: 2px solid #e9ecef;
}
.col-n   { text-align: right; width: 70px; }
.col-pct { text-align: right; width: 60px; }

.resumo-row td { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }
.resumo-row.clickable { cursor: pointer; }
.resumo-row.clickable:hover td { background: #f8fdf8; }
.resumo-row.ativo td { background: #f0f7f0; }

.ic { font-size: 1rem; margin-right: 6px; }

.resumo-total td {
  padding: 10px 14px; font-size: 0.9rem;
  border-top: 2px solid #e9ecef; font-weight: 600; color: #2c3e50;
  background: #f8f9fa;
}

/* Detalhe expandido */
.detalhe-row td { padding: 0; background: #f8fdf8; }
.detalhe-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.detalhe-table th {
  padding: 6px 14px; background: #edf7ed;
  text-align: left; font-size: 0.78rem; color: #555;
  border-bottom: 1px solid #d4edda;
}
.detalhe-table td { padding: 7px 14px; border-bottom: 1px solid #f0f0f0; color: #444; }
.detalhe-table tr:last-child td { border-bottom: none; }
.detalhe-table tr:hover td { background: #f0faf0; }

.text-muted { color: #aaa; }

/* Semáforo de parto */
.col-semaforo { width: 28px; text-align: center; padding: 7px 6px; }
.semaforo-dot {
  display: inline-block;
  width: 11px; height: 11px;
  border-radius: 50%;
  cursor: default;
}
.semaforo-dot.green  { background: #43a047; }
.semaforo-dot.yellow { background: #fb8c00; }
.semaforo-dot.red    { background: #e53935; }
.semaforo-dot.gray   { background: #bdbdbd; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.modal {
  background: white; border-radius: 12px; width: 100%; max-width: 480px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18); overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 16px; border-bottom: 1px solid #f0f0f0;
}
.modal-header h2 { font-size: 1.1rem; font-weight: 700; }
.modal-close { background: none; border: none; font-size: 1rem; cursor: pointer; color: #999; padding: 4px 8px; border-radius: 4px; }
.modal-close:hover { background: #f5f5f5; }
.modal-body { padding: 20px 24px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 24px 20px; border-top: 1px solid #f0f0f0; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; }
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group label { font-size: 0.82rem; font-weight: 600; color: #555; }
.form-group input { padding: 8px 10px; border: 1px solid #ddd; border-radius: 7px; font-size: 0.875rem; font-family: inherit; outline: none; }
.form-group input:focus { border-color: #2c5f2e; }
.req { color: #c62828; }
.erro-modal { margin-top: 12px; color: #c62828; font-size: 0.85rem; background: #ffebee; padding: 8px 12px; border-radius: 6px; }
</style>
