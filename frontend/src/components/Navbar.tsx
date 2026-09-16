import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { logout } from '@/services/auth'

export function Navbar() {
  const { user, isAuthenticated, clear } = useAuthStore()

  const handleLogout = () => {
    logout()
    clear()
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-xl font-bold text-primary-600">
          Ascend
        </Link>

        <div className="flex items-center gap-6 text-sm font-medium text-gray-700">
          <Link to="/jobs" className="hover:text-primary-600">
            Browse Jobs
          </Link>
          <Link to="/guides" className="hover:text-primary-600">
            Guides
          </Link>

          {isAuthenticated ? (
            <>
              {user?.user_type === 'founder' && (
                <Link to="/jobs/new" className="hover:text-primary-600">
                  Post a Job
                </Link>
              )}
              <Link to="/profile" className="hover:text-primary-600">
                {user?.first_name || 'Profile'}
              </Link>
              <button onClick={handleLogout} className="hover:text-primary-600">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:text-primary-600">
                Log in
              </Link>
              <Link
                to="/signup"
                className="rounded-md bg-primary-600 px-4 py-2 text-white hover:bg-primary-700"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
