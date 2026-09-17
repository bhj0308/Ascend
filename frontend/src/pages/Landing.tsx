import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LANDING, type Lang } from '@/content/landing'
import { useAuthStore } from '@/store/authStore'

function initialLang(): Lang {
  try {
    const saved = localStorage.getItem('lang')
    if (saved === 'en' || saved === 'ko') return saved
  } catch {
    /* storage unavailable (private mode) — fall through */
  }
  const language = typeof navigator !== 'undefined' ? navigator.language : undefined
  return language?.toLowerCase().startsWith('ko') ? 'ko' : 'en'
}

const primaryBtn =
  'inline-block rounded-md bg-primary-600 px-6 py-3 font-medium text-white hover:bg-primary-700'
const secondaryBtn =
  'inline-block rounded-md border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50'

export function Landing() {
  const [lang, setLang] = useState<Lang>(initialLang)
  const t = LANDING[lang]
  const user = useAuthStore((s) => s.user)

  const toggleLang = () => {
    const next: Lang = lang === 'en' ? 'ko' : 'en'
    setLang(next)
    try {
      localStorage.setItem('lang', next)
    } catch {
      /* ignore */
    }
  }

  // Logged-in founders go straight to posting; logged-out visitors start at signup.
  // Logged-in non-founders don't post jobs, so they only get browse CTAs.
  const isFounder = user?.user_type === 'founder'
  const canPost = !user || isFounder
  const postHref = isFounder ? '/jobs/new' : '/signup'
  const signupHref = user ? '/jobs' : '/signup'

  return (
    <div lang={lang}>
      {/* Hero */}
      <section className="mx-auto max-w-5xl px-4 pb-16 pt-14 text-center">
        <div className="flex justify-end">
          <button
            onClick={toggleLang}
            className="rounded-full border border-gray-300 px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
            aria-label="Switch language"
          >
            {t.toggle}
          </button>
        </div>
        <p className="mt-6 text-sm font-medium uppercase tracking-wide text-primary-600">
          {t.eyebrow}
        </p>
        <h1 className="mt-3 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
          {t.headline}
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600">{t.sub}</p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          {canPost && (
            <Link to={postHref} className={primaryBtn}>
              {t.ctaPost}
            </Link>
          )}
          <Link to="/jobs" className={canPost ? secondaryBtn : primaryBtn}>
            {t.ctaBrowse}
          </Link>
        </div>
      </section>

      {/* Two audiences */}
      <section className="mx-auto grid max-w-5xl gap-6 px-4 sm:grid-cols-2">
        {[
          { block: t.founders, href: postHref, showCta: canPost },
          { block: t.talent, href: '/jobs', showCta: true },
        ].map(({ block, href, showCta }) => (
          <div key={block.title} className="rounded-xl border border-gray-200 bg-white p-8">
            <h2 className="text-xl font-semibold text-gray-900">{block.title}</h2>
            <ul className="mt-4 space-y-3 text-gray-600">
              {block.bullets.map((b) => (
                <li key={b} className="flex gap-3">
                  <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-primary-500" aria-hidden />
                  <span>{b}</span>
                </li>
              ))}
            </ul>
            {showCta && (
              <Link to={href} className={`${primaryBtn} mt-6`}>
                {block.cta}
              </Link>
            )}
          </div>
        ))}
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-5xl px-4 pt-20">
        <h2 className="text-center text-2xl font-bold text-gray-900">{t.how.title}</h2>
        <ol className="mt-10 grid gap-8 sm:grid-cols-3">
          {t.how.steps.map((step, i) => (
            <li key={step.title}>
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-sm font-bold text-white">
                {i + 1}
              </div>
              <h3 className="mt-4 font-semibold text-gray-900">{step.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-4 pt-20">
        <h2 className="text-center text-2xl font-bold text-gray-900">{t.features.title}</h2>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {t.features.items.map((f) => (
            <div key={f.title} className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="font-semibold text-gray-900">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Straight talk */}
      <section className="mx-auto max-w-5xl px-4 pt-20">
        <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-8">
          <h2 className="text-xl font-semibold text-yellow-900">{t.straight.title}</h2>
          <ul className="mt-4 space-y-2 text-sm text-yellow-900">
            {t.straight.items.map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto max-w-5xl px-4 pb-8 pt-20 text-center">
        <p className="text-lg text-gray-700">{t.final.line}</p>
        <Link to={signupHref} className={`${primaryBtn} mt-6`}>
          {user ? t.final.ctaLoggedIn : t.final.cta}
        </Link>
      </section>
    </div>
  )
}
