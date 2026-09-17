import { Link } from 'react-router-dom'
import type { Job } from '@/types'
import { formatCents } from '@/utils/money'

function formatSalary(job: Job): string | null {
  if (!job.salary_min && !job.salary_max) return null
  const fmt = (cents: number) => formatCents(cents, job.salary_currency)

  if (job.salary_min && job.salary_max) return `${fmt(job.salary_min)} – ${fmt(job.salary_max)}`
  return fmt(job.salary_min || job.salary_max || 0)
}

export function JobCard({ job }: { job: Job }) {
  const salary = formatSalary(job)

  return (
    <Link
      to={`/jobs/${job.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-5 transition hover:border-primary-300 hover:shadow-sm"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
          {job.company_name && <p className="text-sm text-gray-500">{job.company_name}</p>}
        </div>
        {job.remote_ok && (
          <span className="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
            Remote OK
          </span>
        )}
      </div>

      <p className="mt-3 line-clamp-2 text-sm text-gray-600">{job.description}</p>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
        {salary && (
          <span className="rounded-full bg-gray-100 px-3 py-1 font-medium text-gray-700">
            {salary}
          </span>
        )}
        {job.location_city && (
          <span className="rounded-full bg-gray-100 px-3 py-1 text-gray-700">
            {job.location_city}
            {job.location_country ? `, ${job.location_country}` : ''}
          </span>
        )}
        {job.visa_sponsorship && (
          <span className="rounded-full bg-blue-100 px-3 py-1 font-medium text-blue-700">
            Visa Sponsorship
          </span>
        )}
        {job.iec_friendly && (
          <span className="rounded-full bg-purple-100 px-3 py-1 font-medium text-purple-700">
            IEC Friendly
          </span>
        )}
      </div>
    </Link>
  )
}
