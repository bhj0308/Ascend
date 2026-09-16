const GUIDES = [
  {
    title: 'Hiring an engineer in Korea from Canada',
    summary: 'Employment law, EOR options, and what to put in the contract.',
  },
  {
    title: 'IEC Working Holiday: finding a tech job in Canada',
    summary: 'Where jobs actually get posted, and how to network before you land.',
  },
  {
    title: 'Cross-border payments 101',
    summary: 'Comparing Wise, bank wires, and payroll providers for CAD ⇄ KRW.',
  },
  {
    title: 'Canadian tax basics for newcomers',
    summary: 'What to know about T1135, RRSP/TFSA, and filing your first return.',
  },
]

export function Guides() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900">Guides</h1>
      <p className="mt-2 text-gray-600">
        Plain-language references for cross-border hiring, visas, and payments. Not legal or tax
        advice — always confirm with a professional for your specific situation.
      </p>

      <div className="mt-6 space-y-4">
        {GUIDES.map((guide) => (
          <div key={guide.title} className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="font-semibold text-gray-900">{guide.title}</h2>
            <p className="mt-1 text-sm text-gray-600">{guide.summary}</p>
            <p className="mt-2 text-xs text-gray-400">Coming soon</p>
          </div>
        ))}
      </div>
    </div>
  )
}
