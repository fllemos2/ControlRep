<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { matrizes, crias, type Matriz, type Cria, type Financeiro } from '@/api/client'

const route = useRoute()
const id = Number(route.params.id)

const matriz = ref<Matriz | null>(null)
const filhos = ref<Cria[]>([])
const financeiro = ref<Financeiro | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [mRes, cRes, fRes] = await Promise.all([
      matrizes.get(id),
      crias.list({ id_matriz: id, limit: 500 }),
      matrizes.financeiro(id),
    ])
    matriz.value = mRes.data
    filhos.value = cRes.data
    financeiro.value = fRes.data
  } catch {
    error.value = 'Erro ao carregar dados da matriz.'
  } finally {
    loading.value = false
  }
})

function formatDate(d: string | null) {
  if (!d) return '—'
  return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR')
}

function brl(v: number | null) {
  if (v === null || v === undefined) return '—'
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <RouterLink to="/matrizes" class="back-link">← Matrizes</RouterLink>
        <h1 v-if="matriz">Matriz {{ matriz.brinco }}</h1>
      </div>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <template v-else-if="matriz">
      <div class="info-grid">
        <div class="card info-card">
          <h3>Dados Gerais</h3>
          <div class="info-row"><span>Brinco</span><strong>{{ matriz.brinco }}</strong></div>
          <div class="info-row"><span>Registro</span><strong>{{ matriz.numero_registro }}</strong></div>
          <div class="info-row"><span>Raça</span><strong>{{ matriz.raca }}</strong></div>
          <div class="info-row">
            <span>Status</span>
            <span class="badge" :class="matriz.status === 'ativa' ? 'badge-green' : 'badge-gray'">
              {{ matriz.status }}
            </span>
          </div>
        </div>
        <div class="card info-card">
          <h3>Histórico Reprodutivo</h3>
          <div class="info-row"><span>Total de crias</span><strong>{{ matriz.total_crias }}</strong></div>
          <div class="info-row"><span>1ª cria</span><strong>{{ formatDate(matriz.primeira_cria_data) }}</strong></div>
          <div class="info-row"><span>Última cria</span><strong>{{ formatDate(matriz.ultima_cria_data) }}</strong></div>
          <div class="info-row">
            <span>Intervalo médio</span>
            <strong>{{ matriz.media_dias_intervalo ? `${matriz.media_dias_intervalo} dias` : '—' }}</strong>
          </div>
        </div>
      </div>

      <div v-if="matriz.observacoes" class="card obs-card">
        <strong>Observações:</strong> {{ matriz.observacoes }}
      </div>

      <!-- Card financeiro -->
      <div v-if="financeiro" class="card fin-card">
        <div class="fin-header">
          <h3>Rendimento Financeiro</h3>
          <span class="fin-ref">
            Valores corrigidos pelo IPCA até {{ new Date(financeiro.data_referencia + 'T00:00:00').toLocaleDateString('pt-BR') }}
            <span v-if="!financeiro.ipca_disponivel" class="fin-aviso"> (estimado 5,5% a.a.)</span>
          </span>
        </div>

        <div class="fin-grid">
          <!-- Coluna 1: Realizados -->
          <div class="fin-bloco">
            <div class="fin-bloco-titulo">Vendas registradas ({{ financeiro.crias_com_valor }})</div>
            <div class="fin-linha">
              <span>Total nominal</span>
              <strong>{{ brl(financeiro.total_nominal) }}</strong>
            </div>
            <div class="fin-linha destaque">
              <span>Total corrigido pelo IPCA</span>
              <strong class="valor-verde">{{ brl(financeiro.total_corrigido) }}</strong>
            </div>
            <div class="fin-linha">
              <span>Média por cria (nominal)</span>
              <span>{{ brl(financeiro.media_nominal) }}</span>
            </div>
            <div class="fin-linha">
              <span>Média por cria (corrigida)</span>
              <span>{{ brl(financeiro.media_corrigida) }}</span>
            </div>
          </div>

          <!-- Divider -->
          <div class="fin-divider"></div>

          <!-- Coluna 2: Estimados -->
          <div class="fin-bloco">
            <div class="fin-bloco-titulo">Crias sem valor registrado ({{ financeiro.crias_sem_valor }})</div>
            <div class="fin-linha">
              <span>Valor estimado por cria</span>
              <span>{{ brl(financeiro.media_corrigida) }}</span>
            </div>
            <div class="fin-linha destaque">
              <span>Total estimado</span>
              <strong class="valor-laranja">{{ brl(financeiro.total_estimado) }}</strong>
            </div>
          </div>

          <!-- Divider -->
          <div class="fin-divider"></div>

          <!-- Coluna 3: Total geral -->
          <div class="fin-bloco fin-total">
            <div class="fin-bloco-titulo">Total geral</div>
            <div class="fin-total-valor">{{ brl(financeiro.total_geral) }}</div>
            <div v-if="financeiro.valor_por_ano" class="fin-total-ano">
              {{ brl(financeiro.valor_por_ano) }}<span class="fin-total-ano-label">&nbsp;/ ano produtivo</span>
            </div>
            <div class="fin-total-sub">
              {{ financeiro.total_crias }} crias
              <template v-if="financeiro.anos_produtivos"> · {{ financeiro.anos_produtivos }} anos produtivos</template>
            </div>
            <div class="fin-total-sub">
              {{ financeiro.crias_com_valor }} realizadas ·
              {{ financeiro.crias_sem_valor }} estimadas
            </div>
          </div>
        </div>

        <div class="fin-nota">
          <span v-if="financeiro.idade_media_venda_dias">
            Idade média na venda: <strong>{{ Math.round(financeiro.idade_media_venda_dias / 30) }} meses</strong>
            — usada como base IPCA para crias com valor mas sem data de venda registrada.
          </span>
          <span v-if="!financeiro.ipca_disponivel" class="fin-aviso">
            ⚠ API do Banco Central indisponível — correção estimada em 5,5% a.a.
          </span>
        </div>
      </div>

      <h2 class="section-title">Crias ({{ filhos.length }})</h2>
      <div class="card">
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Nº Reg.</th>
                <th>Sexo</th>
                <th>Nascimento</th>
                <th>Status</th>
                <th>Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filhos" :key="c.id">
                <td>{{ c.numero_registro ?? '—' }}</td>
                <td>
                  <span class="badge" :class="c.sexo === 'M' ? 'badge-blue' : 'badge-red'">
                    {{ c.sexo === 'M' ? 'Macho' : c.sexo === 'F' ? 'Fêmea' : '—' }}
                  </span>
                </td>
                <td>{{ formatDate(c.data_nascimento) }}</td>
                <td class="td-status">
                  <span v-if="c.status === 'Vendido'" class="ic-venda" title="Vendido">&#36;</span>
                  <span v-else-if="c.status === 'Morto'" class="ic-morto" title="Morto">&#x1F480;</span>
                  {{ c.status ?? '—' }}
                </td>
                <td>{{ c.valor_venda ? `R$ ${c.valor_venda.toLocaleString('pt-BR')}` : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.back-link { color: #2c5f2e; text-decoration: none; font-size: 0.875rem; display: block; margin-bottom: 6px; }
.back-link:hover { text-decoration: underline; }

.info-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; margin-bottom: 16px; }

.info-card h3 { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin-bottom: 16px; }

.info-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.info-row:last-child { border-bottom: none; }
.info-row span:first-child { color: #666; font-size: 0.875rem; }

.obs-card { margin-bottom: 24px; font-size: 0.9rem; color: #555; }

.section-title { font-size: 1.15rem; font-weight: 600; margin: 24px 0 12px; }

/* Card financeiro */
.fin-card { margin-bottom: 24px; }

.fin-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 6px;
}
.fin-header h3 { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin: 0; }
.fin-ref { font-size: 0.78rem; color: #aaa; }
.fin-aviso { color: #fb8c00; }

.fin-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  gap: 0;
  align-items: start;
}

.fin-divider {
  width: 1px;
  background: #f0f0f0;
  align-self: stretch;
  margin: 0 24px;
}

.fin-bloco { display: flex; flex-direction: column; gap: 10px; }

.fin-bloco-titulo {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #aaa;
  margin-bottom: 4px;
}

.fin-linha {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
  color: #555;
  padding: 5px 0;
  border-bottom: 1px solid #f8f8f8;
}
.fin-linha:last-child { border-bottom: none; }
.fin-linha.destaque { background: #fafafa; border-radius: 6px; padding: 7px 10px; margin: 0 -10px; border: none; }
.fin-linha strong { font-size: 0.95rem; }

.valor-verde  { color: #2c5f2e; }
.valor-laranja { color: #e65100; }

.fin-total {
  text-align: center;
  align-items: center;
  justify-content: center;
  padding: 12px 0;
}
.fin-total-valor {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 8px 0 4px;
}
.fin-total-ano { font-size: 1rem; font-weight: 600; color: #5a8a5c; margin: 2px 0 6px; }
.fin-total-ano-label { font-size: 0.72rem; font-weight: 400; color: #aaa; }
.fin-total-sub { font-size: 0.78rem; color: #aaa; }
.td-status { white-space: nowrap; }
.ic-venda { color: #2e7d32; font-weight: 700; margin-right: 3px; }
.ic-morto { margin-right: 3px; font-size: 0.9rem; }

.fin-nota { margin-top: 16px; padding-top: 12px; border-top: 1px solid #f0f0f0; font-size: 0.78rem; color: #aaa; display: flex; flex-wrap: wrap; gap: 12px; }

@media (max-width: 700px) {
  .fin-grid { grid-template-columns: 1fr; }
  .fin-divider { width: 100%; height: 1px; margin: 16px 0; }
}
</style>
