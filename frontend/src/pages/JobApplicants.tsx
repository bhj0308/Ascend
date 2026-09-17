import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { getJobApplications } from '@/services/applications'
import { getProfile } from '@/services/profile'
import type { Application } from '@/types'

function ApplicantRow({ application, jobId }: { application: Application; jobId: number }) {
  const { data: applicant, isLoading } = useQuery({
    queryKey: ['profile', application.user_id],
    queryFn: () => getProfile(application.user_id),
  })

  const name =
    (applicant && `${applicant.first_name || ''} ${applicant.last_name || ''}`.trim()) ||
    `Applicant #${application.user_id}`

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900">
            {isLoading ? (
              'Loading…'
            ) : (
              <Link to={`/users/${application.user_id}`} className="hover:text-primary-600">
                {name}
              </Link>
            )}
          </h3>
          {applicant?.visa_status && (
            <p className="text-sm text-gray-500">Visa status: {applicant.visa_status}</p>
          )}
        </div>
        <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium capitalize text-gray-700">
          {application.status}
        </span>
      </div>

      {applicant?.skills && applicant.skills.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {applicant.skills.map((skill) => (
            <span
              key={skill}
              className="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-700"
            >
              {skill}
            </span>
          ))}
        </div>
      )}

      {application.cover_note && (
        <p className="mt-3 text-sm text-gray-700">{application.cover_note}</p>
      )}

      <Link
        to={`/contracts/new?application=${application.id}&job=${jobId}`}
        className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
      >
        Create contract →
      </Link>
    </div>
  )
}

export function JobApplicants() {
  const { id } = useParams<{ id: string }>()
  const jobId = Number(id)

  const {
    data: applications,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['job-applications', jobId],
    queryFn: () => getJobApplications(jobId),
    enabled: !Number.isNaN(jobId),
  })

  const isForbidden = axios.isAxiosError(error) && error.response?.status === 403

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Applicants</h1>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-gray-500">Loading applicants…</p>}
        {error && (
          <p className="text-red-600">
            {isForbidden ? "This isn't your job." : 'Could not load applicants.'}
          </p>
        )}
        {applications?.length === 0 && (
          <p className="text-gray-500">No applicants yet.</p>
        )}
        {applications?.map((application) => (
          <ApplicantRow key={application.id} application={application} jobId={jobId} />
        ))}
      </div>
    </div>
  )
}
