import { Link } from 'react-router-dom'

export function PayUserButton({ userId, name }: { userId: number; name?: string }) {
  return (
    <Link
      to={`/payments/new?to=${userId}`}
      title={name}
      className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700 hover:bg-gray-50"
    >
      Record payment
    </Link>
  )
}
