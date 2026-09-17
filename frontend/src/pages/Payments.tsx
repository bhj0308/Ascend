import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getMyPayments } from '@/services/payments'
import { useAuthStore } from '@/store/authStore'
import { formatCents } from '@/utils/money'
import type { PaymentStatus, PaymentType } from '@/types/payment'

const STATUS_STYLES: Record<PaymentStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  processing: 'bg-blue-100 text-blue-700',
  complete: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  cancelled: 'bg-gray-100 text-gray-700',
}

const TYPE_LABELS: Record<PaymentType, string> = {
  salary: 'Salary',
  contract_payment: 'Contract payment',
  remittance: 'Remittance',
}

export function Payments() {
  const user = useAuthStore((s) => s.user)

  const { data: payments, isLoading, error } = useQuery({
    queryKey: ['payments'],
    queryFn: getMyPayments,
  })

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Payments</h1>

      <div className="mt-4 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
        Payments are recorded for your history only — transfers via Wise are coming soon. No
        money is moved from Ascend yet.
      </div>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-gray-500">Loading payments…</p>}
        {error && <p className="text-red-600">Could not load payments.</p>}
        {payments?.length === 0 && <p className="text-gray-500">No payments yet.</p>}
        {payments?.map((payment) => {
          const isSender = user?.id === payment.from_user_id
          const direction = isSender
            ? `To ${payment.to_user_name || payment.recipient_name || payment.recipient_email}`
            : `From ${payment.from_user_name}`
          return (
            <Link
              key={payment.id}
              to={`/payments/${payment.id}`}
              className="block rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{direction}</h3>
                  <p className="text-sm text-gray-500">{TYPE_LABELS[payment.payment_type]}</p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_STYLES[payment.status]}`}
                >
                  {payment.status}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                <span className="font-medium text-gray-900">
                  {formatCents(payment.amount, payment.currency)}
                </span>
                <span>{new Date(payment.created_at).toLocaleDateString()}</span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
