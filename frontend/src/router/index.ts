import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import ListaOperadoras from '../views/ListaOperadoras.vue'
import DetalheOperadora from '../views/DetalheOperadora.vue'

const routes: Array<RouteRecordRaw> = [
  { path: '/', name: 'Lista', component: ListaOperadoras },
  { path: '/operadora/:cnpj', name: 'Detalhe', component: DetalheOperadora, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router