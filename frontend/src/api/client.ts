import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

export interface Matriz {
  id: number
  numero_registro: string
  brinco: string
  nome: string | null
  status: string
  total_crias: number
  raca: string
  parceria: string | null
  primeira_cria_data: string | null
  ultima_cria_data: string | null
  media_dias_intervalo: number | null
  observacoes: string | null
  data_nascimento: string | null
}

export interface Cria {
  id: number
  id_matriz: number
  numero_registro: string | null
  brinco: string | null
  sexo: string | null
  raca_pelagem: string | null
  pai: string | null
  data_nascimento: string
  status: string
  id_comprador: number | null
  valor_venda: number | null
}

export interface Reprodutor {
  id: number
  brinco: string
  nome: string | null
  raca: string
}

export interface Comprador {
  id: number
  nome: string
  telefone: string | null
  cidade: string | null
}

export interface Financeiro {
  total_crias: number
  crias_com_valor: number
  crias_sem_valor: number
  media_nominal: number | null
  media_corrigida: number | null
  total_nominal: number
  total_corrigido: number
  total_estimado: number
  total_geral: number
  idade_media_venda_dias: number | null
  anos_produtivos: number | null
  valor_por_ano: number | null
  data_referencia: string
  ipca_disponivel: boolean
}

export const matrizes = {
  list: (params?: { status?: string; skip?: number; limit?: number }) =>
    api.get<Matriz[]>('/matrizes/', { params }),
  get: (id: number) => api.get<Matriz>(`/matrizes/${id}`),
  financeiro: (id: number) => api.get<Financeiro>(`/matrizes/${id}/financeiro`),
  create: (data: Partial<Matriz>) => api.post<Matriz>('/matrizes/', data),
  update: (id: number, data: Partial<Matriz>) => api.put<Matriz>(`/matrizes/${id}`, data),
  delete: (id: number) => api.delete(`/matrizes/${id}`),
}

export const crias = {
  list: (params?: { id_matriz?: number; sexo?: string; status?: string; sem_venda?: boolean; skip?: number; limit?: number }) =>
    api.get<Cria[]>('/crias/', { params }),
  get: (id: number) => api.get(`/crias/${id}`),
  create: (data: unknown) => api.post('/crias/', data),
  update: (id: number, data: unknown) => api.put(`/crias/${id}`, data),
  delete: (id: number) => api.delete(`/crias/${id}`),
}

export const reprodutores = {
  list: () => api.get<Reprodutor[]>('/reprodutores/'),
}

export const compradores = {
  list: () => api.get<Comprador[]>('/compradores/'),
}

export interface ExameToque {
  id: number
  periodo_inicio: string
  periodo_fim: string
  veterinario: string | null
  data_realizacao: string
}

export interface ToqueMatriz {
  id: number
  id_matriz: number
  id_exame_toque: number
  resultado: string
  dias_estimados_fecundacao: number | null
  observacoes: string | null
}

export const examesToque = {
  list: () => api.get<ExameToque[]>('/exames-toque/'),
  ultimo: () => api.get<ExameToque>('/exames-toque/ultimo'),
  get: (id: number) => api.get<ExameToque>(`/exames-toque/${id}`),
  create: (data: Partial<ExameToque>) => api.post<ExameToque>('/exames-toque/', data),
  update: (id: number, data: Partial<ExameToque>) => api.put<ExameToque>(`/exames-toque/${id}`, data),
  delete: (id: number) => api.delete(`/exames-toque/${id}`),
}

export const toquesMatrizes = {
  list: (params?: { id_matriz?: number; id_exame_toque?: number }) =>
    api.get<ToqueMatriz[]>('/toques-matrizes/', { params }),
  create: (data: Partial<ToqueMatriz>) => api.post<ToqueMatriz>('/toques-matrizes/', data),
  update: (id: number, data: Partial<ToqueMatriz>) => api.put<ToqueMatriz>(`/toques-matrizes/${id}`, data),
  delete: (id: number) => api.delete(`/toques-matrizes/${id}`),
}

export interface SyncStatus {
  type: string
  last_modified?: number
  last_modified_iso?: string
  size_bytes?: number
  cloud_configured: boolean
}

export const sync = {
  status: () => api.get<SyncStatus>('/sync/status'),
  push:   () => api.post<{ status: string; pushed_bytes: number }>('/sync/push'),
  pull:   () => api.post<{ status: string; pulled_bytes: number }>('/sync/pull'),
}

export interface MatrizResumo {
  id: number
  numero_registro: string
  brinco: string
  status: string
  total_crias: number
  crias_no_pasto: number
  valor_vendido: number
}

export interface ParceriaResumo {
  nome: string
  matrizes: MatrizResumo[]
  total_matrizes: number
  total_crias: number
  total_crias_no_pasto: number
  total_valor_vendido: number
}

export const parcerias = {
  resumo: () => api.get<ParceriaResumo[]>('/parcerias/resumo'),
}

export interface DashboardStats {
  matrizes: { ativas: number; cheias: number; vazias: number; paridas: number }
  crias: { no_pasto: number; idade_media_meses: number; machos: number; femeas: number } // campo renomeado em backend para anos, mas mantemos compatibilidade
}

export const dashboard = {
  stats: () => api.get<DashboardStats>('/dashboard/'),
}

export interface ChatAction {
  type: string
  label: string
  payload: Record<string, unknown>
}

export interface ChatResponse {
  message: string
  actions: ChatAction[]
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export const chat = {
  send: (message: string, history: ChatMessage[] = []) =>
    api.post<ChatResponse>('/chat/', { message, history }),
  execute: (actions: ChatAction[]) =>
    api.post<{ results: string[] }>('/chat/execute', { actions }),
}

export default api
