import { api } from './api'
import type { User } from '@/types'

export async function getProfile(userId: number): Promise<User> {
  const { data } = await api.get<User>(`/profile/${userId}`)
  return data
}
