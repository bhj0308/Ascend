import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { getJob, applyToJob } from '@/services/jobs'
import { useAuthStore } from '@/store/authStore'

export function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const jobId = Number(id)
  const { isAuthenticated } = useAuthStore()
  const [coverNote, setCoverNote] = useState('')
  const [applied, setApplied] = useState(false)

  const { data: job, isLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJob(jobId),
    enabled: !Number.isNaN(jobId),
  })

  const applyMutation = useMutation({
    mutationFn: () => applyToJob(jobId, coverNote),
    onSuccess: () => setApplied(true),
  })

  if (isLoading) return <p className="mx-auto max-w-3xl px-4 py-10 text-gray-500">Loading…</p>
  if (!job) return <p className="mx-auto max-w-3xl px-4 py-10 text-gray-500">Job not found.</p>

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
      {job.company_name && <p className="mt-1 text-gray-500">{job.company_name}</p>}

      <p className="mt-6 whitespace-pre-wrap text-gray-700">{job.description}</p>

      <div className="mt-8 rounded-lg border border-gray-200 bg-white p-6">
        {!isAuthenticated ? (
          <p className="text-gray-600">Log in to apply for this job.</p>
        ) : applied ? (
          <p className="font-medium text-green-700">Application submitted! 🎉</p>
        ) : (
          <>
            <h2 className="font-semibold text-gray-900">Apply to this job</h2>
            <textarea
              className="mt-3 w-full rounded-md border border-gray-300 p-3 text-sm"
              rows={4}
              placeholder="A short note about why you're a good fit (optional)"
              value={coverNote}
              onChange={(e) => setCoverNote(e.target.value)}
            />
            <button
              onClick={() => applyMutation.mutate()}
              disabled={applyMutation.isPending}
              className="mt-3 rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
            >
              {applyMutation.isPending ? 'Submitting…' : 'Submit Application'}
            </button>
            {applyMutation.isError && (
              <p className="mt-2 text-sm text-red-600">
                Could not submit application. Have you already applied?
              </p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
