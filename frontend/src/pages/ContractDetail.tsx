import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  cancelContract,
  getContract,
  getTemplates,
  sendContract,
  signContract,
  updateContractTerms,
} from '@/services/contracts'
import { PayUserButton } from '@/components/PayUserButton'
import { useAuthStore } from '@/store/authStore'
import { formatDateOnly } from '@/utils/dates'
import { formatCents, isMoneyTerm, isNumericTerm } from '@/utils/money'
import type { ContractStatus } from '@/types'

const STATUS_STYLES: Record<ContractStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  pending_signature: 'bg-yellow-100 text-yellow-700',
  signed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

function formatTermValue(term: string, value: unknown, currency: string): string {
  if (isMoneyTerm(term) && typeof value === 'number') return formatCents(value, currency)
  if (term.endsWith('_date') && typeof value === 'string' && value) {
    return formatDateOnly(value)
  }
  return String(value ?? '')
}

export function ContractDetail() {
  const { id } = useParams<{ id: string }>()
  const contractId = Number(id)
  const user = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const [editValues, setEditValues] = useState<Record<string, string>>({})

  const {
    data: contract,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['contract', contractId],
    queryFn: () => getContract(contractId),
    enabled: !Number.isNaN(contractId),
  })

  const { data: templates } = useQuery({
    queryKey: ['contract-templates'],
    queryFn: getTemplates,
  })

  const template = templates?.find((t) => t.type === contract?.template_type)

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['contract', contractId] })

  const sendMutation = useMutation({ mutationFn: () => sendContract(contractId), onSuccess: invalidate })
  const signMutation = useMutation({ mutationFn: () => signContract(contractId), onSuccess: invalidate })
  const cancelMutation = useMutation({ mutationFn: () => cancelContract(contractId), onSuccess: invalidate })
  const saveMutation = useMutation({
    mutationFn: () => {
      const terms: Record<string, unknown> = {}
      for (const term of template?.required_terms || []) {
        const raw = editValues[term] || ''
        terms[term] = isMoneyTerm(term)
          ? Math.round(parseFloat(raw || '0') * 100)
          : isNumericTerm(term)
            ? Number(raw)
            : raw
      }
      return updateContractTerms(contractId, terms)
    },
    onSuccess: () => {
      setEditing(false)
      invalidate()
    },
  })

  const startEditing = () => {
    if (!contract) return
    const values: Record<string, string> = {}
    for (const term of template?.required_terms || []) {
      const value = contract.terms[term]
      values[term] = isMoneyTerm(term) && typeof value === 'number' ? String(value / 100) : String(value ?? '')
    }
    setEditValues(values)
    setEditing(true)
  }

  if (isLoading) return <p className="mx-auto max-w-2xl px-4 py-10 text-gray-500">Loading…</p>

  const isForbidden = axios.isAxiosError(error) && error.response?.status === 403
  if (error || !contract) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">
          {isForbidden ? "You're not a party to this contract." : 'Could not load contract.'}
        </p>
      </div>
    )
  }

  const isFounder = user?.id === contract.founder_id
  const isApplicant = user?.id === contract.applicant_id
  const currency = typeof contract.terms.currency === 'string' ? contract.terms.currency : 'CAD'
  const errorDetail = axios.isAxiosError(saveMutation.error)
    ? (saveMutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">{contract.job_title}</h1>
      <p className="mt-1 text-gray-500">{template?.label || contract.template_type}</p>
      <span
        className={`mt-3 inline-block rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_STYLES[contract.status]}`}
      >
        {contract.status.replace('_', ' ')}
      </span>

      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="font-semibold text-gray-900">Terms</h2>
        {editing ? (
          <div className="mt-3 space-y-4">
            {template?.required_terms.map((term) => (
              <div key={term}>
                <label className="block text-sm font-medium capitalize text-gray-700">
                  {term.replace(/_/g, ' ')}
                </label>
                <input
                  type={
                    isMoneyTerm(term) || isNumericTerm(term)
                      ? 'number'
                      : term.endsWith('_date')
                        ? 'date'
                        : 'text'
                  }
                  className="mt-1 w-full rounded-md border border-gray-300 p-2"
                  value={editValues[term] || ''}
                  onChange={(e) => setEditValues((v) => ({ ...v, [term]: e.target.value }))}
                />
              </div>
            ))}
            <div className="flex gap-3">
              <button
                onClick={() => saveMutation.mutate()}
                disabled={saveMutation.isPending}
                className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {saveMutation.isPending ? 'Saving…' : 'Save'}
              </button>
              <button
                onClick={() => setEditing(false)}
                className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700"
              >
                Cancel
              </button>
            </div>
            {saveMutation.isError && (
              <p className="text-sm text-red-600">{errorDetail || 'Could not save terms.'}</p>
            )}
          </div>
        ) : (
          <dl className="mt-3 divide-y divide-gray-100">
            {Object.entries(contract.terms).map(([key, value]) => (
              <div key={key} className="flex justify-between py-2 text-sm">
                <dt className="capitalize text-gray-500">{key.replace(/_/g, ' ')}</dt>
                <dd className="text-gray-900">{formatTermValue(key, value, currency)}</dd>
              </div>
            ))}
          </dl>
        )}

        {contract.signed_at && (
          <p className="mt-4 text-sm text-gray-500">
            Signed on {new Date(contract.signed_at).toLocaleDateString()}
          </p>
        )}
      </div>

      {!editing && (
        <div className="mt-6 flex flex-wrap gap-3">
          {isFounder && contract.status === 'draft' && (
            <>
              <button
                onClick={startEditing}
                className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700"
              >
                Edit terms
              </button>
              <button
                onClick={() => sendMutation.mutate()}
                disabled={sendMutation.isPending}
                className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {sendMutation.isPending ? 'Sending…' : 'Send'}
              </button>
            </>
          )}
          {isFounder && contract.status !== 'signed' && contract.status !== 'cancelled' && (
            <button
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
              className="rounded-md border border-red-300 px-5 py-2 font-medium text-red-700"
            >
              {cancelMutation.isPending ? 'Cancelling…' : 'Cancel contract'}
            </button>
          )}
          {isFounder && contract.status !== 'cancelled' && (
            <PayUserButton userId={contract.applicant_id} />
          )}
          {isApplicant && contract.status === 'pending_signature' && (
            <div>
              <p className="mb-2 text-sm text-gray-500">
                This records your acceptance in Ascend. It is not a legal e-signature.
              </p>
              <button
                onClick={() => signMutation.mutate()}
                disabled={signMutation.isPending}
                className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
              >
                {signMutation.isPending ? 'Signing…' : 'Sign'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
