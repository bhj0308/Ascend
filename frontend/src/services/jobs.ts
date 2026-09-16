import { api } from './api'
import type { Job } from '@/types'

export interface JobFilters {
  location_country?: string
  remote_ok?: boolean
  visa_sponsorship?: boolean
  iec_friendly?: boolean
}

export async function browseJobs(filters: JobFilters = {}): Promise<Job[]> {
  const { data } = await api.get<Job[]>('/jobs', { params: filters })
  return data
}

export async function getJob(id: number): Promise<Job> {
  const { data } = await api.get<Job>(`/jobs/${id}`)
  return data
}

export async function createJob(payload: Partial<Job>): Promise<Job> {
  const { data } = await api.post<Job>('/jobs', payload)
  return data
}

export async function applyToJob(jobId: number, coverNote?: string) {
  const { data } = await api.post('/applications', { job_id: jobId, cover_note: coverNote })
  return data
}
