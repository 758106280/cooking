import { createApp } from 'vue'

import App from './App.vue'
import { router } from './router'
import './style.css'
import { initializeNativePlatform } from './platform'

initializeNativePlatform()
createApp(App).use(router).mount('#app')
