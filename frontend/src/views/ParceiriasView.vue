<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { parcerias as parceriasApi, type ParceriaResumo, type MatrizResumo } from '@/api/client'

const loading = ref(true)
const error = ref('')
const lista = ref<ParceriaResumo[]>([])
const selecionada = ref('') // '' = todos

onMounted(async () => {
  try {
    const { data } = await parceriasApi.resumo()
    lista.value = data
  } catch {
    error.value = 'Erro ao carregar parcerias'
  } finally {
    loading.value = false
  }
})

// Todas as matrizes de todas as parcerias (com nome do parceiro embutido)
interface MatrizComParceria extends MatrizResumo {
  parceiro: string
  crias_vendidas: number
}

const todasMatrizes = computed<MatrizComParceria[]>(() =>
  lista.value.flatMap(p =>
    p.matrizes.map(m => ({
      ...m,
      parceiro: p.nome,
      crias_vendidas: (m as any).crias_vendidas ?? 0,
    }))
  ).sort((a, b) => {
    const na = parseInt(a.numero_registro), nb = parseInt(b.numero_registro)
    if (!isNaN(na) && !isNaN(nb)) return na - nb
    return a.numero_registro.localeCompare(b.numero_registro, 'pt-BR', { numeric: true })
  })
)

const matrizesFiltradas = computed<MatrizComParceria[]>(() =>
  selecionada.value
    ? todasMatrizes.value.filter(m => m.parceiro === selecionada.value)
    : todasMatrizes.value
)

const kpis = computed(() => {
  const mats = matrizesFiltradas.value
  return {
    matrizes:    mats.length,
    total_crias: mats.reduce((s, m) => s + m.total_crias, 0),
    no_pasto:    mats.reduce((s, m) => s + m.crias_no_pasto, 0),
    vendidas:    mats.reduce((s, m) => s + m.crias_vendidas, 0),
    valor:       mats.reduce((s, m) => s + m.valor_vendido, 0),
  }
})

function fmt(v: number) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
</script>

<template>
  <div v-if="loading" class="loading">Carregando…</div>
  <div v-else-if="error" class="error-msg">{{ error }}</div>
  <div v-else class="parcerias-layout">

    <!-- Sidebar: filtro por parceiro -->
    <aside class="parceiros-sidebar">
      <div class="sidebar-title">Parceiros</div>
      <ul class="parceiros-lista">
        <li
          class="parceiro-item"
          :class="{ ativo: selecionada === '' }"
          @click="selecionada = ''"
        >
          <span class="parceiro-nome">Todos</span>
          <span class="parceiro-badge">{{ todasMatrizes.length }}</span>
        </li>
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

      <!-- Resumo vertical abaixo da lista -->
      <div class="sidebar-resumo">
        <div class="sidebar-title">Resumo</div>
        <div class="resumo-item">
          <span class="resumo-label">Matrizes</span>
          <span class="resumo-valor">{{ kpis.matrizes }}</span>
        </div>
        <div class="resumo-item">
          <span class="resumo-label">Crias Totais</span>
          <span class="resumo-valor">{{ kpis.total_crias }}</span>
        </div>
        <div class="resumo-item resumo-destaque">
          <span class="resumo-label">No Pasto</span>
          <span class="resumo-valor">{{ kpis.no_pasto }}</span>
        </div>
        <div class="resumo-item">
          <span class="resumo-label">Vendidas</span>
          <span class="resumo-valor">{{ kpis.vendidas }}</span>
        </div>
        <div class="resumo-item resumo-verde">
          <span class="resumo-label">Total Vendas</span>
          <span class="resumo-valor resumo-moeda">{{ fmt(kpis.valor) }}</span>
        </div>
      </div>
    </aside>

    <!-- Conteúdo principal -->
    <section class="parceiro-detalhe">
      <div class="page-header">
        <h1>{{ selecionada || 'Todas as Matrizes' }}</h1>
      </div>

      <!-- Tabela de matrizes -->
      <div class="card table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Registro</th>
              <th v-if="!selecionada">Parceiro</th>
              <th>Status</th>
              <th style="text-align:center">Total Crias</th>
              <th style="text-align:center">No Pasto</th>
              <th style="text-align:center">Vendidas</th>
              <th style="text-align:right">Valor Vendas</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in matrizesFiltradas" :key="m.id">
              <td><strong>{{ m.numero_registro }}</strong></td>
              <td v-if="!selecionada" class="text-muted">{{ m.parceiro }}</td>
              <td>
                <span class="badge" :class="m.status === 'ativa' ? 'badge-green' : 'badge-gray'">
                  {{ m.status }}
                </span>
              </td>
              <td style="text-align:center"><strong>{{ m.total_crias }}</strong></td>
              <td style="text-align:center">
                <span v-if="m.crias_no_pasto > 0" class="badge badge-green">{{ m.crias_no_pasto }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td style="text-align:center">
                <span v-if="m.crias_vendidas > 0" class="badge badge-blue">{{ m.crias_vendidas }}</span>
                <span v-else class="text-muted">—</span>
              </td>
              <td style="text-align:right">
                <span v-if="m.valor_vendido > 0">{{ fmt(m.valor_vendido) }}</span>
                <span v-else class="text-muted">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </div>
</template>

<style scoped>
.parcerias-layout { display: flex; gap: 24px; align-items: flex-start; }

/* Sidebar */
.parceiros-sidebar {
  width: 210px; flex-shrink: 0;
  background: white; border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  overflow: hidden; position: sticky; top: 20px;
}
.sidebar-title {
  padding: 14px 16px 10px;
  font-size: 0.75rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em;
  color: #888; border-bottom: 1px solid #f0f0f0;
}
.parceiros-lista { list-style: none; padding: 6px 0; }
.parceiro-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 16px; cursor: pointer; transition: background 0.12s;
  border-left: 3px solid transparent;
}
.parceiro-item:hover { background: #f5f5f0; }
.parceiro-item.ativo { background: #f0f7f0; border-left-color: #2c5f2e; }
.parceiro-nome { font-size: 0.9rem; font-weight: 500; color: #2c3e50; }
.parceiro-item.ativo .parceiro-nome { color: #2c5f2e; font-weight: 600; }
.parceiro-badge {
  background: #e9ecef; color: #666;
  border-radius: 10px; font-size: 0.72rem; padding: 1px 7px; font-weight: 600;
}
.parceiro-item.ativo .parceiro-badge { background: #c8e6c9; color: #2c5f2e; }

/* Resumo na sidebar */
.sidebar-resumo { border-top: 1px solid #f0f0f0; }
.resumo-item {
  display: flex; flex-direction: column; gap: 2px;
  padding: 10px 16px; border-left: 3px solid transparent;
  border-bottom: 1px solid #f8f8f8;
}
.resumo-destaque { border-left-color: #1565c0; }
.resumo-verde    { border-left-color: #2c5f2e; }
.resumo-label { font-size: 0.72rem; color: #999; text-transform: uppercase; letter-spacing: 0.04em; }
.resumo-valor { font-size: 1.1rem; font-weight: 700; color: #2c3e50; }
.resumo-moeda { font-size: 0.9rem; font-weight: 700; color: #2c5f2e; }

/* Detalhe */
.parceiro-detalhe { flex: 1; min-width: 0; }

.text-muted { color: #aaa; }
</style>
