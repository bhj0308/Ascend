import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { getThread, sendMessage } from '@/services/messages'
import { getProfile } from '@/services/profile'
import { useAuthStore } from '@/store/authStore'

export function MessageThread() {
  const { userId: userIdParam } = useParams<{ userId: string }>()
  const userId = Number(userIdParam)
  const isValidUserId = Number.isInteger(userId) && userId > 0
  const currentUser = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()
  const [body, setBody] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  const threadKey = ['thread', String(userId)]

  const {
    data: messages,
    isLoading,
    error,
  } = useQuery({
    queryKey: threadKey,
    queryFn: () => getThread(userId),
    enabled: isValidUserId,
    refetchInterval: 5000,
  })

  const { data: counterpart, error: profileError } = useQuery({
    queryKey: ['profile', userId],
    queryFn: () => getProfile(userId),
    enabled: isValidUserId,
  })

  const sendMutation = useMutation({
    mutationFn: () => sendMessage({ recipient_id: userId, body: body.trim() }),
    onSuccess: () => {
      setBody('')
      queryClient.invalidateQueries({ queryKey: threadKey })
      queryClient.invalidateQueries({ queryKey: ['threads'] })
    },
  })

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end' })
  }, [messages])

  if (!isValidUserId) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">Invalid conversation.</p>
      </div>
    )
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (body.trim() && !sendMutation.isPending) sendMutation.mutate()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (body.trim() && !sendMutation.isPending) sendMutation.mutate()
  }

  const isProfileNotFound = axios.isAxiosError(profileError) && profileError.response?.status === 404
  const headerName = isProfileNotFound
    ? 'User not found'
    : counterpart
      ? [counterpart.first_name, counterpart.last_name].filter(Boolean).join(' ') || counterpart.email
      : ' '

  const sendErrorDetail = axios.isAxiosError(sendMutation.error)
    ? (sendMutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  return (
    <div className="mx-auto flex max-w-2xl flex-col px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">{headerName}</h1>

      <div className="mt-6 flex-1 space-y-3 overflow-y-auto rounded-lg border border-gray-200 bg-white p-4">
        {isLoading && <p className="text-gray-500">Loading messages…</p>}
        {error && <p className="text-red-600">Could not load messages.</p>}
        {messages?.length === 0 && <p className="text-gray-500">No messages yet. Say hello.</p>}
        {messages?.map((message) => {
          const isMine = message.sender_id === currentUser?.id
          return (
            <div key={message.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[75%] rounded-lg px-4 py-2 text-sm ${
                  isMine ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.body}</p>
                <p className={`mt-1 text-xs ${isMine ? 'text-primary-100' : 'text-gray-500'}`}>
                  {new Date(message.created_at).toLocaleString()}
                </p>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex gap-3">
        <textarea
          rows={2}
          className="flex-1 rounded-md border border-gray-300 p-2"
          placeholder="Write a message…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          disabled={!body.trim() || sendMutation.isPending}
          className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {sendMutation.isPending ? 'Sending…' : 'Send'}
        </button>
      </form>
      {sendMutation.isError && (
        <p className="mt-2 text-sm text-red-600">{sendErrorDetail || 'Could not send message.'}</p>
      )}
    </div>
  )
}
