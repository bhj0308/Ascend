import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { createContract, getTemplates } from '@/services/contracts'
import { isMoneyTerm, isNumericTerm } from '@/utils/money'
import type { ContractTemplateType } from '@/types'

const CURRENCIES = ['CAD', 'KRW', 'USD']

export function ContractNew() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  // `Number(null)` is 0, not NaN — coerce a missing/empty param to NaN so the guard below catches it.
  const applicationId = Number(searchParams.get('application') || NaN)

  const [templateType, setTemplateType] = useState<ContractTemplateType | ''>('')
  const [termValues, setTermValues] = useState<Record<string, string>>({})

  const { data: templates, isLoading } = useQuery({
    queryKey: ['contract-templates'],
    queryFn: getTemplates,
  })

  const selectedTemplate = templates?.find((t) => t.type === templateType)

  const mutation = useMutation({
    mutationFn: () => {
      const terms: Record<string, unknown> = {}
      for (const term of selectedTemplate?.required_terms || []) {
        const raw = termValues[term] || ''
        terms[term] = isMoneyTerm(term)
          ? Math.round(parseFloat(raw || '0') * 100)
          : isNumericTerm(term)
            ? Number(raw)
            : raw
      }
      return createContract({
        application_id: applicationId,
        template_type: templateType as ContractTemplateType,
        terms,
      })
    },
    onSuccess: (contract) => navigate(`/contracts/${contract.id}`),
  })

  const errorDetail = axios.isAxiosError(mutation.error)
    ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  const handleTemplateChange = (value: string) => {
    setTemplateType(value as ContractTemplateType)
    setTermValues({})
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  if (!Number.isInteger(applicationId) || applicationId <= 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">Missing application. Open this page from an applicant's row.</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">New Contract</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Template</label>
          {isLoading ? (
            <p className="mt-1 text-sm text-gray-500">Loading templates…</p>
          ) : (
            <select
              required
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={templateType}
              onChange={(e) => handleTemplateChange(e.target.value)}
            >
              <option value="" disabled>
                Select a template
              </option>
              {templates?.map((t) => (
                <option key={t.type} value={t.type}>
                  {t.label}
                </option>
              ))}
            </select>
          )}
          {selectedTemplate && (
            <p className="mt-2 text-sm text-gray-500">{selectedTemplate.description}</p>
          )}
        </div>

        {selectedTemplate?.required_terms.map((term) => (
          <div key={term}>
            <label className="block text-sm font-medium capitalize text-gray-700">
              {term.replace(/_/g, ' ')}
            </label>
            {term === 'currency' ? (
              <select
                required
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={termValues[term] || ''}
                onChange={(e) => setTermValues((v) => ({ ...v, [term]: e.target.value }))}
              >
                <option value="" disabled>
                  Select currency
                </option>
                {CURRENCIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            ) : isMoneyTerm(term) ? (
              <input
                required
                type="number"
                min="0"
                step="0.01"
                placeholder="Whole currency units, e.g. 75000"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={termValues[term] || ''}
                onChange={(e) => setTermValues((v) => ({ ...v, [term]: e.target.value }))}
              />
            ) : isNumericTerm(term) ? (
              <input
                required
                type="number"
                min="0.5"
                step="0.5"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={termValues[term] || ''}
                onChange={(e) => setTermValues((v) => ({ ...v, [term]: e.target.value }))}
              />
            ) : term.endsWith('_date') ? (
              <input
                required
                type="date"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={termValues[term] || ''}
                onChange={(e) => setTermValues((v) => ({ ...v, [term]: e.target.value }))}
              />
            ) : (
              <input
                required
                type="text"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={termValues[term] || ''}
                onChange={(e) => setTermValues((v) => ({ ...v, [term]: e.target.value }))}
              />
            )}
          </div>
        ))}

        {selectedTemplate && (
          <button
            type="submit"
            disabled={mutation.isPending}
            className="rounded-md bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {mutation.isPending ? 'Creating…' : 'Create Contract'}
          </button>
        )}
        {mutation.isError && (
          <p className="text-sm text-red-600">{errorDetail || 'Could not create contract.'}</p>
        )}
      </form>
    </div>
  )
}
