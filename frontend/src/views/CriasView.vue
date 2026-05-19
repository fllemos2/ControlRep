<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { crias, matrizes, type Cria, type Matriz } from '@/api/client'

const RACAS = ['Nel. Branca', 'Nel. Castanho', 'Nel. Pintado']
const STATUS_OPTS = ['No Pasto', 'Vendido', 'Morto', 'SUBMAT']
const STATUS_BADGE: Record<string, string> = {
  'No Pasto': 'badge-pasto',
  'Vendido':  'badge-vendido',
  'Morto':    'badge-morto',
  'SUBMAT':   'badge-submat',
}

const all = ref<Cria[]>([])
const allMatrizes = ref<Matriz[]>([])
const loading = ref(true)
const error = ref('')

const filtroStatus = ref('No Pasto')
const filtroSexo = ref('')
const filtroMatriz = ref('')

// --- Modal ---
type Modo = 'criar' | 'editar'
const modalAberto = ref(false)
const modalModo = ref<Modo>('criar')
const salvando = ref(false)
const erroModal = ref('')

const form = ref({
  id: 0,
  id_matriz: 0,
  numero_registro: '',
  raca_pelagem: '',
  sexo: '',
  data_nascimento: '',
  pai: '',
  status: 'No Pasto',
})

onMounted(async () => {
  try {
    const [cRes, mRes] = await Promise.all([
      crias.list({ limit: 2000 }),
      matrizes.list({ limit: 500 }),
    ])
    all.value = cRes.data
    allMatrizes.value = mRes.data
  } catch {
    error.value = 'Erro ao carregar dados.'
  } finally {
    loading.value = false
  }
})

function sortByNumReg(a: Cria, b: Cria) {
  const na = parseInt(a.numero_registro ?? '')
  const nb = parseInt(b.numero_registro ?? '')
  if (!isNaN(na) && !isNaN(nb)) return na - nb
  return (a.numero_registro ?? '').localeCompare(b.numero_registro ?? '', 'pt-BR', { numeric: true })
}

const lista = computed(() => {
  let items = all.value
  if (filtroStatus.value)  items = items.filter(c => c.status === filtroStatus.value)
  if (filtroSexo.value)    items = items.filter(c => c.sexo === filtroSexo.value)
  if (filtroMatriz.value)  items = items.filter(c => c.id_matriz === Number(filtroMatriz.value))
  return [...items].sort(sortByNumReg)
})

// Nº de ordem: sequencial só para "No Pasto" dentro da listagem atual
const ordemMap = computed(() => {
  const m: Record<number, number> = {}
  let seq = 0
  lista.value.forEach(c => {
    if (c.status === 'No Pasto') m[c.id] = ++seq
  })
  return m
})

const matrizMap = computed(() => {
  const m: Record<number, string> = {}
  allMatrizes.value.forEach(mx => { m[mx.id] = mx.numero_registro })
  return m
})

const totalNoPasto = computed(() => all.value.filter(c => c.status === 'No Pasto').length)

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

// --- Modal helpers ---

function nextNumeroRegistro(): string {
  const nums = all.value
    .map(c => parseInt(c.numero_registro ?? ''))
    .filter(n => !isNaN(n) && n > 0)
  return nums.length > 0 ? String(Math.max(...nums) + 1) : ''
}

function abrirCriar() {
  modalModo.value = 'criar'
  erroModal.value = ''
  form.value = { id: 0, id_matriz: 0, numero_registro: nextNumeroRegistro(), raca_pelagem: '', sexo: '', data_nascimento: '', pai: '', status: 'No Pasto' }
  modalAberto.value = true
}

function abrirEditar(c: Cria) {
  modalModo.value = 'editar'
  erroModal.value = ''
  form.value = {
    id: c.id,
    id_matriz: c.id_matriz,
    numero_registro: c.numero_registro ?? '',
    raca_pelagem: c.raca_pelagem ?? '',
    sexo: c.sexo ?? '',
    data_nascimento: c.data_nascimento ?? '',
    pai: c.pai ?? '',
    status: c.status ?? 'No Pasto',
  }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  erroModal.value = ''
}

async function salvar() {
  erroModal.value = ''
  if (!form.value.data_nascimento) { erroModal.value = 'Data do parto obrigatória.'; return }
  if (!form.value.id_matriz) { erroModal.value = 'Selecione a matriz.'; return }

  salvando.value = true
  try {
    if (modalModo.value === 'criar') {
      const payload = {
        id_matriz: form.value.id_matriz,
        numero_registro: form.value.numero_registro || undefined,
        raca_pelagem: form.value.raca_pelagem || undefined,
        sexo: form.value.sexo || undefined,
        data_nascimento: form.value.data_nascimento,
        pai: form.value.pai || undefined,
        status: form.value.status,
      }
      const res = await crias.create(payload)
      all.value.push(res.data)
    } else {
      const payload = {
        numero_registro: form.value.numero_registro || undefined,
        raca_pelagem: form.value.raca_pelagem || undefined,
        sexo: form.value.sexo || undefined,
        data_nascimento: form.value.data_nascimento,
        pai: form.value.pai || undefined,
        status: form.value.status,
      }
      const res = await crias.update(form.value.id, payload)
      const idx = all.value.findIndex(c => c.id === form.value.id)
      if (idx !== -1) all.value[idx] = res.data
    }
    fecharModal()
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    erroModal.value = msg ?? 'Erro ao salvar. Verifique os dados.'
  } finally {
    salvando.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Crias <span class="count">({{ lista.length }})</span></h1>
        <div class="sub">{{ totalNoPasto }} no pasto</div>
      </div>
      <button class="btn btn-primary" @click="abrirCriar">+ Nova Cria</button>
    </div>

    <div class="filters">
      <select v-model="filtroStatus">
        <option value="">Todos os status</option>
        <option v-for="s in STATUS_OPTS" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="filtroSexo">
        <option value="">Todos os sexos</option>
        <option value="M">Macho</option>
        <option value="F">Fêmea</option>
      </select>
      <select v-model="filtroMatriz">
        <option value="">Todas as matrizes</option>
        <option v-for="m in allMatrizes" :key="m.id" :value="m.id">{{ m.numero_registro }}</option>
      </select>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th class="col-num">Nº Ord.</th>
              <th>Reg. Nasc.</th>
              <th>Raça / Pelagem</th>
              <th class="col-center">Sexo</th>
              <th>Data do Parto</th>
              <th>Pai</th>
              <th>Matriz</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in lista" :key="c.id" :class="{ 'row-off': c.status !== 'No Pasto' }">
              <td class="col-num text-muted">
                {{ ordemMap[c.id] ?? '—' }}
              </td>
              <td><strong>{{ c.numero_registro ?? '—' }}</strong></td>
              <td>{{ c.raca_pelagem ?? '—' }}</td>
              <td class="col-center">
                <span v-if="c.sexo" class="badge" :class="c.sexo === 'M' ? 'badge-blue' : 'badge-red'">
                  {{ c.sexo === 'M' ? 'M' : 'F' }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td>{{ formatDate(c.data_nascimento) }}</td>
              <td class="col-pai">{{ c.pai ?? '—' }}</td>
              <td class="text-muted">{{ matrizMap[c.id_matriz] ?? c.id_matriz }}</td>
              <td>
                <span class="badge-status" :class="STATUS_BADGE[c.status] ?? ''">{{ c.status }}</span>
              </td>
              <td>
                <button class="btn-edit" @click="abrirEditar(c)" title="Editar">✎</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal criar / editar -->
    <Teleport to="body">
      <div v-if="modalAberto" class="modal-overlay" @click.self="fecharModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ modalModo === 'criar' ? 'Nova Cria' : 'Editar Cria' }}</h2>
            <button class="modal-close" @click="fecharModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid">
              <div class="form-group">
                <label>Matriz <span class="req">*</span></label>
                <select v-model="form.id_matriz">
                  <option :value="0" disabled>— selecione —</option>
                  <option v-for="m in allMatrizes" :key="m.id" :value="m.id">{{ m.numero_registro }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Reg. Nasc.</label>
                <input v-model="form.numero_registro" type="text" placeholder="Número de registro" />
              </div>
              <div class="form-group">
                <label>Raça / Pelagem</label>
                <select v-model="form.raca_pelagem">
                  <option value="">— selecione —</option>
                  <option v-for="r in RACAS" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Sexo</label>
                <select v-model="form.sexo">
                  <option value="">— selecione —</option>
                  <option value="M">M — Macho</option>
                  <option value="F">F — Fêmea</option>
                </select>
              </div>
              <div class="form-group">
                <label>Data do Parto <span class="req">*</span></label>
                <input v-model="form.data_nascimento" type="date" />
              </div>
              <div class="form-group">
                <label>Pai</label>
                <input v-model="form.pai" type="text" placeholder="Nome ou identificação do pai" />
              </div>
              <div class="form-group full">
                <label>Status</label>
                <div class="radio-group">
                  <label v-for="s in STATUS_OPTS" :key="s" class="radio-label">
                    <input type="radio" v-model="form.status" :value="s" />
                    <span class="badge-status" :class="STATUS_BADGE[s]">{{ s }}</span>
                  </label>
                </div>
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
.count { font-size: 1rem; font-weight: 400; color: #888; }
.sub   { font-size: 0.8rem; color: #999; margin-top: 2px; }

/* Colunas */
.col-num    { text-align: right; white-space: nowrap; width: 60px; }
.col-center { text-align: center; }
.col-pai    { max-width: 160px; font-size: 0.85rem; color: #555; }
.text-muted { color: #aaa; }

/* Linhas não-pasto */
.row-off td { opacity: 0.5; }

/* Botão editar */
.btn-edit {
  background: none;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 2px 8px;
  cursor: pointer;
  color: #555;
  font-size: 0.9rem;
}
.btn-edit:hover { background: #f5f5f5; border-color: #bbb; }

/* Status badges */
.badge-status {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}
.badge-pasto   { background: #e6f4ea; color: #2c5f2e; }
.badge-vendido { background: #e3f2fd; color: #1565c0; }
.badge-morto   { background: #ffebee; color: #c62828; }
.badge-submat  { background: #f3e5f5; color: #6a1b9a; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 540px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  overflow: hidden;
}
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.modal-header h2 { font-size: 1.1rem; font-weight: 700; }
.modal-close {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: #999;
  padding: 4px 8px;
  border-radius: 4px;
}
.modal-close:hover { background: #f5f5f5; }

.modal-body { padding: 20px 24px; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid #f0f0f0;
}

/* Form grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 20px;
}
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 0.82rem; font-weight: 600; color: #555; }
.form-group input,
.form-group select {
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 7px;
  font-size: 0.875rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}
.form-group input:focus,
.form-group select:focus { border-color: #2c5f2e; }
.req { color: #c62828; }

/* Radio group para status */
.radio-group { display: flex; gap: 10px; flex-wrap: wrap; }
.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.radio-label input[type="radio"] { accent-color: #2c5f2e; }

.erro-modal {
  margin-top: 12px;
  color: #c62828;
  font-size: 0.85rem;
  background: #ffebee;
  padding: 8px 12px;
  border-radius: 6px;
}
</style>
