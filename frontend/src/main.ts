import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import './themes.css'
import App from './App.vue'
import { initializeSharedSession, sharedUser } from './stores/sharedSession'
import { initializePwa } from './pwa'
import { initializeAppearance } from './stores/appearance'

const app = createApp(App)
initializeAppearance()
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Resolve account identity before any store loads private data or opens SSE.
initializeSharedSession().then(async (ready) => {
  if (ready) {
    await router.isReady()
    app.mount('#app')
    if (!sharedUser.value) initializePwa()
  }
})
