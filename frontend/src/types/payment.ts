// Payment domain types. Kept in sync with backend/app/schemas/payment.py.
// Payments are a ledger only — execute is 501 until Wise is wired.

export type PaymentType = 'salary' | 'contract_payment' | 'remittance'
export type PaymentStatus = 'pending' | 'processing' | 'complete' | 'failed' | 'cancelled'

export interface Payment {
  id: number
  from_user_id: number
  to_user_id: number | null
  amount: number
  currency: string
  payment_type: PaymentType
  status: PaymentStatus
  recipient_name: string | null
  recipient_email: string | null
  notes: string | null
  created_at: string
  from_user_name: string
  to_user_name: string | null
}
