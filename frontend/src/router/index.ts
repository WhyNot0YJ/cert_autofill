import { createRouter, createWebHistory } from 'vue-router'
import MVP from '../views/MVP.vue'
import TemplateManager from '../views/TemplateManager.vue'
import ApplicationManager from '../views/ApplicationManager.vue'
import CompanyManagement from '../views/CompanyManagement.vue'

const routes = [
  {
    path: '/',
    name: 'MVP',
    component: MVP
  },
  {
    path: '/templates',
    name: 'TemplateManager',
    component: TemplateManager
  },
  {
    path: '/applications',
    name: 'ApplicationManager',
    component: ApplicationManager
  },
  {
    path: '/companies',
    name: 'CompanyManagement',
    component: CompanyManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 