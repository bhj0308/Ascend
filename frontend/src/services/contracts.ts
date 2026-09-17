import { api } from './api'
import type { Contract, ContractTemplateType, TemplateInfo } from '@/types'

export async function getTemplates(): Promise<TemplateInfo[]> {
  const { data } = await api.get<TemplateInfo[]>('/contracts/templates')
  return data
}

export async function getMyContracts(): Promise<Contract[]> {
  const { data } = await api.get<Contract[]>('/contracts/me')
  return data
}

export interface CreateContractPayload {
  application_id: number
  template_type: ContractTemplateType
  terms: Record<string, unknown>
}

export async function createContract(payload: CreateContractPayload): Promise<Contract> {
  const { data } = await api.post<Contract>('/contracts', payload)
  return data
}

export async function getContract(id: number): Promise<Contract> {
  const { data } = await api.get<Contract>(`/contracts/${id}`)
  return data
}

export async function updateContractTerms(
  id: number,
  terms: Record<string, unknown>
): Promise<Contract> {
  const { data } = await api.put<Contract>(`/contracts/${id}`, { terms })
  return data
}

export async function sendContract(id: number): Promise<Contract> {
  const { data } = await api.post<Contract>(`/contracts/${id}/send`)
  return data
}

export async function signContract(id: number): Promise<Contract> {
  const { data } = await api.post<Contract>(`/contracts/${id}/sign`)
  return data
}

export async function cancelContract(id: number): Promise<Contract> {
  const { data } = await api.post<Contract>(`/contracts/${id}/cancel`)
  return data
}
