<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { matrizes, examesToque, toquesMatrizes, type Matriz, type ExameToque, type ToqueMatriz } from '@/api/client'

const all = ref<Matriz[]>([])
const loading = ref(true)
const error = ref('')
const hoje = new Date()
const mostrarInativas = ref(false)

// --- Exames de toque disponíveis ---
const listaExames = ref<ExameToque[]>([])
const allToques = ref<ToqueMatriz[]>([])

// Map exame id -> exame
const exameMap = computed(() => {
  const m: Record<number, ExameToque> = {}
  listaExames.value.forEach(e => { m[e.id] = e })
  return m
})

// Map id_matriz -> último toque (pelo mais recente data_realizacao)
const toqueMap = computed(() => {
  const m: Record<number, { toque: ToqueMatriz; dataExame: string }> = {}
  for (const t of allToques.value) {
    const exame = exameMap.value[t.id_exame_toque]
    if (!exame) continue
    const existing = m[t.id_matriz]
    if (!existing || exame.data_realizacao > existing.dataExame) {
      m[t.id_matriz] = { toque: t, dataExame: exame.data_realizacao }
    }
  }
  return m
})

function iconeToque(m: Matriz): 'cheia' | 'parida' | 'vazia-alerta' | 'vazia-ok' | null {
  if (m.status === 'morta' || m.status === 'descartada') return null

  const entry = toqueMap.value[m.id]

  if (!entry) {
    // Sem toque registrado → trata como Vazia, referência = hoje
    if (!m.ultima_cria_data) return 'vazia-alerta'
    const meses = (hoje.getTime() - new Date(m.ultima_cria_data + 'T00:00:00').getTime()) / (86400000 * 30)
    return meses > 9 ? 'vazia-alerta' : 'vazia-ok'
  }

  if (entry.toque.resultado === 'Cheia') {
    if (m.ultima_cria_data && m.ultima_cria_data > entry.dataExame) return 'parida'
    return 'cheia'
  }

  if (entry.toque.resultado === 'Vazia') {
    if (!m.ultima_cria_data) return 'vazia-alerta'
    const dtExame = new Date(entry.dataExame + 'T00:00:00')
    const dtCria  = new Date(m.ultima_cria_data + 'T00:00:00')
    const meses   = (dtExame.getTime() - dtCria.getTime()) / (86400000 * 30)
    return meses > 9 ? 'vazia-alerta' : 'vazia-ok'
  }

  return null
}

// --- Modal editar / criar Matriz ---
const editModalAberto = ref(false)
const editModo = ref<'editar' | 'criar'>('editar')
const editSalvando = ref(false)
const editErro = ref('')
const editMatrizId = ref(0)
const editForm = ref({ numero_registro: '', brinco: '', raca: 'Nelore', parceria: 'Fazenda', observacoes: '' })

// --- Modal toque ---
const toqueModalAberto = ref(false)
const toqueMatrizAlvo = ref<Matriz | null>(null)
const toqueSalvando = ref(false)
const toqueErro = ref('')
const toqueForm = ref({
  id_exame_toque: 0,
  resultado: '',
  dias_estimados_fecundacao: '',
  observacoes: '',
})

// --- Modal de descarte ---
const modalAberto = ref(false)
const matrizModal = ref<Matriz | null>(null)
const motivoDescarte = ref('')
const salvando = ref(false)

onMounted(async () => {
  try {
    const [mRes, eRes, tRes] = await Promise.all([
      matrizes.list({ limit: 500 }),
      examesToque.list(),
      toquesMatrizes.list(),
    ])
    all.value = mRes.data
    listaExames.value = eRes.data
    allToques.value = tRes.data
  } catch {
    error.value = 'Erro ao carregar matrizes.'
  } finally {
    loading.value = false
  }
})

function mesesEntre(inicio: string | null, fim: string | null): number | null {
  if (!inicio || !fim) return null
  const d1 = new Date(inicio + 'T00:00:00')
  const d2 = new Date(fim + 'T00:00:00')
  const dias = (d2.getTime() - d1.getTime()) / 86400000
  return (dias + 1) / 30
}

function mesesMaisGestacao(m: Matriz): string {
  const v = mesesEntre(m.primeira_cria_data, m.ultima_cria_data)
  if (v === null) return 'S/R'
  return (v + 9.5).toFixed(2)
}

function mesesPorCria(m: Matriz): number | null {
  const v = mesesEntre(m.primeira_cria_data, m.ultima_cria_data)
  if (v === null || !m.total_crias) return null
  return (v + 9.5) / m.total_crias
}

function mesesDesdeUltimaCria(m: Matriz): number | null {
  if (!m.ultima_cria_data) return null
  const d = new Date(m.ultima_cria_data + 'T00:00:00')
  return (hoje.getTime() - d.getTime()) / (86400000 * 30)
}

function corFarol(m: Matriz): 'green' | 'yellow' | 'red' | 'gray' {
  const meses = mesesPorCria(m)
  if (meses === null) return 'gray'
  if (meses < 13) return 'green'
  if (meses <= 15) return 'yellow'
  return 'red'
}

const ativas = computed(() => all.value.filter(m => m.status === 'ativa' || m.status === 'inativa'))
const inativas = computed(() => all.value.filter(m => m.status === 'morta' || m.status === 'descartada'))
const listagem = computed(() => mostrarInativas.value ? all.value : ativas.value)

function parceria(m: Matriz): string {
  if (m.parceria) return m.parceria
  const obs = (m.observacoes || '').toLowerCase()
  if (/fabio/.test(obs)) return 'Fabio'
  if (/mary|mari/.test(obs)) return 'Mariana'
  return 'Fazenda'
}

function formatDate(d: string | null): string {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

// --- Ações de status ---

function abrirDescarte(m: Matriz) {
  matrizModal.value = m
  motivoDescarte.value = ''
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  matrizModal.value = null
  motivoDescarte.value = ''
}

async function confirmarDescarte() {
  const m = matrizModal.value
  if (!m) return
  salvando.value = true
  try {
    const dataHoje = hoje.toLocaleDateString('pt-BR')
    const entrada = motivoDescarte.value.trim()
    const novaObs = [m.observacoes?.trim(), `Descartada em ${dataHoje}${entrada ? ': ' + entrada : '.'}`]
      .filter(Boolean).join('\n')
    const res = await matrizes.update(m.id, { status: 'descartada', observacoes: novaObs })
    const idx = all.value.findIndex(x => x.id === m.id)
    if (idx !== -1) all.value[idx] = res.data
    fecharModal()
  } catch {
    alert('Erro ao salvar. Tente novamente.')
  } finally {
    salvando.value = false
  }
}

async function reativar(m: Matriz) {
  if (!confirm(`Reativar a matriz ${m.numero_registro}?`)) return
  try {
    const res = await matrizes.update(m.id, { status: 'ativa' })
    const idx = all.value.findIndex(x => x.id === m.id)
    if (idx !== -1) all.value[idx] = res.data
  } catch {
    alert('Erro ao reativar. Tente novamente.')
  }
}

function abrirToque(m: Matriz) {
  toqueMatrizAlvo.value = m
  toqueErro.value = ''
  const defaultExame = listaExames.value[0]?.id ?? 0
  toqueForm.value = {
    id_exame_toque: defaultExame,
    resultado: '',
    dias_estimados_fecundacao: '',
    observacoes: '',
  }
  toqueModalAberto.value = true
}

function fecharToqueModal() {
  toqueModalAberto.value = false
  toqueMatrizAlvo.value = null
  toqueErro.value = ''
}

async function salvarToque() {
  toqueErro.value = ''
  if (!toqueForm.value.resultado) { toqueErro.value = 'Selecione o resultado do toque.'; return }
  if (!toqueForm.value.id_exame_toque) { toqueErro.value = 'Selecione o exame de toque.'; return }

  toqueSalvando.value = true
  try {
    await toquesMatrizes.create({
      id_matriz: toqueMatrizAlvo.value!.id,
      id_exame_toque: toqueForm.value.id_exame_toque,
      resultado: toqueForm.value.resultado,
      dias_estimados_fecundacao: toqueForm.value.resultado === 'Cheia' && toqueForm.value.dias_estimados_fecundacao
        ? Number(toqueForm.value.dias_estimados_fecundacao)
        : undefined,
      observacoes: toqueForm.value.observacoes || undefined,
    })
    fecharToqueModal()
  } catch {
    toqueErro.value = 'Erro ao salvar. Tente novamente.'
  } finally {
    toqueSalvando.value = false
  }
}

function labelExame(e: ExameToque): string {
  return `${new Date(e.data_realizacao + 'T00:00:00').toLocaleDateString('pt-BR')}${e.veterinario ? ' — ' + e.veterinario : ''}`
}

function abrirEditar(m: Matriz) {
  editModo.value = 'editar'
  editErro.value = ''
  editMatrizId.value = m.id
  editForm.value = {
    numero_registro: m.numero_registro,
    brinco: m.brinco,
    raca: m.raca,
    parceria: parceria(m),
    observacoes: m.observacoes ?? '',
  }
  editModalAberto.value = true
}

function abrirCriarMatriz() {
  editModo.value = 'criar'
  editErro.value = ''
  editMatrizId.value = 0
  editForm.value = { numero_registro: '', brinco: '', raca: 'Nelore', parceria: 'Fazenda', observacoes: '' }
  editModalAberto.value = true
}

function fecharEditModal() {
  editModalAberto.value = false
  editErro.value = ''
}

async function salvarMatriz() {
  editErro.value = ''
  if (!editForm.value.numero_registro.trim()) { editErro.value = 'Número de registro obrigatório.'; return }
  if (!editForm.value.brinco.trim()) { editErro.value = 'Brinco obrigatório.'; return }

  editSalvando.value = true
  try {
    if (editModo.value === 'criar') {
      const res = await matrizes.create({
        numero_registro: editForm.value.numero_registro.trim(),
        brinco: editForm.value.brinco.trim(),
        raca: editForm.value.raca,
        parceria: editForm.value.parceria,
        observacoes: editForm.value.observacoes || undefined,
      })
      all.value.unshift(res.data)
    } else {
      const res = await matrizes.update(editMatrizId.value, {
        parceria: editForm.value.parceria,
        observacoes: editForm.value.observacoes || undefined,
      })
      const idx = all.value.findIndex(x => x.id === editMatrizId.value)
      if (idx !== -1) all.value[idx] = res.data
    }
    fecharEditModal()
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    editErro.value = msg ?? 'Erro ao salvar.'
  } finally {
    editSalvando.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h1>Matrizes <span class="count">({{ listagem.length }})</span></h1>
        <div class="posicao">Posição em: {{ hoje.toLocaleDateString('pt-BR') }}</div>
      </div>
      <div class="controles">
        <button class="btn btn-primary" @click="abrirCriarMatriz">+ Nova Matriz</button>
        <button class="btn-toggle" @click="mostrarInativas = !mostrarInativas">
          {{ mostrarInativas ? 'Ocultar descartadas/mortas' : `Mostrar descartadas/mortas (${inativas.length})` }}
        </button>
      </div>
      <div class="legenda">
        <span class="dot green"></span> &lt; 13 meses
        <span class="dot yellow"></span> 13 – 15 meses
        <span class="dot red"></span> &gt; 15 meses
      </div>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th class="col-num">Nº Ord.</th>
              <th class="col-flag"></th>
              <th>Nº Reg.</th>
              <th>1ª Cria</th>
              <th>Últ. Cria</th>
              <th class="col-num">Meses + 9,5</th>
              <th class="col-num">Nº Crias</th>
              <th class="col-num">Meses/Cria</th>
              <th>Parceria</th>
              <th>OBS</th>
              <th class="col-status-h">Status</th>
              <th class="col-toque" title="Resultado do último toque">Toque</th>
              <th class="col-acao"></th>
              <th class="col-acao"></th>
              <th class="col-acao"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(m, idx) in listagem" :key="m.id" :class="{ 'row-inativa': m.status === 'morta' || m.status === 'descartada' }">
              <td class="col-num text-muted">{{ idx + 1 }}</td>
              <td class="col-flag">
                <span v-if="m.status === 'morta'" class="flag flag-morta" title="Morta">✕</span>
                <span v-else-if="m.status === 'descartada'" class="flag flag-descartada" title="Descartada">D</span>
              </td>
              <td><strong>{{ m.numero_registro }}</strong></td>
              <td>{{ formatDate(m.primeira_cria_data) }}</td>
              <td class="col-farol">
                <span class="dot" :class="corFarol(m)"></span>
                {{ formatDate(m.ultima_cria_data) }}
              </td>
              <td class="col-num">{{ mesesMaisGestacao(m) }}</td>
              <td class="col-num">{{ m.total_crias || '—' }}</td>
              <td class="col-num">
                <span v-if="mesesPorCria(m) !== null" class="meses-cria" :class="`cor-${corFarol(m)}`">
                  {{ mesesPorCria(m)!.toFixed(2) }}
                </span>
                <span v-else class="text-muted">—</span>
              </td>
              <td><span class="badge-parceria" :class="`parceria-${parceria(m).toLowerCase()}`">{{ parceria(m) }}</span></td>
              <td class="col-obs">{{ m.observacoes || '' }}</td>
              <td class="col-status">
                <button
                  v-if="m.status === 'ativa' || m.status === 'inativa'"
                  class="status-btn status-ativa"
                  @click="abrirDescarte(m)"
                  title="Clique para descartar"
                >
                  <span class="status-dot on"></span> Ativa
                </button>
                <button
                  v-else-if="m.status === 'descartada'"
                  class="status-btn status-descartada"
                  @click="reativar(m)"
                  title="Clique para reativar"
                >
                  <span class="status-dot off"></span> Descartada
                </button>
                <span v-else class="status-morta">
                  <span class="status-dot dead"></span> Morta
                </span>
              </td>
              <td class="col-toque">
                <span v-if="iconeToque(m) === 'cheia'"        title="Cheia">☑️</span>
                <span v-else-if="iconeToque(m) === 'parida'"  title="Parida após o toque">✅</span>
                <span v-else-if="iconeToque(m) === 'vazia-alerta'" title="Vazia — última cria há mais de 9 meses">❌</span>
                <span v-else-if="iconeToque(m) === 'vazia-ok'"     title="Vazia — última cria há 9 meses ou menos">❎</span>
              </td>
              <td>
                <RouterLink :to="`/matrizes/${m.id}`" class="link-crias">crias</RouterLink>
              </td>
              <td>
                <button class="btn-edit-row" @click="abrirEditar(m)" title="Editar">✎</button>
              </td>
              <td>
                <button
                  v-if="m.status === 'ativa' || m.status === 'inativa'"
                  class="btn-toque"
                  @click="abrirToque(m)"
                  :title="listaExames.length ? 'Registrar resultado de toque' : 'Cadastre um Exame de Toque primeiro'"
                  :disabled="!listaExames.length"
                >Toque</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal editar / criar Matriz -->
    <Teleport to="body">
      <div v-if="editModalAberto" class="modal-overlay" @click.self="fecharEditModal">
        <div class="modal">
          <div class="modal-header">
            <h2>{{ editModo === 'criar' ? 'Nova Matriz' : `Editar Matriz ${editForm.numero_registro}` }}</h2>
            <button class="modal-close" @click="fecharEditModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid-edit">
              <template v-if="editModo === 'criar'">
                <div class="form-group-edit">
                  <label>Nº Registro <span class="req">*</span></label>
                  <input v-model="editForm.numero_registro" type="text" placeholder="Ex: 1001" />
                </div>
                <div class="form-group-edit">
                  <label>Brinco <span class="req">*</span></label>
                  <input v-model="editForm.brinco" type="text" placeholder="Ex: 1001" />
                </div>
                <div class="form-group-edit">
                  <label>Raça</label>
                  <input v-model="editForm.raca" type="text" placeholder="Nelore" />
                </div>
              </template>
              <div class="form-group-edit">
                <label>Parceria</label>
                <select v-model="editForm.parceria">
                  <option value="Fazenda">Fazenda</option>
                  <option value="Fabio">Fabio</option>
                  <option value="Mariana">Mariana</option>
                </select>
              </div>
              <div class="form-group-edit full">
                <label>Observações</label>
                <textarea v-model="editForm.observacoes" rows="3" placeholder="Anotações livres..."></textarea>
              </div>
            </div>
            <p v-if="editErro" class="erro-modal">{{ editErro }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="fecharEditModal" :disabled="editSalvando">Cancelar</button>
            <button class="btn btn-primary" @click="salvarMatriz" :disabled="editSalvando">
              {{ editSalvando ? 'Salvando…' : (editModo === 'criar' ? 'Criar' : 'Salvar') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal de toque -->
    <Teleport to="body">
      <div v-if="toqueModalAberto" class="modal-overlay" @click.self="fecharToqueModal">
        <div class="modal">
          <div class="modal-header">
            <h2>Informações de Toque — Matriz {{ toqueMatrizAlvo?.numero_registro }}</h2>
            <button class="modal-close" @click="fecharToqueModal">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-grid-toque">
              <div class="form-group-toque full">
                <label>Exame de Toque <span class="req">*</span></label>
                <select v-model="toqueForm.id_exame_toque">
                  <option v-for="e in listaExames" :key="e.id" :value="e.id">
                    {{ labelExame(e) }}
                  </option>
                </select>
              </div>

              <div class="form-group-toque full">
                <label>Resultado do Toque <span class="req">*</span></label>
                <div class="resultado-opts">
                  <label class="resultado-label" :class="{ ativo: toqueForm.resultado === 'Cheia' }">
                    <input type="radio" v-model="toqueForm.resultado" value="Cheia" />
                    <span class="resultado-badge badge-cheia">Cheia</span>
                  </label>
                  <label class="resultado-label" :class="{ ativo: toqueForm.resultado === 'Vazia' }">
                    <input type="radio" v-model="toqueForm.resultado" value="Vazia" />
                    <span class="resultado-badge badge-vazia">Vazia</span>
                  </label>
                </div>
              </div>

              <div v-if="toqueForm.resultado === 'Cheia'" class="form-group-toque full">
                <label>Dias estimados da fecundação</label>
                <input
                  v-model="toqueForm.dias_estimados_fecundacao"
                  type="number"
                  min="1"
                  max="280"
                  placeholder="Ex: 45"
                />
              </div>

              <div class="form-group-toque full">
                <label>Observações</label>
                <textarea
                  v-model="toqueForm.observacoes"
                  maxlength="200"
                  rows="3"
                  placeholder="Anotações livres (máx. 200 caracteres)"
                ></textarea>
                <span class="char-count">{{ toqueForm.observacoes.length }}/200</span>
              </div>
            </div>
            <p v-if="toqueErro" class="erro-modal">{{ toqueErro }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="fecharToqueModal" :disabled="toqueSalvando">Cancelar</button>
            <button class="btn btn-primary" @click="salvarToque" :disabled="toqueSalvando">
              {{ toqueSalvando ? 'Salvando…' : 'Registrar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal de descarte -->
    <Teleport to="body">
      <div v-if="modalAberto" class="modal-overlay" @click.self="fecharModal">
        <div class="modal">
          <div class="modal-header">
            <h2>Descartar Matriz {{ matrizModal?.numero_registro }}</h2>
            <button class="modal-close" @click="fecharModal">✕</button>
          </div>
          <div class="modal-body">
            <label class="modal-label">Motivo do descarte <span class="opcional">(opcional)</span></label>
            <textarea
              v-model="motivoDescarte"
              class="modal-textarea"
              placeholder="Ex: vendida c/12@ para Arlindo em 05/2026..."
              rows="4"
              autofocus
            ></textarea>
            <p class="modal-hint">
              O texto será adicionado ao campo Observações e o status alterado para <strong>Descartada</strong>.
            </p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-ghost" @click="fecharModal" :disabled="salvando">Cancelar</button>
            <button class="btn btn-danger" @click="confirmarDescarte" :disabled="salvando">
              {{ salvando ? 'Salvando…' : 'Confirmar descarte' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.count { font-size: 1rem; font-weight: 400; color: #888; }
.posicao { font-size: 0.8rem; color: #999; margin-top: 2px; }

.legenda {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  color: #555;
  background: #f8f9fa;
  padding: 8px 14px;
  border-radius: 8px;
}

/* Farol dot */
.dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot.green  { background: #43a047; }
.dot.yellow { background: #fb8c00; }
.dot.red    { background: #e53935; }
.dot.gray   { background: #bdbdbd; }

/* Colunas */
.col-num { text-align: right; white-space: nowrap; }
.col-farol { white-space: nowrap; display: flex; align-items: center; gap: 6px; }
.col-obs { max-width: 180px; font-size: 0.82rem; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-status { white-space: nowrap; }

.text-muted { color: #aaa; }

/* Meses/Cria colorido */
.meses-cria { font-weight: 600; }
.cor-green  { color: #2e7d32; }
.cor-yellow { color: #e65100; }
.cor-red    { color: #c62828; }
.cor-gray   { color: #aaa; }

.link-crias {
  color: #2c5f2e;
  font-size: 0.8rem;
  text-decoration: none;
  white-space: nowrap;
}
.link-crias:hover { text-decoration: underline; }

/* FLAG column */
.col-flag { width: 28px; text-align: center; padding: 0 4px; }
.flag { display: inline-flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; line-height: 1; }
.flag-morta { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
.flag-descartada { background: #fff3e0; color: #e65100; border: 1px solid #ffcc80; }

/* Rows inativas */
.row-inativa td { opacity: 0.55; }

/* Botão toggle visibilidade */
.controles { display: flex; align-items: center; gap: 10px; }
.btn-toggle {
  font-size: 0.78rem;
  padding: 5px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  color: #555;
  white-space: nowrap;
}
.btn-toggle:hover { background: #f5f5f5; }

/* Parceria badges */
.badge-parceria {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}
.parceria-fabio    { background: #e8f4fd; color: #1565c0; }
.parceria-mariana  { background: #fce4ec; color: #880e4f; }
.parceria-fazenda  { background: #f1f8e9; color: #33691e; }

/* Botões de status inline */
.status-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: 1.5px solid transparent;
  transition: opacity 0.15s, box-shadow 0.15s;
}
.status-btn:hover { opacity: 0.8; box-shadow: 0 0 0 2px rgba(0,0,0,0.08); }

.status-ativa    { background: #e6f4ea; color: #2c5f2e; border-color: #a5d6a7; }
.status-descartada { background: #fff3e0; color: #e65100; border-color: #ffcc80; }

.status-morta {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #c62828;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.on   { background: #43a047; }
.status-dot.off  { background: #fb8c00; }
.status-dot.dead { background: #e53935; }

/* Colunas de ação — largura fixa, não comprimem */
.col-acao { width: 1px; white-space: nowrap; }
.col-status-h { white-space: nowrap; }

/* Ícones resultado toque */
.col-toque { text-align: center; width: 48px; white-space: nowrap; font-size: 1rem; }

/* Botão editar linha */
.btn-edit-row {
  background: none; border: 1px solid #ddd; border-radius: 5px;
  padding: 2px 7px; cursor: pointer; color: #777; font-size: 0.85rem;
}
.btn-edit-row:hover { background: #f5f5f5; border-color: #bbb; }

/* Modal editar/criar form */
.form-grid-edit { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; }
.form-group-edit { display: flex; flex-direction: column; gap: 5px; }
.form-group-edit.full { grid-column: 1 / -1; }
.form-group-edit label { font-size: 0.82rem; font-weight: 600; color: #555; }
.form-group-edit input,
.form-group-edit select,
.form-group-edit textarea {
  padding: 8px 10px; border: 1px solid #ddd; border-radius: 7px;
  font-size: 0.875rem; font-family: inherit; outline: none;
  transition: border-color 0.15s;
}
.form-group-edit input:focus,
.form-group-edit select:focus,
.form-group-edit textarea:focus { border-color: #2c5f2e; }
.form-group-edit textarea { resize: vertical; }

/* Botão Toque */
.btn-toque {
  font-size: 0.75rem;
  padding: 3px 10px;
  border: 1px solid #b0bec5;
  border-radius: 6px;
  background: #eceff1;
  color: #455a64;
  cursor: pointer;
  white-space: nowrap;
}
.btn-toque:hover:not(:disabled) { background: #cfd8dc; }
.btn-toque:disabled { opacity: 0.4; cursor: not-allowed; }

/* Modal toque — form */
.form-grid-toque { display: flex; flex-direction: column; gap: 14px; }
.form-group-toque { display: flex; flex-direction: column; gap: 5px; }
.form-group-toque label { font-size: 0.82rem; font-weight: 600; color: #555; }
.form-group-toque input,
.form-group-toque select,
.form-group-toque textarea {
  padding: 8px 10px; border: 1px solid #ddd; border-radius: 7px;
  font-size: 0.875rem; font-family: inherit; outline: none;
  transition: border-color 0.15s;
}
.form-group-toque input:focus,
.form-group-toque select:focus,
.form-group-toque textarea:focus { border-color: #2c5f2e; }
.form-group-toque textarea { resize: vertical; }
.char-count { font-size: 0.72rem; color: #aaa; text-align: right; }

.resultado-opts { display: flex; gap: 12px; }
.resultado-label {
  display: flex; align-items: center; gap: 7px;
  cursor: pointer; padding: 6px 12px;
  border: 2px solid #e0e0e0; border-radius: 8px;
  transition: border-color 0.15s;
}
.resultado-label.ativo { border-color: #2c5f2e; }
.resultado-label input[type="radio"] { accent-color: #2c5f2e; }
.resultado-badge {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  font-size: 0.8rem; font-weight: 700;
}
.badge-cheia { background: #e6f4ea; color: #2c5f2e; }
.badge-vazia  { background: #fff3e0; color: #e65100; }

/* btn-danger global (não tem no App.vue) */
.btn-danger { background: #c62828; color: white; }
.btn-danger:hover { opacity: 0.87; }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ghost:disabled { opacity: 0.5; cursor: not-allowed; }

/* Modal overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
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
.modal-header h2 { font-size: 1.1rem; font-weight: 700; color: #2c3e50; }
.modal-close {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: #999;
  padding: 4px 8px;
  border-radius: 4px;
}
.modal-close:hover { background: #f5f5f5; color: #555; }

.modal-body { padding: 20px 24px; }
.modal-label { display: block; font-size: 0.875rem; font-weight: 600; color: #444; margin-bottom: 8px; }
.opcional { font-weight: 400; color: #999; }
.modal-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  outline: none;
  transition: border-color 0.15s;
}
.modal-textarea:focus { border-color: #c62828; }
.modal-hint {
  margin-top: 10px;
  font-size: 0.8rem;
  color: #888;
  line-height: 1.4;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px 20px;
  border-top: 1px solid #f0f0f0;
}
</style>
