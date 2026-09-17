// Mentorship domain types.
// Kept in sync with backend/app/schemas and backend/app/models.

export type MentorshipStatus = 'requested' | 'active' | 'completed' | 'declined'

export interface Mentorship {
  id: number
  mentor_id: number
  mentee_id: number
  status: MentorshipStatus
  notes: string | null
  created_at: string
  mentor_name: string
  mentee_name: string
}
