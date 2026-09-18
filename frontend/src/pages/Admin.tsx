import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { closeJob, listAllJobs, listUsers, suspendUser, unsuspendUser } from '@/services/admin'
import { useAuthStore } from '@/store/authStore'
import { describeError } from '@/utils/errors'

const statusStyles: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  suspended: 'bg-red-100 text-red-700',
  inactive: 'bg-gray-100 text-gray-600',
  open: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-600',
  filled: 'bg-blue-100 text-blue-700',
  draft: 'bg-yellow-100 text-yellow-800',
}

function Pill({ value }: { value: string }) {
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
        statusStyles[value] || 'bg-gray-100 text-gray-600'
      }`}
    >
      {value}
    </span>
  )
}

function SearchBox({ value, onChange, placeholder }: { value: string; onChange: (v: string) => void; placeholder: string }) {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full max-w-sm rounded-md border border-gray-300 p-2 text-sm"
    />
  )
}

function UsersPanel() {
  const queryClient = useQueryClient()
  const [q, setQ] = useState('')
  const currentUser = useAuthStore((s) => s.user)

  const { data: users, isLoading } = useQuery({
    queryKey: ['admin', 'users', q],
    queryFn: () => listUsers(q || undefined),
  })

  const mutation = useMutation({
    mutationFn: ({ id, suspend }: { id: number; suspend: boolean }) =>
      suspend ? suspendUser(id) : unsuspendUser(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  })

  return (
    <section className="mt-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Users</h2>
        <SearchBox value={q} onChange={setQ} placeholder="Search email or name" />
      </div>

      {mutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          {describeError(mutation.error, 'Could not update that account.')}
        </p>
      )}

      {isLoading ? (
        <p className="mt-4 text-gray-500">Loading…</p>
      ) : !users?.length ? (
        <p className="mt-4 text-gray-500">No users found.</p>
      ) : (
        <ul className="mt-4 divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
          {users.map((user) => {
            const name = [user.first_name, user.last_name].filter(Boolean).join(' ')
            const isSelf = user.id === currentUser?.id
            const isSuspended = user.status === 'suspended'
            return (
              <li key={user.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <Link to={`/users/${user.id}`} className="font-medium text-gray-900 hover:text-primary-600">
                      {name || `User #${user.id}`}
                    </Link>
                    <Pill value={user.status} />
                    <span className="text-xs text-gray-500">{user.user_type.replace('_', ' ')}</span>
                    {!user.email_verified && (
                      <span className="text-xs text-yellow-700">unverified</span>
                    )}
                  </div>
                  <p className="truncate text-sm text-gray-500">{user.email}</p>
                </div>
                {user.status === 'inactive' ? (
                  <span className="text-xs text-gray-400">deleted</span>
                ) : isSelf ? (
                  <span className="text-xs text-gray-400">you</span>
                ) : (
                  <button
                    onClick={() => mutation.mutate({ id: user.id, suspend: !isSuspended })}
                    disabled={mutation.isPending}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium disabled:opacity-50 ${
                      isSuspended
                        ? 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                        : 'bg-red-600 text-white hover:bg-red-700'
                    }`}
                  >
                    {isSuspended ? 'Unsuspend' : 'Suspend'}
                  </button>
                )}
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}

function JobsPanel() {
  const queryClient = useQueryClient()
  const [q, setQ] = useState('')

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['admin', 'jobs', q],
    queryFn: () => listAllJobs(q || undefined),
  })

  const mutation = useMutation({
    mutationFn: (jobId: number) => closeJob(jobId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin', 'jobs'] }),
  })

  return (
    <section className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-gray-900">Jobs</h2>
        <SearchBox value={q} onChange={setQ} placeholder="Search title or company" />
      </div>

      {mutation.isError && (
        <p className="mt-3 text-sm text-red-600">
          {describeError(mutation.error, 'Could not close that job.')}
        </p>
      )}

      {isLoading ? (
        <p className="mt-4 text-gray-500">Loading…</p>
      ) : !jobs?.length ? (
        <p className="mt-4 text-gray-500">No jobs found.</p>
      ) : (
        <ul className="mt-4 divide-y divide-gray-200 rounded-lg border border-gray-200 bg-white">
          {jobs.map((job) => (
            <li key={job.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <Link to={`/jobs/${job.id}`} className="font-medium text-gray-900 hover:text-primary-600">
                    {job.title}
                  </Link>
                  <Pill value={job.status} />
                </div>
                <p className="truncate text-sm text-gray-500">
                  {job.company_name || '—'} · posted by{' '}
                  <Link to={`/users/${job.creator_id}`} className="hover:text-primary-600">
                    User #{job.creator_id}
                  </Link>
                </p>
              </div>
              {job.status === 'closed' ? (
                <span className="text-xs text-gray-400">closed</span>
              ) : (
                <button
                  onClick={() => mutation.mutate(job.id)}
                  disabled={mutation.isPending}
                  className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                >
                  Close
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function Admin() {
  const user = useAuthStore((s) => s.user)

  if (!user) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-gray-600">
          <Link to="/login" className="text-primary-600 hover:text-primary-700">
            Log in
          </Link>{' '}
          to continue.
        </p>
      </div>
    )
  }

  if (user.user_type !== 'admin') {
    return (
      <div className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-red-600">You don't have access to this page.</p>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Moderation</h1>
      <p className="mt-2 text-sm text-gray-600">
        Suspending an account blocks sign-in and closes its open jobs. Records stay so
        counterparties keep their contracts, payments and messages.
      </p>
      <UsersPanel />
      <JobsPanel />
    </div>
  )
}
