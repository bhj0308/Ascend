import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { MessageButton } from '@/components/MessageButton'
import { getProfile } from '@/services/profile'
import { requestMentorship } from '@/services/mentorships'
import { useAuthStore } from '@/store/authStore'

export function PublicProfile() {
  const { id } = useParams<{ id: string }>()
  const userId = Number(id)
  const currentUser = useAuthStore((s) => s.user)
  const [requesting, setRequesting] = useState(false)
  const [notes, setNotes] = useState('')

  const {
    data: profile,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['profile', userId],
    queryFn: () => getProfile(userId),
    enabled: !Number.isNaN(userId),
  })

  const requestMutation = useMutation({
    mutationFn: () => requestMentorship({ mentor_id: userId, notes: notes || undefined }),
  })

  if (Number.isNaN(userId)) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">User not found.</p>
      </div>
    )
  }

  if (isLoading) return <p className="mx-auto max-w-2xl px-4 py-10 text-gray-500">Loading…</p>

  const isNotFound = axios.isAxiosError(error) && error.response?.status === 404
  if (error || !profile) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">{isNotFound ? 'User not found.' : 'Could not load profile.'}</p>
      </div>
    )
  }

  const isSelf = currentUser?.id === profile.id
  const location = [profile.city, profile.country].filter(Boolean).join(', ')
  const errorDetail = axios.isAxiosError(requestMutation.error)
    ? (requestMutation.error.response?.data as { detail?: string } | undefined)?.detail
    : undefined

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">
        {profile.first_name} {profile.last_name}
      </h1>
      <p className="mt-1 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
        {profile.user_type.replace('_', ' ')}
      </p>
      {location && <p className="mt-2 text-gray-500">{location}</p>}

      {profile.bio && <p className="mt-4 text-gray-700">{profile.bio}</p>}

      {profile.skills && profile.skills.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-900">Skills</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {profile.skills.map((skill) => (
              <span key={skill} className="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-700">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {profile.languages && profile.languages.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-900">Languages</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {profile.languages.map((language) => (
              <span key={language} className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700">
                {language}
              </span>
            ))}
          </div>
        </div>
      )}

      {profile.visa_status && (
        <p className="mt-4 text-sm text-gray-500">Visa status: {profile.visa_status}</p>
      )}

      {isSelf ? (
        <p className="mt-6 text-sm text-gray-500">This is you.</p>
      ) : (
        <div className="mt-6 flex flex-wrap gap-3">
          {requestMutation.isSuccess ? (
            <p className="text-sm text-green-700">Request sent</p>
          ) : requesting ? (
            <div className="w-full">
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Add a note (optional)"
                className="w-full rounded-md border border-gray-300 p-2 text-sm"
                rows={3}
              />
              <div className="mt-2 flex gap-3">
                <button
                  onClick={() => requestMutation.mutate()}
                  disabled={requestMutation.isPending}
                  className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {requestMutation.isPending ? 'Sending…' : 'Send'}
                </button>
                <button
                  onClick={() => setRequesting(false)}
                  className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700"
                >
                  Cancel
                </button>
              </div>
              {requestMutation.isError && (
                <p className="mt-2 text-sm text-red-600">{errorDetail || 'Could not send request.'}</p>
              )}
            </div>
          ) : (
            <button
              onClick={() => setRequesting(true)}
              className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700"
            >
              Request mentorship
            </button>
          )}
          <MessageButton userId={profile.id} />
        </div>
      )}
    </div>
  )
}
