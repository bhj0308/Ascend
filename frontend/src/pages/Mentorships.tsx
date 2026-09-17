import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  acceptMentorship,
  completeMentorship,
  declineMentorship,
  getMyMentorships,
} from '@/services/mentorships'
import { useAuthStore } from '@/store/authStore'
import type { MentorshipStatus } from '@/types/mentorship'

const STATUS_STYLES: Record<MentorshipStatus, string> = {
  requested: 'bg-yellow-100 text-yellow-700',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-gray-100 text-gray-700',
  declined: 'bg-red-100 text-red-700',
}

export function Mentorships() {
  const user = useAuthStore((s) => s.user)
  const queryClient = useQueryClient()

  const { data: mentorships, isLoading, error } = useQuery({
    queryKey: ['mentorships'],
    queryFn: getMyMentorships,
  })

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['mentorships'] })

  const acceptMutation = useMutation({ mutationFn: acceptMentorship, onSuccess: invalidate })
  const declineMutation = useMutation({ mutationFn: declineMentorship, onSuccess: invalidate })
  const completeMutation = useMutation({ mutationFn: completeMentorship, onSuccess: invalidate })

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Mentorships</h1>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-gray-500">Loading mentorships…</p>}
        {error && <p className="text-red-600">Could not load mentorships.</p>}
        {mentorships?.length === 0 && (
          <p className="text-gray-500">No mentorships yet. Visit someone's profile to request one.</p>
        )}
        {mentorships?.map((mentorship) => {
          const isMentor = user?.id === mentorship.mentor_id
          const counterpart = isMentor
            ? `Mentoring ${mentorship.mentee_name}`
            : `Mentored by ${mentorship.mentor_name}`
          const isPending =
            acceptMutation.isPending || declineMutation.isPending || completeMutation.isPending

          return (
            <div
              key={mentorship.id}
              className="rounded-lg border border-gray-200 bg-white p-5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{counterpart}</h3>
                  {mentorship.notes && <p className="mt-1 text-sm text-gray-500">{mentorship.notes}</p>}
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium capitalize ${STATUS_STYLES[mentorship.status]}`}
                >
                  {mentorship.status}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-3 text-xs text-gray-500">
                <span>Requested {new Date(mentorship.created_at).toLocaleDateString()}</span>
              </div>

              {(isMentor && mentorship.status === 'requested') && (
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={() => acceptMutation.mutate(mentorship.id)}
                    disabled={isPending}
                    className="rounded-md bg-primary-600 px-5 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => declineMutation.mutate(mentorship.id)}
                    disabled={isPending}
                    className="rounded-md border border-red-300 px-5 py-2 text-sm font-medium text-red-700 disabled:opacity-50"
                  >
                    Decline
                  </button>
                </div>
              )}

              {mentorship.status === 'active' && (
                <div className="mt-4">
                  <button
                    onClick={() => completeMutation.mutate(mentorship.id)}
                    disabled={isPending}
                    className="rounded-md border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 disabled:opacity-50"
                  >
                    Mark complete
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
