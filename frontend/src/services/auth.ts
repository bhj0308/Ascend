import { api } from './api'
import type { User, UserType } from '@/types'

export interface SignupPayload {
  email: string
  password: string
  first_name?: string
  last_name?: string
  user_type: UserType
  country?: string
  city?: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export async function signup(payload: SignupPayload): Promise<User> {
  const { data } = await api.post<User>('/auth/signup', payload)
  return data
}

export async function login(email: string, password: string): Promise<Token> {
  const { data } = await api.post<Token>('/auth/login', { email, password })
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
  return data
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/auth/me')
  return data
}
