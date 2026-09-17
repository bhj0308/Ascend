import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getMyContracts, getTemplates } from '@/services/contracts'
import { useAuthStore } from '@/store/authStore'
import type { ContractStatus } from '@/types'

const STATUS_STYLES: Record<ContractStatus, string> = {
  draft: 'bg-gray-100 text-gray-700',
  pending_signature: 'bg-yellow-100 text-yellow-700',
  signed: 'bg-green-100 text-green-700',
  cancelled: 'bg-red-100 text-red-700',
}

export function Contracts() {
  const user = useAuthStore((s) => s.user)

  const { data: contracts, isLoading, error } = useQuery({
    queryKey: ['contracts'],
    queryFn: getMyContracts,
  })

  const { data: templates } = useQuery({
    queryKey: ['contract-templates'],
    queryFn: getTemplates,
  })

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Contracts</h1>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-gray-500">Loading contracts…</p>}
        {error && <p className="text-red-600">Could not load contracts.</p>}
        {contracts?.length === 0 && (
          <p className="text-gray-500">No contracts yet.</p>
        )}
        {contracts?.map((contract) => {
          const template = templates?.find((t) => t.type === contract.template_type)
          const role = user?.id === contract.founder_id ? 'Founder' : 'Applicant'
          return (
            <Link
              key={contract.id}
              to={`/contracts/${contract.id}`}
              className="block rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{contract.job_title}</h3>
                  <p className="text-sm text-gray-500">{template?.label || contract.template_type}</p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_STYLES[contract.status]}`}
                >
                  {contract.status.replace('_', ' ')}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                <span>{role}</span>
                <span>Created {new Date(contract.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
