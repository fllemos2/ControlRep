<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { dashboard, type DashboardStats } from '@/api/client'
import { RouterLink } from 'vue-router'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await dashboard.stats()
    stats.value = data
  } catch {
    error.value = 'Erro ao carregar dados.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Dashboard</h1>
      <span class="subtitle">Visão geral do rebanho</span>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else-if="stats" class="cards-grid">

      <!-- Matrizes -->
      <RouterLink to="/matrizes" class="stat-card" style="--accent: #2c5f2e">
        <div class="card-top">
          <span class="card-icon">🐄</span>
          <span class="card-label">Matrizes</span>
        </div>
        <div class="card-value">{{ stats.matrizes.ativas }}</div>
        <div class="card-sub">Ativas</div>
        <div class="card-breakdown">
          <div class="breakdown-item">
            <span class="dot dot-green"></span>
            <span class="breakdown-label">Cheias</span>
            <span class="breakdown-val">{{ stats.matrizes.cheias }}</span>
          </div>
          <div class="breakdown-item">
            <span class="dot dot-red"></span>
            <span class="breakdown-label">Vazias</span>
            <span class="breakdown-val">{{ stats.matrizes.vazias }}</span>
          </div>
          <div class="breakdown-item">
            <span class="dot dot-blue"></span>
            <span class="breakdown-label">Paridas</span>
            <span class="breakdown-val">{{ stats.matrizes.paridas }}</span>
          </div>
        </div>
      </RouterLink>

      <!-- Crias -->
      <RouterLink to="/crias" class="stat-card" style="--accent: #1565c0">
        <div class="card-top">
          <span class="card-icon">🐂</span>
          <span class="card-label">Crias</span>
        </div>
        <div class="card-value">{{ stats.crias.no_pasto }}</div>
        <div class="card-sub">No Pasto</div>
        <div class="card-breakdown">
          <div class="breakdown-item">
            <span class="dot dot-blue"></span>
            <span class="breakdown-label">Machos</span>
            <span class="breakdown-val">{{ stats.crias.machos }}</span>
          </div>
          <div class="breakdown-item">
            <span class="dot dot-pink"></span>
            <span class="breakdown-label">Fêmeas</span>
            <span class="breakdown-val">{{ stats.crias.femeas }}</span>
          </div>
          <div class="breakdown-item age-item">
            <span class="breakdown-label">Idade média</span>
            <span class="breakdown-val">{{ stats.crias.idade_media_meses }} m</span>
          </div>
        </div>
      </RouterLink>

    </div>
  </div>
</template>

<style scoped>
.subtitle { color: #888; font-size: 0.95rem; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-top: 4px solid var(--accent);
  transition: transform 0.15s, box-shadow 0.15s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.card-icon { font-size: 1.4rem; }
.card-label { font-size: 0.85rem; font-weight: 600; color: #888; text-transform: uppercase; letter-spacing: 0.05em; }

.card-value { font-size: 3rem; font-weight: 700; color: var(--accent); line-height: 1; }
.card-sub { font-size: 0.82rem; color: #999; margin-bottom: 16px; }

.card-breakdown {
  border-top: 1px solid #f0f0f0;
  padding-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breakdown-label { font-size: 0.85rem; color: #555; flex: 1; }
.breakdown-val { font-size: 0.9rem; font-weight: 600; color: #333; }

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-green { background: #2c5f2e; }
.dot-red   { background: #c62828; }
.dot-blue  { background: #1565c0; }
.dot-pink  { background: #880e4f; }

.age-item .breakdown-label { color: #888; }
</style>
