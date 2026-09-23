import { App } from '@capacitor/app'
import { Capacitor } from '@capacitor/core'
import { Preferences } from '@capacitor/preferences'
import { SplashScreen } from '@capacitor/splash-screen'
import { StatusBar, Style } from '@capacitor/status-bar'

export const isNativePlatform = Capacitor.isNativePlatform()
const API_BASE_URL_KEY = 'cooking_api_base_url'
const AUTH_TOKEN_KEY = 'cooking_access_token'
const buildTimeApiBaseUrl = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL ?? '')

function getBrowserApiBaseUrl() {
  try {
    return localStorage.getItem(API_BASE_URL_KEY) ?? ''
  } catch {
    return ''
  }
}

function setBrowserApiBaseUrl(value: string) {
  try {
    localStorage.setItem(API_BASE_URL_KEY, value)
  } catch {
    // Private browsing can disable localStorage. The build-time URL remains usable.
  }
}

export function normalizeApiBaseUrl(value: string) {
  const normalized = value.trim().replace(/\/+$/, '')
  if (!normalized) return ''

  let parsed: URL
  try {
    parsed = new URL(normalized)
  } catch {
    throw new Error('请输入完整地址，例如 http://192.168.1.100:8000')
  }
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error('服务地址必须使用 http 或 https')
  }
  return normalized
}

export async function getApiBaseUrl() {
  const savedValue = isNativePlatform
    ? (await Preferences.get({ key: API_BASE_URL_KEY })).value ?? ''
    : getBrowserApiBaseUrl()
  return normalizeApiBaseUrl(savedValue) || buildTimeApiBaseUrl
}

export async function setApiBaseUrl(value: string) {
  const normalized = normalizeApiBaseUrl(value)
  if (!normalized) throw new Error('服务地址不能为空')

  if (isNativePlatform) {
    await Preferences.set({ key: API_BASE_URL_KEY, value: normalized })
  } else {
    setBrowserApiBaseUrl(normalized)
  }
  return normalized
}

export async function clearApiBaseUrl() {
  if (isNativePlatform) {
    await Preferences.remove({ key: API_BASE_URL_KEY })
  } else {
    try {
      localStorage.removeItem(API_BASE_URL_KEY)
    } catch {
      // Ignore unavailable browser storage.
    }
  }
}

export async function getAuthToken() {
  if (!isNativePlatform) return ''
  return (await Preferences.get({ key: AUTH_TOKEN_KEY })).value ?? ''
}

export async function setAuthToken(value: string) {
  if (!isNativePlatform) return
  await Preferences.set({ key: AUTH_TOKEN_KEY, value })
}

export async function clearAuthToken() {
  if (!isNativePlatform) return
  await Preferences.remove({ key: AUTH_TOKEN_KEY })
}

export async function initializeNativePlatform() {
  if (!isNativePlatform) return

  await Promise.allSettled([
    StatusBar.setStyle({ style: Style.Light }),
    SplashScreen.hide(),
  ])

  App.addListener('appUrlOpen', ({ url }) => {
    const parsedUrl = new URL(url)
    const path = `${parsedUrl.pathname}${parsedUrl.search}${parsedUrl.hash}`
    if (path && path !== '/') window.location.href = path
  })
}
