// Core domain types shared across the app.
// Kept in sync with backend/app/schemas and backend/app/models.

export type UserType = 'founder' | 'engineer' | 'iec_worker' | 'immigrant' | 'admin'
export type UserStatus = 'active' | 'inactive' | 'suspended'

export interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  user_type: UserType
  status: UserStatus
  avatar_url?: string
  bio?: string
  country?: string
  city?: string
  skills?: string[]
  languages?: string[]
  visa_status?: string
  created_at: string
}

export type JobType = 'full_time' | 'part_time' | 'contract' | 'internship'
export type JobStatus = 'draft' | 'open' | 'closed' | 'filled'

export interface Job {
  id: number
  creator_id: number
  title: string
  description: string
  company_name?: string
  salary_min?: number
  salary_max?: number
  salary_currency: string
  skills?: string[]
  experience_level?: string
  job_type: JobType
  status: JobStatus
  location_country?: string
  location_city?: string
  remote_ok: boolean
  visa_sponsorship: boolean
  iec_friendly: boolean
  positions_available: number
  created_at: string
}

export type ApplicationStatus =
  | 'applied'
  | 'reviewing'
  | 'interviewing'
  | 'offered'
  | 'rejected'
  | 'hired'
  | 'withdrawn'

export interface Application {
  id: number
  job_id: number
  user_id: number
  status: ApplicationStatus
  cover_note?: string
  created_at: string
}

export type ContractTemplateType =
  | 'korea_engineer_canada_co'
  | 'canada_engineer_korea_co'
  | 'remote_contractor'
  | 'full_time_domestic'
  | 'part_time_gig'
export type ContractStatus = 'draft' | 'pending_signature' | 'signed' | 'cancelled'

export interface TemplateInfo {
  type: ContractTemplateType
  label: string
  description: string
  required_terms: string[]
}

export interface Contract {
  id: number
  application_id: number
  template_type: ContractTemplateType
  status: ContractStatus
  terms: Record<string, unknown>
  signed_at: string | null
  created_at: string
  job_id: number
  job_title: string
  founder_id: number
  applicant_id: number
}
