import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/matrizes', name: 'matrizes', component: () => import('@/views/MatrizesView.vue') },
    { path: '/matrizes/:id', name: 'matriz-detail', component: () => import('@/views/MatrizDetailView.vue') },
    { path: '/crias', name: 'crias', component: () => import('@/views/CriasView.vue') },
    { path: '/exames-toque', name: 'exames-toque', component: () => import('@/views/ExamesToqueView.vue') },
  ],
})

export default router
