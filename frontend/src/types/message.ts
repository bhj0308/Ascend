// Message domain types.
// Kept in sync with backend/app/schemas/message.py.

export interface Message {
  id: number
  sender_id: number
  recipient_id: number
  job_id: number | null
  body: string
  read: boolean
  created_at: string
}

export interface ThreadSummary {
  user_id: number
  user_name: string
  last_message_body: string
  last_message_at: string
  unread_count: number
}
