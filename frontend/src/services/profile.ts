import { api } from './api'
import type { PublicUser, User } from '@/types'

export async function getProfile(userId: number): Promise<PublicUser> {
  const { data } = await api.get<PublicUser>(`/profile/${userId}`)
  return data
}

export async function getMyProfile(): Promise<User> {
  const { data } = await api.get<User>('/profile/me')
  return data
}

export interface UpdateProfilePayload {
  first_name?: string
  last_name?: string
  bio?: string
  avatar_url?: string
  country?: string
  city?: string
  phone?: string
  skills?: string[]
  languages?: string[]
  timezone?: string
  visa_status?: string
  mentor_available?: boolean
}

export async function updateProfile(payload: UpdateProfilePayload): Promise<User> {
  const { data } = await api.put<User>('/profile/me', payload)
  return data
}

export async function deleteAccount(password: string): Promise<void> {
  await api.delete('/profile/me', { data: { password } })
}
