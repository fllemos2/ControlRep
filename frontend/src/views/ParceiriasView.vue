<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { parcerias as parceriasApi, type ParceriaResumo } from '@/api/client'

const loading = ref(true)
const error = ref('')
const lista = ref<ParceriaResumo[]>([])
const selecionada = ref('')

onMounted(async () => {
  try {
    const { data } = await parceriasApi.resumo()
    lista.value = data
    if (data.length > 0) selecionada.value = data[0]?.nome ?? ''
  } catch {
    error.value = 'Erro ao carregar parcerias'
  } finally {
    loading.value = false
  }
})

const parceriaAtual = computed(() =>
  lista.value.find(p => p.nome === selecionada.value) ?? null
)

function fmt(v: number) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

<template>
  <div v-if="loading" class="loading">Carregando…</div>
  <div v-else-if="error" class="error-msg">{{ error }}</div>
  <div v-else class="parcerias-layout">

    <!-- Coluna esquerda: lista de parceiros -->
    <aside class="parceiros-sidebar">
      <div class="sidebar-title">Parceiros</div>
      <ul class="parceiros-lista">
        <li
          v-for="p in lista"
          :key="p.nome"
          class="parceiro-item"
          :class="{ ativo: selecionada === p.nome }"
          @click="selecionada = p.nome"
        >
          <span class="parceiro-nome">{{ p.nome }}</span>
          <span class="parceiro-badge">{{ p.total_matrizes }}</span>
        </li>
      </ul>
    </aside>

    <!-- Coluna direita: detalhes do parceiro -->
    <section class="parceiro-detalhe" v-if="parceriaAtual">
      <div class="page-header">
        <h1>{{ parceriaAtual.nome }}</h1>
      </div>

      <!-- KPIs -->
      <div class="kpis-row">
        <div class="kpi-card">
          <span class="kpi-valor">{{ parceriaAtual.total_matrizes }}</span>
          <span class="kpi-label">Matrizes</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-valor">{{ parceriaAtual.total_crias }}</span>
          <span class="kpi-label">Crias totais</span>
        </div>
        <div class="kpi-card kpi-destaque">
          <span class="kpi-valor">{{ parceriaAtual.total_crias_no_pasto }}</span>
          <span class="kpi-label">No pasto</span>
        </div>
        <div class="kpi-card kpi-verde">
          <span class="kpi-valor">{{ fmt(parceriaAtual.total_valor_vendido) }}</span>
          <span class="kpi-label">Total vendas</span>
        </div>
      </div>

      <!-- Tabela de matrizes -->
      <div class="card table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Registro</th>
              <th>Brinco</th>
              <th>Status</th>
              <th style="text-align:center">Qtd Crias</th>
              <th style="text-align:center">No Pasto</th>
              <th style="text-align:right">Vendas</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in parceriaAtual.matrizes" :key="m.id">
              <td>{{ m.numero_registro }}</td>
              <td>{{ m.brinco }}</td>
              <td>
                <span
                  class="badge"
                  :class="m.status === 'ativa' ? 'badge-green' : 'badge-gray'"
                >{{ m.status }}</span>
              </td>
              <td style="text-align:center">{{ m.total_crias }}</td>
              <td style="text-align:center">
                <span v-if="m.crias_no_pasto > 0" class="badge badge-green">
                  {{ m.crias_no_pasto }}
                </span>
                <span v-else class="sem">—</span>
              </td>
              <td style="text-align:right">
                <span v-if="m.valor_vendido > 0">{{ fmt(m.valor_vendido) }}</span>
                <span v-else class="sem">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</template>

<style scoped>
.parcerias-layout {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

/* Sidebar */
.parceiros-sidebar {
  width: 180px;
  flex-shrink: 0;
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  overflow: hidden;
}

.sidebar-title {
  padding: 14px 16px 10px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #888;
  border-bottom: 1px solid #f0f0f0;
}

.parceiros-lista {
  list-style: none;
  padding: 6px 0;
}

.parceiro-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.12s;
  border-left: 3px solid transparent;
}

.parceiro-item:hover { background: #f5f5f0; }

.parceiro-item.ativo {
  background: #f0f7f0;
  border-left-color: #2c5f2e;
}

.parceiro-nome {
  font-size: 0.9rem;
  font-weight: 500;
  color: #2c3e50;
}

.parceiro-item.ativo .parceiro-nome { color: #2c5f2e; font-weight: 600; }

.parceiro-badge {
  background: #e9ecef;
  color: #666;
  border-radius: 10px;
  font-size: 0.72rem;
  padding: 1px 7px;
  font-weight: 600;
}

.parceiro-item.ativo .parceiro-badge { background: #c8e6c9; color: #2c5f2e; }

/* Detalhe */
.parceiro-detalhe { flex: 1; min-width: 0; }

/* KPIs */
.kpis-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-destaque { border-top: 3px solid #1565c0; }
.kpi-verde    { border-top: 3px solid #2c5f2e; }

.kpi-valor {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1;
}

.kpi-label {
  font-size: 0.78rem;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.sem { color: #ccc; }
</style>
