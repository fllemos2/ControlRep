<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { matrizes, crias, reprodutores, compradores } from '@/api/client'
import { RouterLink } from 'vue-router'

const counts = ref({ matrizes: 0, crias: 0, reprodutores: 0, compradores: 0 })
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [m, c, r, co] = await Promise.all([
      matrizes.list({ limit: 500 }),
      crias.list({ limit: 500 }),
      reprodutores.list(),
      compradores.list(),
    ])
    counts.value = {
      matrizes: m.data.length,
      crias: c.data.length,
      reprodutores: r.data.length,
      compradores: co.data.length,
    }
  } catch {
    error.value = 'Erro ao carregar dados. Verifique se a API está rodando.'
  } finally {
    loading.value = false
  }
})

const cards = [
  { key: 'matrizes',    label: 'Matrizes',    icon: '🐄', to: '/matrizes',    color: '#2c5f2e' },
  { key: 'crias',       label: 'Crias',        icon: '🐂', to: '/crias',       color: '#1565c0' },
  { key: 'reprodutores',label: 'Reprodutores', icon: '🐃', to: '/reprodutores',color: '#6a1b9a' },
  { key: 'compradores', label: 'Compradores',  icon: '🤝', to: '/compradores', color: '#b76e00' },
]
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Dashboard</h1>
      <span class="subtitle">Visão geral do rebanho</span>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="cards-grid">
      <RouterLink
        v-for="card in cards"
        :key="card.key"
        :to="card.to"
        class="stat-card"
        :style="{ '--accent': card.color }"
      >
        <div class="stat-icon">{{ card.icon }}</div>
        <div class="stat-value">{{ counts[card.key as keyof typeof counts] }}</div>
        <div class="stat-label">{{ card.label }}</div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.subtitle { color: #888; font-size: 0.95rem; }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 28px 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border-top: 4px solid var(--accent);
  transition: transform 0.15s, box-shadow 0.15s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.stat-icon { font-size: 2rem; }
.stat-value { font-size: 2.5rem; font-weight: 700; color: var(--accent); }
.stat-label { font-size: 0.9rem; color: #666; font-weight: 500; }
</style>
