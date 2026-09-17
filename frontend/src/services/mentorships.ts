import { api } from './api'
import type { Mentorship } from '@/types/mentorship'

export async function getMyMentorships(): Promise<Mentorship[]> {
  const { data } = await api.get<Mentorship[]>('/mentorships/me')
  return data
}

export interface RequestMentorshipPayload {
  mentor_id: number
  notes?: string
}

export async function requestMentorship(payload: RequestMentorshipPayload): Promise<Mentorship> {
  const { data } = await api.post<Mentorship>('/mentorships', payload)
  return data
}

export async function acceptMentorship(id: number): Promise<Mentorship> {
  const { data } = await api.post<Mentorship>(`/mentorships/${id}/accept`)
  return data
}

export async function declineMentorship(id: number): Promise<Mentorship> {
  const { data } = await api.post<Mentorship>(`/mentorships/${id}/decline`)
  return data
}

export async function completeMentorship(id: number): Promise<Mentorship> {
  const { data } = await api.post<Mentorship>(`/mentorships/${id}/complete`)
  return data
}
