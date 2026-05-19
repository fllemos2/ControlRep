<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import api from '@/api/client'

interface ActionItem {
  type: string
  label: string
  payload: Record<string, unknown>
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  actions?: ActionItem[]
  executedResults?: string[]
}

const open = ref(false)
const input = ref('')
const sending = ref(false)
const executing = ref(false)
const messages = ref<Message[]>([])
const bodyRef = ref<HTMLElement | null>(null)

function toggle() { open.value = !open.value }

function scrollBottom() {
  nextTick(() => {
    if (bodyRef.value) bodyRef.value.scrollTop = bodyRef.value.scrollHeight
  })
}

watch(messages, scrollBottom, { deep: true })

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  input.value = ''

  messages.value.push({ role: 'user', content: text })
  sending.value = true

  try {
    const history = messages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }))
    const res = await api.post('/api/v1/chat/', { message: text, history })
    const data = res.data
    messages.value.push({
      role: 'assistant',
      content: data.message,
      actions: data.actions?.length ? data.actions : undefined,
    })
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    messages.value.push({
      role: 'assistant',
      content: `⚠ Erro: ${detail ?? 'Não foi possível conectar ao assistente.'}`,
    })
  } finally {
    sending.value = false
  }
}

async function executeActions(msg: Message) {
  if (!msg.actions?.length) return
  executing.value = true
  try {
    const res = await api.post('/api/v1/chat/execute', { actions: msg.actions })
    msg.executedResults = res.data.results
    msg.actions = undefined
  } catch {
    msg.executedResults = ['Erro ao executar as ações.']
  } finally {
    executing.value = false
  }
}

function cancelActions(msg: Message) {
  msg.actions = undefined
  messages.value.push({ role: 'assistant', content: 'Ok, ações canceladas.' })
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
}
</script>

<template>
  <!-- Botão flutuante -->
  <button class="chat-fab" @click="toggle" :title="open ? 'Fechar chat' : 'Assistente IA'">
    <span v-if="!open">💬</span>
    <span v-else>✕</span>
  </button>

  <!-- Painel de chat -->
  <Transition name="chat-slide">
    <div v-if="open" class="chat-panel">
      <div class="chat-header">
        <span class="chat-title">🐄 Assistente Cattle Control</span>
        <button class="chat-close" @click="toggle">✕</button>
      </div>

      <div class="chat-body" ref="bodyRef">
        <div v-if="messages.length === 0" class="chat-empty">
          Olá! Pergunte sobre o rebanho, solicite registros de toque ou cria.<br>
          <small>Ex.: "Quais matrizes têm parto previsto este mês?" ou "Registra o toque da 860 como Cheia com 45 dias"</small>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-msg"
          :class="msg.role === 'user' ? 'msg-user' : 'msg-assistant'"
        >
          <div class="msg-bubble">{{ msg.content }}</div>

          <!-- Ações pendentes de confirmação -->
          <div v-if="msg.actions?.length" class="actions-block">
            <div class="actions-title">📋 Ações a confirmar:</div>
            <ul class="actions-list">
              <li v-for="(a, ai) in msg.actions" :key="ai">{{ a.label }}</li>
            </ul>
            <div class="actions-btns">
              <button class="btn-confirmar" @click="executeActions(msg)" :disabled="executing">
                {{ executing ? 'Executando…' : '✓ Confirmar' }}
              </button>
              <button class="btn-cancelar" @click="cancelActions(msg)" :disabled="executing">
                ✕ Cancelar
              </button>
            </div>
          </div>

          <!-- Resultados da execução -->
          <div v-if="msg.executedResults?.length" class="results-block">
            <div v-for="(r, ri) in msg.executedResults" :key="ri" class="result-line">
              {{ r.startsWith('ERRO') ? '❌' : '✅' }} {{ r }}
            </div>
          </div>
        </div>

        <div v-if="sending" class="chat-msg msg-assistant">
          <div class="msg-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-footer-input">
        <textarea
          v-model="input"
          class="chat-input"
          placeholder="Digite sua pergunta ou instrução…"
          rows="2"
          @keydown="onKey"
        ></textarea>
        <button class="chat-send" @click="send" :disabled="sending || !input.trim()">
          ➤
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Botão flutuante */
.chat-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #2c5f2e;
  color: white;
  font-size: 1.4rem;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, transform 0.15s;
}
.chat-fab:hover { background: #1b4020; transform: scale(1.07); }

/* Painel */
.chat-panel {
  position: fixed;
  bottom: 88px;
  right: 24px;
  width: 400px;
  max-width: calc(100vw - 48px);
  height: 520px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 8px 40px rgba(0,0,0,0.22);
  display: flex;
  flex-direction: column;
  z-index: 499;
  overflow: hidden;
}

.chat-header {
  background: #2c5f2e;
  color: white;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.chat-title { font-size: 0.9rem; font-weight: 600; }
.chat-close {
  background: none; border: none; color: rgba(255,255,255,0.8);
  font-size: 1rem; cursor: pointer; padding: 2px 6px; border-radius: 4px;
}
.chat-close:hover { background: rgba(255,255,255,0.15); }

.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-empty {
  color: #aaa;
  font-size: 0.85rem;
  text-align: center;
  margin: auto;
  line-height: 1.6;
}
.chat-empty small { color: #bbb; }

.chat-msg { display: flex; flex-direction: column; max-width: 92%; }
.msg-user { align-self: flex-end; align-items: flex-end; }
.msg-assistant { align-self: flex-start; align-items: flex-start; }

.msg-bubble {
  padding: 9px 13px;
  border-radius: 12px;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
}
.msg-user .msg-bubble { background: #2c5f2e; color: white; border-bottom-right-radius: 3px; }
.msg-assistant .msg-bubble { background: #f0f4f0; color: #2c3e50; border-bottom-left-radius: 3px; }

/* Typing dots */
.typing { display: flex; gap: 4px; padding: 12px 16px; }
.typing span {
  width: 7px; height: 7px; border-radius: 50%;
  background: #aaa; animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* Ações */
.actions-block {
  margin-top: 8px;
  background: #fff8e1;
  border: 1px solid #ffe082;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.82rem;
}
.actions-title { font-weight: 700; color: #e65100; margin-bottom: 6px; }
.actions-list { margin: 0 0 10px 16px; color: #555; }
.actions-list li { margin-bottom: 3px; }
.actions-btns { display: flex; gap: 8px; }
.btn-confirmar {
  padding: 5px 14px; border-radius: 6px; border: none;
  background: #2c5f2e; color: white; font-size: 0.8rem;
  cursor: pointer; font-weight: 600;
}
.btn-confirmar:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancelar {
  padding: 5px 14px; border-radius: 6px;
  border: 1px solid #ccc; background: white;
  color: #666; font-size: 0.8rem; cursor: pointer;
}

/* Resultados */
.results-block {
  margin-top: 8px;
  background: #f1f8e9;
  border: 1px solid #c5e1a5;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.82rem;
}
.result-line { padding: 2px 0; color: #444; }

/* Input */
.chat-footer-input {
  border-top: 1px solid #f0f0f0;
  padding: 10px 12px;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
.chat-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 0.875rem;
  font-family: inherit;
  resize: none;
  outline: none;
  line-height: 1.4;
}
.chat-input:focus { border-color: #2c5f2e; }
.chat-send {
  width: 38px; height: 38px;
  border-radius: 8px;
  background: #2c5f2e; color: white;
  border: none; cursor: pointer;
  font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.chat-send:disabled { opacity: 0.4; cursor: not-allowed; }
.chat-send:not(:disabled):hover { background: #1b4020; }

/* Transição */
.chat-slide-enter-active,
.chat-slide-leave-active { transition: opacity 0.2s, transform 0.2s; }
.chat-slide-enter-from,
.chat-slide-leave-to { opacity: 0; transform: translateY(16px) scale(0.97); }
</style>
