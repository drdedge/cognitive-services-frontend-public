import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Usage from '@/views/Usage.vue'
import DocumentIntelligence from '@/views/DocumentIntelligence.vue'
import Translation from '@/views/Translation.vue'
import Transcription from '@/views/Transcription.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/usage',
    name: 'Usage',
    component: Usage,
  },
  {
    path: '/document-intelligence',
    name: 'DocumentIntelligence',
    component: DocumentIntelligence,
  },
  {
    path: '/translation',
    name: 'Translation',
    component: Translation,
  },
  {
    path: '/transcription',
    name: 'Transcription',
    component: Transcription,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router