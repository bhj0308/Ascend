import { api } from './api'
import type { Job, User } from '@/types'

export async function listUsers(q?: string): Promise<User[]> {
  const { data } = await api.get<User[]>('/admin/users', { params: q ? { q } : {} })
  return data
}

export async function suspendUser(userId: number): Promise<User> {
  const { data } = await api.post<User>(`/admin/users/${userId}/suspend`)
  return data
}

export async function unsuspendUser(userId: number): Promise<User> {
  const { data } = await api.post<User>(`/admin/users/${userId}/unsuspend`)
  return data
}

export async function listAllJobs(q?: string): Promise<Job[]> {
  const { data } = await api.get<Job[]>('/admin/jobs', { params: q ? { q } : {} })
  return data
}

export async function closeJob(jobId: number): Promise<Job> {
  const { data } = await api.post<Job>(`/admin/jobs/${jobId}/close`)
  return data
}
