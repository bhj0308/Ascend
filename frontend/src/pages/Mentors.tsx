import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getMentors } from '@/services/mentorships'

export function Mentors() {
  const [skill, setSkill] = useState('')
  const [country, setCountry] = useState('')
  const [applied, setApplied] = useState({ skill: '', country: '' })

  const { data: mentors, isLoading, error } = useQuery({
    queryKey: ['mentors', applied.skill, applied.country],
    queryFn: () => getMentors({ skill: applied.skill || undefined, country: applied.country || undefined }),
  })

  const handleApply = (e: React.FormEvent) => {
    e.preventDefault()
    setApplied({ skill: skill.trim(), country: country.trim() })
  }

  const handleClear = () => {
    setSkill('')
    setCountry('')
    setApplied({ skill: '', country: '' })
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Find a Mentor</h1>

      <form onSubmit={handleApply} className="mt-6 flex flex-wrap items-end gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Skill</label>
          <input
            placeholder="React"
            className="mt-1 w-48 rounded-md border border-gray-300 p-2"
            value={skill}
            onChange={(e) => setSkill(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Country</label>
          <input
            placeholder="CA / KR"
            maxLength={2}
            className="mt-1 w-32 rounded-md border border-gray-300 p-2"
            value={country}
            onChange={(e) => setCountry(e.target.value.toUpperCase())}
          />
        </div>
        <button
          type="submit"
          className="rounded-md bg-primary-600 px-5 py-2 font-medium text-white hover:bg-primary-700"
        >
          Apply
        </button>
        {(applied.skill || applied.country) && (
          <button
            type="button"
            onClick={handleClear}
            className="rounded-md border border-gray-300 px-5 py-2 font-medium text-gray-700"
          >
            Clear
          </button>
        )}
      </form>

      <div className="mt-8">
        {isLoading && <p className="text-gray-500">Loading mentors…</p>}
        {error && <p className="text-red-600">Could not load mentors.</p>}
        {mentors?.length === 0 && (
          <p className="text-gray-500">No mentors match yet — try clearing the filters.</p>
        )}

        {mentors && mentors.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3">
            {mentors.map((mentor) => {
              const name = [mentor.first_name, mentor.last_name].filter(Boolean).join(' ') || `User #${mentor.id}`
              const location = [mentor.city, mentor.country].filter(Boolean).join(', ')
              return (
                <Link
                  key={mentor.id}
                  to={`/users/${mentor.id}`}
                  className="rounded-lg border border-gray-200 bg-white p-5 hover:border-primary-300"
                >
                  <h3 className="font-semibold text-gray-900">{name}</h3>
                  <p className="mt-1 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
                    {mentor.user_type.replace('_', ' ')}
                  </p>
                  {location && <p className="mt-2 text-sm text-gray-500">{location}</p>}
                  {mentor.skills && mentor.skills.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {mentor.skills.slice(0, 6).map((s) => (
                        <span
                          key={s}
                          className="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-700"
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
