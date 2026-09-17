import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { createPayment } from '@/services/payments'
import { getProfile } from '@/services/profile'
import type { PaymentType } from '@/types/payment'

const CURRENCIES = ['CAD', 'KRW', 'USD']

const TYPE_OPTIONS: { value: PaymentType; label: string }[] = [
  { value: 'salary', label: 'Salary' },
  { value: 'contract_payment', label: 'Contract payment' },
  { value: 'remittance', label: 'Remittance' },
]

export function PaymentNew() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const toParam = searchParams.get('to')
  // `Number(null)` is 0, not NaN — only coerce when the param is actually present.
  const toUserId = toParam !== null ? Number(toParam) : undefined
  const hasInvalidTo = toParam !== null && (!Number.isInteger(toUserId) || (toUserId as number) <= 0)

  const [recipientEmail, setRecipientEmail] = useState('')
  const [recipientName, setRecipientName] = useState('')
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('')
  const [paymentType, setPaymentType] = useState<PaymentType | ''>('')
  const [notes, setNotes] = useState('')

  const { data: recipient, isLoading: isLoadingRecipient } = useQuery({
    queryKey: ['profile', toUserId],
    queryFn: () => getProfile(toUserId as number),
    enabled: !hasInvalidTo && toUserId !== undefined,
  })

  const mutation = useMutation({
    mutationFn: () =>
      createPayment({
        ...(toUserId !== undefined
          ? { to_user_id: toUserId }
          : { recipient_email: recipientEmail, recipient_name: recipientName || undefined }),
        amount: Math.round(parseFloat(amount || '0') * 100),
        currency,
        payment_type: paymentType as PaymentType,
        notes: notes || undefined,
      }),
    onSuccess: (payment) => navigate(`/payments/${payment.id}`),
  })

  const status = axios.isAxiosError(mutation.error) ? mutation.error.response?.status : undefined
  const errorMessage =
    status === 422
      ? 'Amount must be positive and currency a 3-letter code.'
      : status === 400 && axios.isAxiosError(mutation.error)
        ? (mutation.error.response?.data as { detail?: string } | undefined)?.detail
        : undefined

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate()
  }

  if (hasInvalidTo) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">Invalid recipient. Open this page from a user's profile or contract.</p>
      </div>
    )
  }

  const recipientLabel = recipient
    ? [recipient.first_name, recipient.last_name].filter(Boolean).join(' ') || recipient.email
    : undefined

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">New Payment</h1>

      <div className="mt-4 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
        This records a payment for your history only — no money is moved from Ascend yet.
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        {toUserId !== undefined ? (
          <div>
            <label className="block text-sm font-medium text-gray-700">Paying</label>
            <p className="mt-1 rounded-md border border-gray-200 bg-gray-50 p-2 text-gray-900">
              {isLoadingRecipient ? 'Loading…' : recipientLabel || `User #${toUserId}`}
            </p>
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">Recipient email</label>
              <input
                required
                type="email"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Recipient name (optional)</label>
              <input
                type="text"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
              />
            </div>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700">Amount</label>
          <input
            required
            type="number"
            min="0"
            step="0.01"
            placeholder="Whole currency units, e.g. 500.00"
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Currency</label>
          <select
            required
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
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
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Payment type</label>
          <select
            required
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={paymentType}
            onChange={(e) => setPaymentType(e.target.value as PaymentType)}
          >
            <option value="" disabled>
              Select type
            </option>
            {TYPE_OPTIONS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Notes (optional)</label>
          <textarea
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Creating…' : 'Create Payment'}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-600">{errorMessage || 'Could not create payment.'}</p>
        )}
      </form>
    </div>
  )
}
