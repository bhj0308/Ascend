import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { createJob } from '@/services/jobs'
import { describeError } from '@/utils/errors'
import type { Job } from '@/types'

export function JobNew() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '',
    description: '',
    company_name: '',
    location_country: '',
    location_city: '',
    remote_ok: false,
    visa_sponsorship: false,
    iec_friendly: false,
  })

  const mutation = useMutation({
    mutationFn: (payload: Partial<Job>) => createJob(payload),
    onSuccess: (job) => navigate(`/jobs/${job.id}`),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(form)
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Post a Job</h1>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Job Title</label>
          <input
            required
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Company Name</label>
          <input
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.company_name}
            onChange={(e) => setForm((f) => ({ ...f, company_name: e.target.value }))}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            required
            rows={6}
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Country</label>
            <input
              placeholder="CA / KR"
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.location_country}
              onChange={(e) => setForm((f) => ({ ...f, location_country: e.target.value }))}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">City</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.location_city}
              onChange={(e) => setForm((f) => ({ ...f, location_city: e.target.value }))}
            />
          </div>
        </div>

        <div className="flex flex-wrap gap-4 text-sm text-gray-700">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.remote_ok}
              onChange={(e) => setForm((f) => ({ ...f, remote_ok: e.target.checked }))}
            />
            Remote OK
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.visa_sponsorship}
              onChange={(e) => setForm((f) => ({ ...f, visa_sponsorship: e.target.checked }))}
            />
            Visa Sponsorship
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.iec_friendly}
              onChange={(e) => setForm((f) => ({ ...f, iec_friendly: e.target.checked }))}
            />
            IEC Friendly
          </label>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Posting…' : 'Post Job'}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-600">
            {describeError(mutation.error, 'Could not post job.')}
          </p>
        )}
      </form>
    </div>
  )
}
