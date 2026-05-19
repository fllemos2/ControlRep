<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import ChatFooter from '@/components/ChatFooter.vue'
import { sync } from '@/api/client'

const cloudOk = ref(false)
const syncing  = ref(false)
const syncMsg  = ref('')

onMounted(async () => {
  try {
    const { data } = await sync.status()
    cloudOk.value = data.cloud_configured
  } catch { /* sem sync — silencioso */ }
})

async function doSync(dir: 'push' | 'pull') {
  syncing.value = true
  syncMsg.value = ''
  try {
    const { data } = dir === 'push' ? await sync.push() : await sync.pull()
    const bytes = 'pushed_bytes' in data ? data.pushed_bytes : (data as { pulled_bytes: number }).pulled_bytes
    const kb = (bytes / 1024).toFixed(0)
    syncMsg.value = dir === 'push' ? `Enviado (${kb} KB)` : `Recebido (${kb} KB)`
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    syncMsg.value = `Erro: ${detail ?? 'falha na sincronização'}`
  } finally {
    syncing.value = false
    setTimeout(() => { syncMsg.value = '' }, 4000)
  }
}
</script>

<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">🐄 Cattle Control</div>
      <div class="nav-links">
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/matrizes">Matrizes</RouterLink>
        <RouterLink to="/crias">Crias</RouterLink>
        <RouterLink to="/exames-toque">Toque</RouterLink>
        <RouterLink to="/parcerias">Parcerias</RouterLink>
      </div>
      <div v-if="cloudOk" class="sync-area">
        <span v-if="syncMsg" class="sync-msg" :class="syncMsg.startsWith('Erro') ? 'sync-err' : 'sync-ok'">
          {{ syncMsg }}
        </span>
        <button class="sync-btn" @click="doSync('pull')" :disabled="syncing" title="Baixar dados da nuvem">
          {{ syncing ? '…' : '⬇ Pull' }}
        </button>
        <button class="sync-btn" @click="doSync('push')" :disabled="syncing" title="Enviar dados para a nuvem">
          {{ syncing ? '…' : '⬆ Push' }}
        </button>
      </div>
    </nav>
    <main class="main-content">
      <RouterView />
    </main>
    <ChatFooter />
  </div>
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }

#app { display: block; width: 100%; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f5f0;
  color: #2c3e50;
}

.navbar {
  background: #2c5f2e;
  color: white;
  padding: 0 24px;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.nav-brand { font-size: 1.1rem; font-weight: 700; white-space: nowrap; }

.nav-links { display: flex; gap: 4px; flex-wrap: wrap; }

.nav-links a {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: background 0.15s, color 0.15s;
}

.nav-links a:hover,
.nav-links a.router-link-active { background: rgba(255,255,255,0.15); color: white; }

.main-content { max-width: 1440px; margin: 0 auto; padding: 32px 24px; }

.card { background: white; border-radius: 10px; padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }

.table-wrapper { overflow-x: auto; }

table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }

th {
  background: #f8f9fa;
  padding: 10px 14px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
}

td { padding: 10px 14px; border-bottom: 1px solid #f0f0f0; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }

.badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 500; }
.badge-green { background: #e6f4ea; color: #2c5f2e; }
.badge-gray  { background: #f0f0f0; color: #666; }
.badge-blue  { background: #e3f2fd; color: #1565c0; }
.badge-red   { background: #fde8e8; color: #c62828; }

.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.15s;
  text-decoration: none;
}
.btn:hover { opacity: 0.85; }
.btn-primary { background: #2c5f2e; color: white; }
.btn-ghost   { background: transparent; border: 1px solid #ddd; color: #444; }

.loading { text-align: center; padding: 48px; color: #888; }
.error-msg { color: #c62828; padding: 16px; background: #fde8e8; border-radius: 8px; margin-bottom: 16px; }

.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }
.page-header h1 { font-size: 1.5rem; font-weight: 700; }

.filters { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }
.filters select,
.filters input {
  padding: 7px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.875rem;
  outline: none;
}
.filters select:focus,
.filters input:focus { border-color: #2c5f2e; }

/* Sync */
.sync-area { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.sync-btn {
  padding: 4px 12px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.12); color: white; font-size: 0.8rem;
  cursor: pointer; white-space: nowrap; transition: background 0.15s;
}
.sync-btn:hover:not(:disabled) { background: rgba(255,255,255,0.25); }
.sync-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.sync-msg { font-size: 0.78rem; white-space: nowrap; }
.sync-ok  { color: #a5d6a7; }
.sync-err { color: #ef9a9a; }
</style>
