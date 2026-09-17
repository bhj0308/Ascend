import { api } from './api'
import type { Application } from '@/types'

export async function getJobApplications(jobId: number): Promise<Application[]> {
  const { data } = await api.get<Application[]>(`/applications/job/${jobId}`)
  return data
}
