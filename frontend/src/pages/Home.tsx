import { Link } from 'react-router-dom'

export function Home() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-20 text-center">
      <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
        Professional growth, <span className="text-primary-600">without borders</span>
      </h1>
      <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">
        Ascend connects Korean-Canadian founders with global tech talent, and helps IEC
        working holiday participants and immigrants find real careers in Canada — with
        contracts, compliance guidance, and cross-border payments built in.
      </p>

      <div className="mt-10 flex justify-center gap-4">
        <Link
          to="/jobs"
          className="rounded-md bg-primary-600 px-6 py-3 font-medium text-white hover:bg-primary-700"
        >
          Browse Jobs
        </Link>
        <Link
          to="/signup"
          className="rounded-md border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50"
        >
          Post a Job
        </Link>
      </div>

      <div className="mt-20 grid grid-cols-1 gap-8 text-left sm:grid-cols-3">
        <div>
          <h3 className="font-semibold text-gray-900">For Founders</h3>
          <p className="mt-2 text-sm text-gray-600">
            Hire pre-vetted engineers across Korea and Canada without EOR middleman markup.
          </p>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">For Talent</h3>
          <p className="mt-2 text-sm text-gray-600">
            Find jobs matched to your visa status, get mentorship, and grow your career.
          </p>
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">For Everyone</h3>
          <p className="mt-2 text-sm text-gray-600">
            Simple contracts, compliance checklists, and cross-border payments — no guesswork.
          </p>
        </div>
      </div>
    </div>
  )
}
