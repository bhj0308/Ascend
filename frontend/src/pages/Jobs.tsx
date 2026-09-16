import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { browseJobs, type JobFilters } from '@/services/jobs'
import { JobCard } from '@/components/JobCard'

export function Jobs() {
  const [filters, setFilters] = useState<JobFilters>({})

  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['jobs', filters],
    queryFn: () => browseJobs(filters),
  })

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Browse Jobs</h1>

      <div className="mt-4 flex flex-wrap gap-3">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={!!filters.remote_ok}
            onChange={(e) => setFilters((f) => ({ ...f, remote_ok: e.target.checked || undefined }))}
          />
          Remote OK
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={!!filters.visa_sponsorship}
            onChange={(e) =>
              setFilters((f) => ({ ...f, visa_sponsorship: e.target.checked || undefined }))
            }
          />
          Visa Sponsorship
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={!!filters.iec_friendly}
            onChange={(e) =>
              setFilters((f) => ({ ...f, iec_friendly: e.target.checked || undefined }))
            }
          />
          IEC Friendly
        </label>
      </div>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-gray-500">Loading jobs…</p>}
        {error && <p className="text-red-600">Could not load jobs. Is the backend running?</p>}
        {jobs?.length === 0 && <p className="text-gray-500">No jobs match your filters yet.</p>}
        {jobs?.map((job) => <JobCard key={job.id} job={job} />)}
      </div>
    </div>
  )
}
