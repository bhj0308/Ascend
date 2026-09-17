import { api } from './api'
import type { Payment, PaymentType } from '@/types/payment'

export async function getMyPayments(): Promise<Payment[]> {
  const { data } = await api.get<Payment[]>('/payments/me')
  return data
}

export async function getPayment(id: number): Promise<Payment> {
  const { data } = await api.get<Payment>(`/payments/${id}`)
  return data
}

export interface CreatePaymentPayload {
  to_user_id?: number
  recipient_email?: string
  recipient_name?: string
  amount: number
  currency: string
  payment_type: PaymentType
  notes?: string
}

export async function createPayment(payload: CreatePaymentPayload): Promise<Payment> {
  const { data } = await api.post<Payment>('/payments', payload)
  return data
}

export async function cancelPayment(id: number): Promise<Payment> {
  const { data } = await api.post<Payment>(`/payments/${id}/cancel`)
  return data
}
