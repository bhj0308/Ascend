import { useRef, useState, type CSSProperties, type PointerEvent, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { LANDING, type LandingCopy, type Lang } from '@/content/landing'
import { usePrefersReducedMotion, useReveal } from '@/hooks/useReveal'
import { browseJobs } from '@/services/jobs'
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

const glowBtn =
  'group inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-sky-400 to-primary-500 px-7 py-3.5 font-semibold text-white shadow-lg shadow-sky-500/30 transition duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-sky-400/40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300'
const glassBtn =
  'inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-7 py-3.5 font-semibold text-white backdrop-blur transition duration-300 hover:-translate-y-0.5 hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-300'
const sectionTitle = 'text-center text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl'

// Stroke icons (24px grid), one path each.
const ICONS = {
  arrow: 'M5 12h14M13 6l6 6-6 6',
  check: 'M5 13l4 4L19 7',
  briefcase: 'M4 8h16v11H4zM9 8V5h6v3M4 13h16',
  cap: 'M12 4l9 5-9 5-9-5zM7 11.5V16c0 1.4 2.2 3 5 3s5-1.6 5-3v-4.5',
  document: 'M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6',
  users: 'M9 11a4 4 0 100-8 4 4 0 000 8zM3 21v-1a6 6 0 0112 0v1M17 11a3 3 0 100-6M21 21v-1a5 5 0 00-3-4.6',
  chat: 'M4 5h16v11H9l-5 4z',
  receipt: 'M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6',
  lock: 'M6 11h12v10H6zM8 11V8a4 4 0 018 0v3',
  search: 'M11 18a7 7 0 100-14 7 7 0 000 14zM20 20l-4-4',
  info: 'M12 21a9 9 0 100-18 9 9 0 000 18zM12 11v5M12 8h.01',
}
// Same order as LANDING[lang].features.items.
const FEATURE_ICONS = [ICONS.search, ICONS.document, ICONS.users, ICONS.chat, ICONS.receipt, ICONS.lock]
// Bento layout for the six features: wide, narrow / narrow, wide / wide, narrow.
const FEATURE_SPANS = [true, false, false, true, true, false]

function Icon({ d, className = 'h-5 w-5' }: { d: string; className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d={d} />
    </svg>
  )
}

function Reveal({
  children,
  delay = 0,
  className = '',
}: {
  children: ReactNode
  delay?: number
  className?: string
}) {
  const { ref, visible } = useReveal<HTMLDivElement>()
  return (
    <div
      ref={ref}
      className={`reveal ${visible ? 'is-visible' : ''} ${className}`}
      style={{ '--reveal-delay': `${delay}ms` } as CSSProperties}
    >
      {children}
    </div>
  )
}

function Ping({ color }: { color: string }) {
  return (
    <span className="relative flex h-2 w-2" aria-hidden>
      <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${color}`} />
      <span className={`relative inline-flex h-2 w-2 rounded-full ${color}`} />
    </span>
  )
}

function Aurora({ small = false }: { small?: boolean }) {
  const size = small ? 'h-72 w-72' : 'h-[32rem] w-[32rem]'
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 -z-10">
      <div className={`absolute -left-32 -top-40 ${size} animate-aurora rounded-full bg-primary-600/40 blur-3xl`} />
      <div
        className={`absolute -right-24 top-0 ${size} animate-aurora rounded-full bg-sky-500/30 blur-3xl [animation-delay:-6s]`}
      />
      <div
        className={`absolute -bottom-48 left-1/3 ${size} animate-aurora rounded-full bg-fuchsia-500/20 blur-3xl [animation-delay:-12s]`}
      />
      <div className="bg-grid absolute inset-0" />
    </div>
  )
}

const floatCard =
  'rounded-2xl border border-white/10 bg-slate-900/80 p-4 shadow-xl shadow-black/40 backdrop-blur-xl'

// Decorative product preview: a Seoul ⇄ Toronto route with floating feature cards.
function HeroVisual({ preview, reduced }: { preview: LandingCopy['preview']; reduced: boolean }) {
  const route = 'M 20 115 Q 160 -25 300 115'
  return (
    <div aria-hidden className="relative mx-auto w-full max-w-md animate-fade-up py-14 [animation-delay:300ms]">
      <div className="relative rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl sm:pb-28 sm:pt-20">
        <svg viewBox="0 0 320 140" className="w-full">
          <defs>
            <linearGradient id="landing-route" x1="0" x2="1">
              <stop offset="0%" stopColor="#38bdf8" />
              <stop offset="100%" stopColor="#c084fc" />
            </linearGradient>
          </defs>
          <path
            d={route}
            fill="none"
            stroke="url(#landing-route)"
            strokeWidth="2.5"
            strokeDasharray="6 14"
            strokeLinecap="round"
            className="animate-dash"
          />
          <circle cx="20" cy="115" r="16" fill="#38bdf8" opacity="0.15" />
          <circle cx="20" cy="115" r="6" fill="#38bdf8" />
          <circle cx="300" cy="115" r="16" fill="#c084fc" opacity="0.15" />
          <circle cx="300" cy="115" r="6" fill="#c084fc" />
          {!reduced && (
            <circle r="5" fill="#fff">
              <animateMotion dur="3.5s" repeatCount="indefinite" path={route} />
            </circle>
          )}
        </svg>
        <div className="mt-2 flex items-center justify-between text-xs font-semibold uppercase tracking-widest text-slate-400">
          <span>{preview.route.from}</span>
          <span>{preview.route.to}</span>
        </div>
        <p className="mt-3 text-center text-sm font-medium text-slate-200">{preview.route.caption}</p>
      </div>

      <div className={`absolute -left-3 top-0 hidden w-56 animate-float sm:block lg:-left-12 ${floatCard}`}>
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/20 text-sky-300">
            <Icon d={ICONS.briefcase} />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">{preview.job.title}</p>
            <p className="text-xs text-slate-400">{preview.job.meta}</p>
          </div>
        </div>
        <span className="mt-3 inline-flex rounded-full bg-emerald-400/15 px-2.5 py-1 text-xs font-medium text-emerald-300">
          {preview.job.badge}
        </span>
      </div>

      <div
        className={`absolute -right-3 top-10 hidden animate-float items-center gap-3 [animation-delay:-2s] sm:flex lg:-right-10 ${floatCard}`}
      >
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-fuchsia-500/20 text-fuchsia-300">
          <Icon d={ICONS.document} />
        </div>
        <div>
          <p className="text-xs text-slate-400">{preview.contract.label}</p>
          <p className="flex items-center gap-1 text-sm font-semibold text-emerald-300">
            <Icon d={ICONS.check} className="h-4 w-4" />
            {preview.contract.status}
          </p>
        </div>
      </div>

      <div
        className={`absolute bottom-6 left-8 hidden w-64 animate-float [animation-delay:-4s] sm:block ${floatCard}`}
      >
        <div className="flex items-start gap-3">
          <div className="h-9 w-9 shrink-0 rounded-full bg-gradient-to-br from-sky-400 to-fuchsia-500" />
          <div className="min-w-0">
            <p className="flex items-center gap-2 text-xs font-semibold text-sky-300">
              {preview.message.from}
              <Ping color="bg-sky-400" />
            </p>
            <p className="mt-0.5 truncate text-sm text-slate-200">{preview.message.body}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Real open jobs from the API, scrolling as a marquee. Hidden when there are none.
function LiveRoles({ t, reduced }: { t: LandingCopy; reduced: boolean }) {
  const { data: jobs } = useQuery({
    queryKey: ['jobs', 'landing'],
    queryFn: () => browseJobs(),
    staleTime: 60_000,
  })
  if (!jobs || jobs.length === 0) return null

  const recent = jobs.slice(0, 12)
  // The loop translates by -50%, so the track is the row twice; short rows are repeated
  // first so the strip never shows a gap on wide screens.
  let row = recent
  while (row.length < 8) row = row.concat(recent)
  const track = reduced ? recent : row.concat(row)

  return (
    <section className="border-t border-white/5 bg-slate-950 py-8 text-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4">
        <p className="flex items-center gap-3 text-sm font-semibold">
          <Ping color="bg-emerald-400" />
          {t.live.title}
          <span className="font-normal text-slate-400">· {t.live.count(jobs.length)}</span>
        </p>
        <Link to="/jobs" className="group inline-flex items-center gap-1 text-sm text-sky-300 hover:text-sky-200">
          {t.live.viewAll}
          <Icon d={ICONS.arrow} className="h-4 w-4 transition-transform group-hover:translate-x-1" />
        </Link>
      </div>
      <div className={`mt-5 ${reduced ? 'overflow-x-auto' : 'mask-fade-x overflow-clip'}`}>
        <ul
          className={`flex w-max gap-3 px-4 ${reduced ? '' : 'animate-marquee hover:[animation-play-state:paused]'}`}
        >
          {track.map((job, i) => {
            const copy = i >= recent.length
            const flag = job.iec_friendly
              ? t.flags.iec
              : job.visa_sponsorship
                ? t.flags.visa
                : job.remote_ok
                  ? t.flags.remote
                  : null
            return (
              <li key={`${job.id}-${i}`} aria-hidden={copy || undefined}>
                <Link
                  to={`/jobs/${job.id}`}
                  tabIndex={copy ? -1 : undefined}
                  className="flex items-center gap-3 whitespace-nowrap rounded-full border border-white/10 bg-white/5 py-2 pl-2 pr-4 text-sm transition hover:border-sky-400/50 hover:bg-white/10"
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-sky-400 to-primary-500 text-xs font-bold">
                    {(job.company_name || job.title).charAt(0).toUpperCase()}
                  </span>
                  <span className="font-medium">{job.title}</span>
                  {job.company_name && <span className="text-slate-400">{job.company_name}</span>}
                  {flag && (
                    <span className="rounded-full bg-emerald-400/15 px-2 py-0.5 text-xs text-emerald-300">
                      {flag}
                    </span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </div>
    </section>
  )
}

function HowItWorks({ how }: { how: LandingCopy['how'] }) {
  const { ref, visible } = useReveal<HTMLOListElement>(0.3)
  return (
    <section className="bg-white py-24">
      <div className="mx-auto max-w-6xl px-4">
        <Reveal>
          <h2 className={sectionTitle}>{how.title}</h2>
        </Reveal>
        <ol
          ref={ref}
          className={`relative mt-16 grid gap-12 md:grid-cols-3 md:before:absolute md:before:left-[16.66%] md:before:right-[16.66%] md:before:top-7 md:before:h-px md:before:origin-left md:before:bg-gradient-to-r md:before:from-sky-400 md:before:via-indigo-400 md:before:to-fuchsia-400 md:before:transition-transform md:before:duration-1000 md:before:content-[''] ${
            visible ? 'md:before:scale-x-100' : 'md:before:scale-x-0'
          }`}
        >
          {how.steps.map((step, i) => (
            <li
              key={step.title}
              className={`reveal relative text-center ${visible ? 'is-visible' : ''}`}
              style={{ '--reveal-delay': `${150 + i * 200}ms` } as CSSProperties}
            >
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-lg font-bold shadow-lg shadow-indigo-500/20 ring-1 ring-white/10">
                <span className="bg-gradient-to-br from-sky-300 to-fuchsia-300 bg-clip-text text-transparent">
                  {i + 1}
                </span>
              </div>
              <h3 className="mt-6 text-lg font-semibold text-gray-900">{step.title}</h3>
              <p className="mx-auto mt-2 max-w-xs text-gray-600">{step.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}

export function Landing() {
  const [lang, setLang] = useState<Lang>(initialLang)
  const t = LANDING[lang]
  const user = useAuthStore((s) => s.user)
  const reduced = usePrefersReducedMotion()
  const heroRef = useRef<HTMLElement>(null)

  const toggleLang = () => {
    const next: Lang = lang === 'en' ? 'ko' : 'en'
    setLang(next)
    try {
      localStorage.setItem('lang', next)
    } catch {
      /* ignore */
    }
  }

  // Spotlight follows the mouse across the hero. Written to CSS variables, not state,
  // so moving the mouse doesn't re-render the page.
  const onHeroPointerMove = (e: PointerEvent<HTMLElement>) => {
    const el = heroRef.current
    if (!el || e.pointerType !== 'mouse') return
    const rect = el.getBoundingClientRect()
    el.style.setProperty('--spot-x', `${e.clientX - rect.left}px`)
    el.style.setProperty('--spot-y', `${e.clientY - rect.top}px`)
  }

  // Logged-in founders go straight to posting; logged-out visitors start at signup.
  // Logged-in non-founders don't post jobs, so they only get browse CTAs.
  const isFounder = user?.user_type === 'founder'
  const canPost = !user || isFounder
  const postHref = isFounder ? '/jobs/new' : '/signup'
  const signupHref = user ? '/jobs' : '/signup'

  const audiences = [
    { block: t.founders, href: postHref, showCta: canPost, icon: ICONS.briefcase, accent: 'from-sky-400 to-primary-600' },
    { block: t.talent, href: '/jobs', showCta: true, icon: ICONS.cap, accent: 'from-fuchsia-500 to-indigo-500' },
  ]

  return (
    <div lang={lang} className="overflow-x-clip">
      {/* Hero */}
      <section
        ref={heroRef}
        onPointerMove={onHeroPointerMove}
        className="relative isolate overflow-clip bg-slate-950 text-white"
      >
        <Aurora />
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10"
          style={{
            background:
              'radial-gradient(600px circle at var(--spot-x, 70%) var(--spot-y, 40%), rgba(56, 189, 248, 0.12), transparent 60%)',
          }}
        />

        <div className="mx-auto flex max-w-6xl justify-end px-4 pt-6">
          <button
            onClick={toggleLang}
            className="rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-medium text-slate-200 backdrop-blur transition hover:bg-white/10"
            aria-label="Switch language"
          >
            {t.toggle}
          </button>
        </div>

        <div className="mx-auto grid max-w-6xl items-center gap-6 px-4 pb-16 pt-8 lg:grid-cols-[1.1fr_0.9fr] lg:gap-14 lg:pb-24">
          <div className="text-center lg:text-left">
            <p className="inline-flex animate-fade-up items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-medium text-sky-200 backdrop-blur">
              <Ping color="bg-sky-400" />
              {t.eyebrow}
            </p>
            <h1 className="mt-6 animate-fade-up text-4xl font-extrabold leading-[1.1] tracking-tight [animation-delay:100ms] sm:text-6xl lg:text-7xl">
              <span className="animate-shimmer bg-gradient-to-r from-white via-sky-300 to-white bg-[length:200%_auto] bg-clip-text text-transparent">
                {t.headline}
              </span>
            </h1>
            <p className="mx-auto mt-6 max-w-xl animate-fade-up text-lg text-slate-300 [animation-delay:200ms] lg:mx-0">
              {t.sub}
            </p>
            <div className="mt-10 flex animate-fade-up flex-wrap justify-center gap-4 [animation-delay:300ms] lg:justify-start">
              {canPost && (
                <Link to={postHref} className={glowBtn}>
                  {t.ctaPost}
                  <Icon d={ICONS.arrow} className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              )}
              <Link to="/jobs" className={canPost ? glassBtn : glowBtn}>
                {t.ctaBrowse}
                {!canPost && (
                  <Icon d={ICONS.arrow} className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                )}
              </Link>
            </div>
            <ul className="mt-8 flex animate-fade-up flex-wrap justify-center gap-x-6 gap-y-2 text-sm text-slate-400 [animation-delay:400ms] lg:justify-start">
              {t.heroNotes.map((note) => (
                <li key={note} className="flex items-center gap-2">
                  <Icon d={ICONS.check} className="h-4 w-4 text-sky-400" />
                  {note}
                </li>
              ))}
            </ul>
          </div>

          <HeroVisual preview={t.preview} reduced={reduced} />
        </div>
      </section>

      <LiveRoles t={t} reduced={reduced} />

      {/* Two audiences */}
      <section className="bg-gray-50 py-24">
        <div className="mx-auto grid max-w-6xl gap-6 px-4 md:grid-cols-2">
          {audiences.map(({ block, href, showCta, icon, accent }, i) => (
            <Reveal key={block.title} delay={i * 120} className="h-full">
              <div className="group relative h-full overflow-clip rounded-3xl border border-gray-200 bg-white p-8 shadow-sm transition duration-300 hover:-translate-y-1 hover:shadow-xl sm:p-10">
                <div
                  aria-hidden
                  className={`pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-gradient-to-br ${accent} opacity-20 blur-2xl transition duration-500 group-hover:scale-150 group-hover:opacity-30`}
                />
                <div
                  className={`relative flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br ${accent} text-white shadow-lg`}
                >
                  <Icon d={icon} className="h-6 w-6" />
                </div>
                <h2 className="relative mt-6 text-2xl font-bold text-gray-900">{block.title}</h2>
                <ul className="relative mt-5 space-y-3 text-gray-600">
                  {block.bullets.map((b) => (
                    <li key={b} className="flex gap-3">
                      <Icon d={ICONS.check} className="mt-0.5 h-5 w-5 shrink-0 text-primary-500" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
                {showCta && (
                  <Link
                    to={href}
                    className="group/cta relative mt-8 inline-flex items-center gap-2 font-semibold text-primary-600 hover:text-primary-700"
                  >
                    {block.cta}
                    <Icon d={ICONS.arrow} className="h-4 w-4 transition-transform group-hover/cta:translate-x-1" />
                  </Link>
                )}
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <HowItWorks how={t.how} />

      {/* Features */}
      <section className="bg-gray-50 pb-16 pt-24">
        <div className="mx-auto max-w-6xl px-4">
          <Reveal>
            <h2 className={sectionTitle}>{t.features.title}</h2>
          </Reveal>
          <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {t.features.items.map((f, i) => (
              <Reveal
                key={f.title}
                delay={i * 80}
                className={`h-full ${FEATURE_SPANS[i] ? 'lg:col-span-2' : ''}`}
              >
                <div className="group relative h-full overflow-clip rounded-2xl border border-gray-200 bg-white p-6 transition duration-300 hover:-translate-y-1 hover:shadow-xl">
                  <div
                    aria-hidden
                    className="absolute inset-0 bg-gradient-to-br from-sky-50 via-white to-fuchsia-50 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
                  />
                  <div className="relative">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-950 text-sky-300 transition duration-300 group-hover:-rotate-6 group-hover:scale-110">
                      <Icon d={FEATURE_ICONS[i] ?? ICONS.check} />
                    </div>
                    <h3 className="mt-5 font-semibold text-gray-900">{f.title}</h3>
                    <p className="mt-2 text-sm text-gray-600">{f.body}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* Straight talk */}
      <section className="bg-gray-50 pb-24">
        <Reveal className="mx-auto max-w-4xl px-4">
          <div className="rounded-3xl border border-amber-200 bg-gradient-to-br from-amber-50 to-orange-50 p-8 sm:p-10">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-100 text-amber-700">
                <Icon d={ICONS.info} />
              </div>
              <h2 className="text-xl font-semibold text-amber-950">{t.straight.title}</h2>
            </div>
            <ul className="mt-5 space-y-3 text-amber-900">
              {t.straight.items.map((item) => (
                <li key={item} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" aria-hidden />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </section>

      {/* Final CTA */}
      <section className="bg-gray-50 px-4">
        <Reveal className="mx-auto max-w-6xl">
          <div className="relative isolate overflow-clip rounded-3xl bg-slate-950 px-6 py-16 text-center text-white sm:px-16 sm:py-20">
            <Aurora small />
            <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight sm:text-5xl">
              <span className="animate-shimmer bg-gradient-to-r from-white via-sky-300 to-white bg-[length:200%_auto] bg-clip-text text-transparent">
                {t.headline}
              </span>
            </h2>
            <p className="mt-4 text-lg text-slate-300">{t.final.line}</p>
            <Link to={signupHref} className={`${glowBtn} mt-8`}>
              {user ? t.final.ctaLoggedIn : t.final.cta}
              <Icon d={ICONS.arrow} className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
        </Reveal>
      </section>
    </div>
  )
}
