import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getThreads } from '@/services/messages'

function truncate(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max)}…` : text
}

function formatThreadTime(iso: string): string {
  const date = new Date(iso)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  return isToday
    ? date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
    : date.toLocaleDateString()
}

export function Messages() {
  const {
    data: threads,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['threads'],
    queryFn: getThreads,
    refetchInterval: 15000,
  })

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Messages</h1>

      <div className="mt-6 space-y-3">
        {isLoading && <p className="text-gray-500">Loading conversations…</p>}
        {error && <p className="text-red-600">Could not load conversations.</p>}
        {threads?.length === 0 && (
          <p className="text-gray-500">No conversations yet. Message someone from their profile.</p>
        )}
        {threads?.map((thread) => (
          <Link
            key={thread.user_id}
            to={`/messages/${thread.user_id}`}
            className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:border-primary-300 hover:shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className={`truncate text-gray-900 ${thread.unread_count > 0 ? 'font-bold' : 'font-medium'}`}>
                  {thread.user_name}
                </p>
                <p
                  className={`mt-0.5 truncate text-sm ${
                    thread.unread_count > 0 ? 'font-semibold text-gray-800' : 'text-gray-500'
                  }`}
                >
                  {truncate(thread.last_message_body, 80)}
                </p>
              </div>
              <div className="flex shrink-0 flex-col items-end gap-1">
                <span className="text-xs text-gray-500">{formatThreadTime(thread.last_message_at)}</span>
                {thread.unread_count > 0 && (
                  <span className="rounded-full bg-primary-600 px-2 py-0.5 text-xs font-medium text-white">
                    {thread.unread_count}
                  </span>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
