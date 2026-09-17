import { api } from './api'
import type { Message, ThreadSummary } from '@/types/message'

export async function getThreads(): Promise<ThreadSummary[]> {
  const { data } = await api.get<ThreadSummary[]>('/messages/threads')
  return data
}

export async function getThread(userId: number): Promise<Message[]> {
  const { data } = await api.get<Message[]>(`/messages/with/${userId}`)
  return data
}

export interface SendMessagePayload {
  recipient_id: number
  body: string
  job_id?: number
}

export async function sendMessage(payload: SendMessagePayload): Promise<Message> {
  const { data } = await api.post<Message>('/messages', payload)
  return data
}
