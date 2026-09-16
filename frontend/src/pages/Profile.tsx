import { useAuthStore } from '@/store/authStore'

export function Profile() {
  const user = useAuthStore((s) => s.user)

  if (!user) return null

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">
        {user.first_name} {user.last_name}
      </h1>
      <p className="text-gray-500">{user.email}</p>
      <p className="mt-1 inline-block rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
        {user.user_type.replace('_', ' ')}
      </p>

      {user.bio && <p className="mt-4 text-gray-700">{user.bio}</p>}

      {user.skills && user.skills.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-900">Skills</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {user.skills.map((skill) => (
              <span key={skill} className="rounded-full bg-primary-50 px-3 py-1 text-xs text-primary-700">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
