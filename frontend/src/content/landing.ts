// Landing page copy in both languages. Keep every claim true to what the app
// actually does today (see the "straight" section) — the Terms and Privacy
// pages make the same statements, and a reviewer checks them against the code.

export type Lang = 'en' | 'ko'

export interface LandingCopy {
  toggle: string
  eyebrow: string
  headline: string
  sub: string
  ctaPost: string
  ctaBrowse: string
  heroNotes: string[]
  preview: {
    route: { from: string; to: string; caption: string }
    job: { title: string; meta: string; badge: string }
    contract: { label: string; status: string }
    message: { from: string; body: string }
  }
  live: { title: string; count: (n: number) => string; viewAll: string }
  flags: { remote: string; visa: string; iec: string }
  founders: { title: string; bullets: string[]; cta: string }
  talent: { title: string; bullets: string[]; cta: string }
  how: { title: string; steps: { title: string; body: string }[] }
  features: { title: string; items: { title: string; body: string }[] }
  straight: { title: string; items: string[] }
  final: { line: string; cta: string; ctaLoggedIn: string }
}

export const LANDING: Record<Lang, LandingCopy> = {
  en: {
    toggle: '한국어',
    eyebrow: 'For Korean-Canadian founders and global tech talent',
    headline: 'Build your team across Korea and Canada.',
    sub: 'Ascend connects founders with engineers on both sides of the Pacific, and gives IEC working-holiday talent and newcomers a real way into Canadian tech. Jobs, contracts, mentorship, messaging, and payment records — in one place.',
    ctaPost: 'Post a job — free',
    ctaBrowse: 'Browse jobs',
    heroNotes: ['Free during early access', 'English & 한국어', 'Your email stays private'],
    // Illustrations of real features in the hero; not live data.
    preview: {
      route: { from: 'Seoul', to: 'Toronto', caption: 'Hire across the Pacific' },
      job: { title: 'Backend Engineer', meta: 'Toronto · Full-time', badge: 'IEC-friendly' },
      contract: { label: 'Contract', status: 'Signed' },
      message: { from: 'New message', body: 'Are you free for a call Thursday?' },
    },
    live: {
      title: 'Open right now',
      count: (n) => `${n} open ${n === 1 ? 'role' : 'roles'}`,
      viewAll: 'View all jobs',
    },
    flags: { remote: 'Remote OK', visa: 'Visa sponsorship', iec: 'IEC-friendly' },
    founders: {
      title: "I'm hiring",
      bullets: [
        'Reach engineers in Korea and Canada without an agency in between.',
        'Draft a contract from a cross-border template in minutes.',
        'Keep a payment record for every contract, so the documentation is there when you need it.',
      ],
      cta: 'Post a job',
    },
    talent: {
      title: "I'm looking for work",
      bullets: [
        'Filter listings by IEC-friendly and visa sponsorship — matching jobs are flagged for you.',
        'Ask someone who has already made the move to be your mentor.',
        'Message founders directly — no recruiter in the middle.',
      ],
      cta: 'Find jobs',
    },
    how: {
      title: 'How it works',
      steps: [
        {
          title: 'Create a profile',
          body: 'Founders add their company; talent adds skills, languages, and visa status.',
        },
        {
          title: 'Connect',
          body: 'Post or apply, message each other, and request mentorship from people who have done it.',
        },
        {
          title: 'Make it official',
          body: 'Generate a contract draft, send it, record the acknowledgment, and log payments against it.',
        },
      ],
    },
    features: {
      title: 'What you get',
      items: [
        { title: 'Job board with visa filters', body: 'Filter by Remote-OK, visa sponsorship, and IEC-friendly — matching listings are flagged.' },
        { title: 'Contract templates', body: 'Korea ↔ Canada, remote contractor, full-time, and part-time — with typed, validated terms.' },
        { title: 'Mentorship', body: 'Request a mentor from any profile; they accept, and you both track it.' },
        { title: 'Messaging', body: 'Direct threads between founders and talent, with unread counts.' },
        { title: 'Payment records', body: 'Log salaries, contract payments, and remittances per counterparty.' },
        { title: 'Private by default', body: 'Your email is never shown to other users — not on your profile, not anywhere.' },
      ],
    },
    straight: {
      title: 'Straight talk',
      items: [
        'Contract templates are scaffolding, not legal advice. Have a professional review anything you sign.',
        'Payments are recorded, not transferred. No money moves through Ascend yet (Wise integration is planned).',
        'In-app signing records an acknowledgment. It is not a legal electronic signature.',
      ],
    },
    final: {
      line: 'Free while we are in early access.',
      cta: 'Create your account',
      ctaLoggedIn: 'Go to jobs',
    },
  },
  ko: {
    toggle: 'English',
    eyebrow: '한인 창업자와 글로벌 테크 인재를 위한 플랫폼',
    headline: '한국과 캐나다를 잇는 팀을 만드세요.',
    sub: 'Ascend는 태평양 양쪽의 창업자와 엔지니어를 연결하고, 워킹홀리데이(IEC)와 이민자 인재에게 캐나다 테크 업계로 가는 실질적인 길을 열어줍니다. 채용 공고, 계약서, 멘토링, 메시지, 결제 기록까지 한곳에서.',
    ctaPost: '무료로 채용 공고 올리기',
    ctaBrowse: '채용 공고 보기',
    heroNotes: ['얼리 액세스 기간 무료', '한국어 & English', '이메일은 비공개'],
    // 히어로 영역의 기능 예시 이미지이며 실제 데이터가 아닙니다.
    preview: {
      route: { from: '서울', to: '토론토', caption: '태평양을 넘는 채용' },
      job: { title: '백엔드 엔지니어', meta: '토론토 · 정규직', badge: 'IEC 가능' },
      contract: { label: '계약서', status: '서명 완료' },
      message: { from: '새 메시지', body: '목요일에 통화 가능하실까요?' },
    },
    live: {
      title: '지금 모집 중',
      count: (n) => `${n}개 포지션 모집 중`,
      viewAll: '전체 공고 보기',
    },
    flags: { remote: '원격 가능', visa: '비자 지원', iec: 'IEC 가능' },
    founders: {
      title: '채용 중이에요',
      bullets: [
        '에이전시 없이 한국과 캐나다의 엔지니어에게 직접 닿을 수 있습니다.',
        '국가 간 계약서 템플릿으로 몇 분 만에 초안을 만듭니다.',
        '계약별 결제 내역을 남겨 필요할 때 바로 확인할 수 있습니다.',
      ],
      cta: '공고 올리기',
    },
    talent: {
      title: '일자리를 찾고 있어요',
      bullets: [
        'IEC 가능 여부와 비자 지원 여부로 공고를 필터링할 수 있고, 해당 공고에는 배지가 표시됩니다.',
        '먼저 그 길을 걸어본 분에게 멘토링을 요청할 수 있습니다.',
        '리크루터 없이 창업자에게 직접 메시지를 보낼 수 있습니다.',
      ],
      cta: '공고 찾기',
    },
    how: {
      title: '이용 방법',
      steps: [
        { title: '프로필 만들기', body: '창업자는 회사 정보를, 인재는 기술·언어·비자 상태를 등록합니다.' },
        { title: '연결하기', body: '공고를 올리거나 지원하고, 메시지를 주고받고, 경험자에게 멘토링을 요청합니다.' },
        { title: '정식으로 진행하기', body: '계약서 초안을 만들어 보내고, 수락을 기록하고, 결제 내역을 남깁니다.' },
      ],
    },
    features: {
      title: '제공 기능',
      items: [
        { title: '비자 필터가 있는 채용 게시판', body: '원격 가능, 비자 지원, IEC 가능 여부로 필터링할 수 있으며, 해당 공고에는 배지가 표시됩니다.' },
        { title: '계약서 템플릿', body: '한국↔캐나다, 원격 프리랜서, 정규직, 파트타임 — 항목별 검증이 포함된 템플릿.' },
        { title: '멘토링', body: '프로필에서 바로 멘토링을 요청하고, 수락 후 함께 진행 상황을 관리합니다.' },
        { title: '메시지', body: '창업자와 인재가 직접 대화하고, 읽지 않은 메시지 수를 확인합니다.' },
        { title: '결제 기록', body: '급여, 계약 대금, 송금을 상대방별로 기록합니다.' },
        { title: '기본이 프라이버시', body: '이메일은 프로필을 포함해 어디에서도 다른 사용자에게 보이지 않습니다.' },
      ],
    },
    straight: {
      title: '솔직하게 말씀드리면',
      items: [
        '계약서 템플릿은 참고용 초안이며 법률 자문이 아닙니다. 서명 전에 전문가 검토를 받으세요.',
        '결제는 기록만 되며 실제 송금은 이루어지지 않습니다. (Wise 연동 예정)',
        '앱 내 서명은 수락 확인 기록이며 법적 효력이 있는 전자서명이 아닙니다.',
      ],
    },
    final: { line: '얼리 액세스 기간 동안 무료입니다.', cta: '계정 만들기', ctaLoggedIn: '채용 공고로 이동' },
  },
}
