import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { logout } from '@/services/auth'

const linkCls = 'hover:text-primary-600'

export function Navbar() {
  const { user, isAuthenticated, clear } = useAuthStore()
  const [open, setOpen] = useState(false)
  const close = () => setOpen(false)

  const handleLogout = () => {
    logout()
    clear()
    close()
  }

  // Rendered twice: as the desktop row and inside the mobile panel.
  const links = (
    <>
      <Link to="/jobs" className={linkCls} onClick={close}>
        Browse Jobs
      </Link>
      <Link to="/guides" className={linkCls} onClick={close}>
        Guides
      </Link>

      {isAuthenticated ? (
        <>
          {user?.user_type === 'founder' && (
            <Link to="/jobs/new" className={linkCls} onClick={close}>
              Post a Job
            </Link>
          )}
          <Link to="/contracts" className={linkCls} onClick={close}>
            Contracts
          </Link>
          <Link to="/mentorships" className={linkCls} onClick={close}>
            Mentorships
          </Link>
          <Link to="/mentors" className={linkCls} onClick={close}>
            Find a Mentor
          </Link>
          <Link to="/payments" className={linkCls} onClick={close}>
            Payments
          </Link>
          <Link to="/messages" className={linkCls} onClick={close}>
            Messages
          </Link>
          <Link to="/profile" className={linkCls} onClick={close}>
            {user?.first_name || 'Profile'}
          </Link>
          <button onClick={handleLogout} className={`${linkCls} text-left`}>
            Log out
          </button>
        </>
      ) : (
        <>
          <Link to="/login" className={linkCls} onClick={close}>
            Log in
          </Link>
          <Link
            to="/signup"
            onClick={close}
            className="rounded-md bg-primary-600 px-4 py-2 text-center text-white hover:bg-primary-700"
          >
            Sign up
          </Link>
        </>
      )}
    </>
  )

  return (
    <nav className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-xl font-bold text-primary-600" onClick={close}>
          Ascend
        </Link>

        {/* Desktop */}
        <div className="hidden items-center gap-6 text-sm font-medium text-gray-700 sm:flex">
          {links}
        </div>

        {/* Mobile toggle */}
        <button
          type="button"
          className="rounded-md p-2 text-gray-700 hover:bg-gray-100 sm:hidden"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          onClick={() => setOpen((o) => !o)}
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden>
            {open ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile panel */}
      {open && (
        <div className="flex flex-col gap-4 border-t border-gray-200 px-4 py-4 text-sm font-medium text-gray-700 sm:hidden">
          {links}
        </div>
      )}
    </nav>
  )
}
