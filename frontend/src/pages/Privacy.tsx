// DRAFT placeholder. Replace with lawyer-reviewed policy before marketing the
// product. Statements below describe what the app actually does today; keep
// them in sync with the code (e.g. no card/bank data is collected).

const LAST_UPDATED = 'September 2026'

export function Privacy() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-6 rounded-md border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-800">
        Draft — this policy has not yet been reviewed by a lawyer.
      </div>

      <h1 className="text-2xl font-bold text-gray-900">Privacy Policy</h1>
      <p className="mt-1 text-sm text-gray-500">Last updated {LAST_UPDATED}</p>

      <div className="mt-6 space-y-6 text-sm leading-relaxed text-gray-700">
        <section>
          <h2 className="font-semibold text-gray-900">What we collect</h2>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            <li>Account details: email, name, password (stored only as a bcrypt hash).</li>
            <li>Profile details you choose to add: bio, skills, languages, location, visa status.</li>
            <li>
              Content you create: job listings, applications, contract terms, mentorship
              requests, messages, and payment records (amount, currency, counterparty).
            </li>
            <li>
              We do <strong>not</strong> collect card numbers or bank account details. Payments
              are recorded, not processed.
            </li>
          </ul>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">How we use it</h2>
          <p>
            To run the service: showing your profile to people you interact with, delivering
            messages, and keeping your contract and payment history. We do not sell personal
            data or use it for advertising.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">Who can see what</h2>
          <p>
            Your public profile (name, type, bio, skills, languages, visa status, location) is
            visible to signed-in users. Contracts, payments, and messages are visible only to
            the parties involved. Your email is never shown to other users — not on your
            profile, and not as a name anywhere else in the app.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">Storage and security</h2>
          <p>
            Data is stored in a managed PostgreSQL database with our hosting provider and
            transmitted over HTTPS. Sign-in uses short-lived tokens kept in your browser's local
            storage; we do not use tracking cookies.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">Your choices</h2>
          <p>
            You can edit your profile at any time. You can delete your account yourself from the
            Profile page: your personal details (name, email, bio, skills, location, visa status)
            are removed and sign-in is disabled. Contracts, payment records, and messages that
            other users are party to are kept, attributed to an anonymous "User #id", because
            they are the other party's records too. Questions:{' '}
            <span className="font-mono">privacy@[your-domain]</span> (placeholder).
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">Contact</h2>
          <p>
            Questions about this policy: <span className="font-mono">privacy@[your-domain]</span>{' '}
            (placeholder).
          </p>
        </section>
      </div>
    </div>
  )
}
