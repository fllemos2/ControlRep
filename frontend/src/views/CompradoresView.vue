<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { compradores, type Comprador } from '@/api/client'

const lista = ref<Comprador[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    lista.value = (await compradores.list()).data
  } catch {
    error.value = 'Erro ao carregar compradores.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Compradores <span class="count">({{ lista.length }})</span></h1>
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="loading" class="loading">Carregando...</div>

    <div v-else class="card">
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Nome</th>
              <th>Telefone</th>
              <th>Cidade</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in lista" :key="c.id">
              <td><strong>{{ c.nome }}</strong></td>
              <td>{{ c.telefone ?? '—' }}</td>
              <td>{{ c.cidade ?? '—' }}</td>
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
