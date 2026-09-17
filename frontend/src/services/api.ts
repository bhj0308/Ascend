import axios, { type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
})

// Attach the access token to every outgoing request, if present.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// --- Refresh-once-then-retry on 401 -----------------------------------------
// Access tokens are short-lived (30 min). When one expires we exchange the
// refresh token for a new pair and replay the original request exactly once.
// A separate bare client is used for the refresh call so it never re-enters
// this interceptor.

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean }

const bare = axios.create({ baseURL: API_URL })
let refreshInFlight: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) return null
  try {
    const { data } = await bare.post<{ access_token: string; refresh_token: string }>(
      '/auth/refresh',
      { refresh_token: refreshToken }
    )
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data.access_token
  } catch {
    return null
  }
}

export function clearSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  useAuthStore.getState().clear()
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as RetriableConfig | undefined
    const url = original?.url ?? ''
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/refresh')

    if (error.response?.status !== 401 || !original || original._retried || isAuthEndpoint) {
      return Promise.reject(error)
    }

    original._retried = true
    // Coalesce concurrent 401s into a single refresh call.
    refreshInFlight = refreshInFlight ?? refreshAccessToken().finally(() => {
      refreshInFlight = null
    })
    const token = await refreshInFlight

    if (!token) {
      clearSession()
      return Promise.reject(error)
    }

    original.headers.Authorization = `Bearer ${token}`
    return api(original)
  }
)
