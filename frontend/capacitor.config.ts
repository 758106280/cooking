import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.cooking.assistant',
  appName: '做饭助手',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    // 家用局域网可能使用 http://192.168.x.x:8000；正式公网部署仍建议使用 HTTPS。
    cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
    },
  },
}

export default config
