import { Link } from 'react-router-dom'

export function Footer() {
  return (
    <footer className="mt-16 border-t border-gray-200 py-6 text-xs text-gray-500">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-center gap-x-6 gap-y-2 px-4">
        <span>© {new Date().getFullYear()} Ascend</span>
        <Link to="/terms" className="hover:text-primary-600">
          Terms
        </Link>
        <Link to="/privacy" className="hover:text-primary-600">
          Privacy
        </Link>
        <span>Contract templates and guides are not legal advice.</span>
      </div>
    </footer>
  )
}
