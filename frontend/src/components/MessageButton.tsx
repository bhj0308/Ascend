import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

export function MessageButton({ userId }: { userId: number }) {
  const currentUserId = useAuthStore((s) => s.user?.id)

  if (currentUserId === userId) return null

  return (
    <Link
      to={`/messages/${userId}`}
      className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700 hover:bg-gray-50"
    >
      Message
    </Link>
  )
}
