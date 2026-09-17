import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { clearSession } from '@/services/api'
import { deleteAccount, getMyProfile, updateProfile } from '@/services/profile'
import { useAuthStore } from '@/store/authStore'

interface FormState {
  first_name: string
  last_name: string
  bio: string
  city: string
  country: string
  visa_status: string
  skills: string
  languages: string
  mentor_available: boolean
}

function toFormState(user: {
  first_name?: string
  last_name?: string
  bio?: string
  city?: string
  country?: string
  visa_status?: string
  skills?: string[]
  languages?: string[]
  mentor_available?: boolean
}): FormState {
  return {
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    bio: user.bio || '',
    city: user.city || '',
    country: user.country || '',
    visa_status: user.visa_status || '',
    skills: (user.skills || []).join(', '),
    languages: (user.languages || []).join(', '),
    mentor_available: user.mentor_available || false,
  }
}

function splitList(value: string): string[] {
  const seen = new Set<string>()
  const result: string[] = []
  for (const item of value.split(',').map((s) => s.trim()).filter(Boolean)) {
    if (!seen.has(item)) {
      seen.add(item)
      result.push(item)
    }
  }
  return result
}

function extractDetail(error: unknown): string | undefined {
  return axios.isAxiosError(error)
    ? (error.response?.data as { detail?: string } | undefined)?.detail
    : undefined
}

export function Profile() {
  const navigate = useNavigate()
  const setUser = useAuthStore((s) => s.setUser)
  const [form, setForm] = useState<FormState | null>(null)
  const [saved, setSaved] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [password, setPassword] = useState('')

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ['me'],
    queryFn: getMyProfile,
  })

  useEffect(() => {
    if (profile) setForm(toFormState(profile))
  }, [profile])

  const saveMutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: (user) => {
      setUser(user)
      setForm(toFormState(user))
      setSaved(true)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => deleteAccount(password),
    onSuccess: () => {
      clearSession()
      navigate('/')
    },
  })

  if (isLoading || !form) {
    return <p className="mx-auto max-w-2xl px-4 py-10 text-gray-500">Loading…</p>
  }

  if (error || !profile) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <p className="text-red-600">Could not load profile.</p>
      </div>
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSaved(false)
    saveMutation.mutate({
      first_name: form.first_name,
      last_name: form.last_name,
      bio: form.bio,
      city: form.city,
      country: form.country,
      visa_status: form.visa_status,
      skills: splitList(form.skills),
      languages: splitList(form.languages),
      mentor_available: form.mentor_available,
    })
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>

      <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
        <span>{profile.email}</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            profile.email_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
          }`}
        >
          {profile.email_verified ? 'verified' : 'not verified'}
        </span>
      </div>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">First Name</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.first_name}
              onChange={(e) => setForm((f) => f && { ...f, first_name: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Last Name</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.last_name}
              onChange={(e) => setForm((f) => f && { ...f, last_name: e.target.value })}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Bio</label>
          <textarea
            rows={4}
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.bio}
            onChange={(e) => setForm((f) => f && { ...f, bio: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">City</label>
            <input
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.city}
              onChange={(e) => setForm((f) => f && { ...f, city: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Country</label>
            <input
              placeholder="CA / KR"
              maxLength={2}
              className="mt-1 w-full rounded-md border border-gray-300 p-2"
              value={form.country}
              onChange={(e) => setForm((f) => f && { ...f, country: e.target.value.toUpperCase() })}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Visa Status</label>
          <input
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.visa_status}
            onChange={(e) => setForm((f) => f && { ...f, visa_status: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Skills</label>
          <input
            placeholder="React, Python, AWS"
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.skills}
            onChange={(e) => setForm((f) => f && { ...f, skills: e.target.value })}
          />
          <p className="mt-1 text-xs text-gray-500">Comma-separated.</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Languages</label>
          <input
            placeholder="English, Korean"
            className="mt-1 w-full rounded-md border border-gray-300 p-2"
            value={form.languages}
            onChange={(e) => setForm((f) => f && { ...f, languages: e.target.value })}
          />
          <p className="mt-1 text-xs text-gray-500">Comma-separated.</p>
        </div>

        <label className="flex items-start gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            className="mt-1"
            checked={form.mentor_available}
            onChange={(e) => setForm((f) => f && { ...f, mentor_available: e.target.checked })}
          />
          <span>
            <span className="font-medium">Available as a mentor</span>
            <p className="text-xs text-gray-500">
              Shows you in the mentor directory so people can request mentorship.
            </p>
          </span>
        </label>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={saveMutation.isPending}
            className="rounded-md bg-primary-600 px-6 py-2 font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {saveMutation.isPending ? 'Saving…' : 'Save'}
          </button>
          {saved && !saveMutation.isPending && <span className="text-sm text-green-700">Saved</span>}
        </div>
        {saveMutation.isError && (
          <p className="text-sm text-red-600">{extractDetail(saveMutation.error) || 'Could not save profile.'}</p>
        )}
      </form>

      <div className="mt-12 rounded-lg border border-red-200 bg-red-50 p-5">
        <h2 className="text-sm font-semibold text-red-900">Danger zone</h2>

        {!deleting ? (
          <button
            onClick={() => setDeleting(true)}
            className="mt-3 rounded-md border border-red-300 px-5 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
          >
            Delete account
          </button>
        ) : (
          <div className="mt-3 space-y-3">
            <p className="text-sm text-red-800">
              This removes your personal details and disables login. Contracts, payments and
              messages you've shared with other users are kept, shown as "User #{profile.id}".
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700">Confirm your password</label>
              <input
                type="password"
                className="mt-1 w-full rounded-md border border-gray-300 p-2"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending || !password}
                className="rounded-md bg-red-600 px-5 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting…' : 'Confirm delete'}
              </button>
              <button
                onClick={() => {
                  setDeleting(false)
                  setPassword('')
                }}
                className="rounded-md border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700"
              >
                Cancel
              </button>
            </div>
            {deleteMutation.isError && (
              <p className="text-sm text-red-600">
                {extractDetail(deleteMutation.error) || 'Could not delete account.'}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
