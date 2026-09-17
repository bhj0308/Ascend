import { api } from './api'
import type { PublicUser } from '@/types'

export async function getProfile(userId: number): Promise<PublicUser> {
  const { data } = await api.get<PublicUser>(`/profile/${userId}`)
  return data
}
