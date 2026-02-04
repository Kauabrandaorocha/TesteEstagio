import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(router) // Avisa ao Vue para usar o Router
app.mount('#app')