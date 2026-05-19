<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { examesToque, toquesMatrizes, matrizes, type ExameToque, type ToqueMatriz, type Matriz } from '@/api/client'

const GESTACAO = 285

const listaExames  = ref<ExameToque[]>([])
const exameAtual   = ref<ExameToque | null>(null)
const toques       = ref<ToqueMatriz[]>([])
const allMatrizes  = ref<Matriz[]>([])
const loading      = ref(true)
const error        = ref('')
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
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Exame de Toque</h1>
      <button class="btn btn-primary" @click="abrirCriar">+ Novo Exame</button>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <template v-else>
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
            <!-- Cheias -->
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
                        <span class="semaforo-dot" :class="corParto(m)" :title="corParto(m)==='green'?'Parto: ainda no prazo':corParto(m)==='yellow'?'Parto: dentro da janela (±30 dias)':corParto(m)==='red'?'Parto: prazo vencido — não pariu':''"></span>
                      </td>
                      <td><strong>{{ m.numero_registro }}</strong></td>
                      <td class="text-muted">{{ toqueMap[m.id]?.dias_estimados_fecundacao ?? '—' }} dias</td>
                      <td>{{ previstoParto(m) }}</td>
                    </tr>
                  </tbody>
                </table>
              </td>
            </tr>

            <!-- Paridas -->
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

            <!-- Vazias -->
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

            <!-- Total -->
            <tr class="resumo-total">
              <td>Total de matrizes ativas</td>
              <td class="col-n"><strong>{{ ativas.length }}</strong></td>
              <td class="col-pct text-muted">100%</td>
            </tr>
          </tbody>
        </table>
      </div>
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
