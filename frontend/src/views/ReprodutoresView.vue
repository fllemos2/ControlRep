<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reprodutores, type Reprodutor } from '@/api/client'

const lista = ref<Reprodutor[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    lista.value = (await reprodutores.list()).data
  } catch {
    error.value = 'Erro ao carregar reprodutores.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Reprodutores <span class="count">({{ lista.length }})</span></h1>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Brinco</th>
              <th>Nome</th>
              <th>Raça</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in lista" :key="r.id">
              <td><strong>{{ r.brinco }}</strong></td>
              <td>{{ r.nome ?? '—' }}</td>
              <td><span class="badge badge-green">{{ r.raca }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.count { font-size: 1rem; font-weight: 400; color: #888; }
</style>
