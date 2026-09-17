import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { cancelPayment, getPayment } from '@/services/payments'
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

export function PaymentDetail() {
  const { id } = useParams<{ id: string }>()
  const paymentId = Number(id)
  const user = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()

  const {
    data: payment,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['payment', paymentId],
    queryFn: () => getPayment(paymentId),
    enabled: !Number.isNaN(paymentId),
  })

  const cancelMutation = useMutation({
    mutationFn: () => cancelPayment(paymentId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['payment', paymentId] }),
  })

  if (isLoading) return <p className="mx-auto max-w-2xl px-4 py-10 text-gray-500">Loading…</p>

  const isForbidden = axios.isAxiosError(error) && error.response?.status === 403
  if (error || !payment) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">
          {isForbidden ? "You're not a party to this payment." : 'Could not load payment.'}
        </p>
      </div>
    )
  }

  const isSender = user?.id === payment.from_user_id
  const toLabel = payment.to_user_name || payment.recipient_name || payment.recipient_email || '—'

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">{formatCents(payment.amount, payment.currency)}</h1>
      <p className="mt-1 text-gray-500">{TYPE_LABELS[payment.payment_type]}</p>
      <span
        className={`mt-3 inline-block rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_STYLES[payment.status]}`}
      >
        {payment.status}
      </span>

      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="font-semibold text-gray-900">Details</h2>
        <dl className="mt-3 divide-y divide-gray-100">
          <div className="flex justify-between py-2 text-sm">
            <dt className="text-gray-500">From</dt>
            <dd className="text-gray-900">{payment.from_user_name}</dd>
          </div>
          <div className="flex justify-between py-2 text-sm">
            <dt className="text-gray-500">To</dt>
            <dd className="text-gray-900">{toLabel}</dd>
          </div>
          <div className="flex justify-between py-2 text-sm">
            <dt className="text-gray-500">Amount</dt>
            <dd className="text-gray-900">{formatCents(payment.amount, payment.currency)}</dd>
          </div>
          <div className="flex justify-between py-2 text-sm">
            <dt className="text-gray-500">Type</dt>
            <dd className="text-gray-900">{TYPE_LABELS[payment.payment_type]}</dd>
          </div>
          {payment.notes && (
            <div className="flex justify-between py-2 text-sm">
              <dt className="text-gray-500">Notes</dt>
              <dd className="text-gray-900">{payment.notes}</dd>
            </div>
          )}
          <div className="flex justify-between py-2 text-sm">
            <dt className="text-gray-500">Created</dt>
            <dd className="text-gray-900">{new Date(payment.created_at).toLocaleDateString()}</dd>
          </div>
        </dl>
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-3">
        {isSender && payment.status === 'pending' && (
          <button
            onClick={() => cancelMutation.mutate()}
            disabled={cancelMutation.isPending}
            className="rounded-md border border-red-300 px-5 py-2 font-medium text-red-700"
          >
            {cancelMutation.isPending ? 'Cancelling…' : 'Cancel'}
          </button>
        )}
        <div>
          <button
            disabled
            className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-400"
          >
            Send via Wise
          </button>
          <p className="mt-1 text-xs text-gray-500">Not available yet — this payment is recorded only.</p>
        </div>
      </div>
      {cancelMutation.isError && <p className="mt-3 text-sm text-red-600">Could not cancel payment.</p>}
    </div>
  )
}
