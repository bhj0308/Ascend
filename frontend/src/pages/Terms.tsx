// DRAFT placeholder. Replace with lawyer-reviewed terms before marketing the
// product. Kept deliberately plain so the actual product behavior is stated
// accurately rather than promising things the app doesn't do.

const LAST_UPDATED = 'September 2026'

export function Terms() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-6 rounded-md border border-yellow-300 bg-yellow-50 p-3 text-sm text-yellow-800">
        Draft — these terms have not yet been reviewed by a lawyer.
      </div>

      <h1 className="text-2xl font-bold text-gray-900">Terms of Service</h1>
      <p className="mt-1 text-sm text-gray-500">Last updated {LAST_UPDATED}</p>

      <div className="mt-6 space-y-6 text-sm leading-relaxed text-gray-700">
        <section>
          <h2 className="font-semibold text-gray-900">1. What Ascend is</h2>
          <p>
            Ascend is a marketplace that connects hiring companies with tech talent and provides
            tools around that relationship: job listings, applications, contract drafts,
            mentorship, messaging, and a record of payments. Ascend is not a party to any
            employment or contractor agreement formed between users.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">2. Accounts</h2>
          <p>
            You must be at least 18 and provide accurate information. You are responsible for
            activity under your account and for keeping your password confidential.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">3. Contracts and guides are not legal advice</h2>
          <p>
            Contract templates, checklists, and guides are general scaffolding only. They are
            not legal, tax, or immigration advice and may not be suitable for your situation.
            Have any agreement reviewed by a qualified professional before relying on it. The
            in-app "Sign" action records an acknowledgment inside Ascend; it is not a legal
            electronic signature.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">4. Payments are records, not transfers</h2>
          <p>
            In this version Ascend only records payments for your history. It does not move
            money, hold funds, or process card or bank details.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">5. Acceptable use</h2>
          <p>
            Do not post false job listings, misrepresent your identity or qualifications,
            harass other users, or use Ascend for anything unlawful. We may suspend accounts
            that do.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">6. No warranty; limitation of liability</h2>
          <p>
            Ascend is provided "as is" during this early-access period. To the extent permitted
            by law, we are not liable for indirect or consequential losses, or for outcomes of
            agreements formed between users.
          </p>
        </section>
        <section>
          <h2 className="font-semibold text-gray-900">7. Changes and contact</h2>
          <p>
            We may update these terms; continued use after an update means you accept it.
            Questions: <span className="font-mono">legal@[your-domain]</span> (placeholder).
            Governing law: [jurisdiction to be confirmed].
          </p>
        </section>
      </div>
    </div>
  )
}
