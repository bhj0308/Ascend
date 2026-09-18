import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { Landing } from '@/pages/Landing'
import { Jobs } from '@/pages/Jobs'
import { JobDetail } from '@/pages/JobDetail'
import { JobNew } from '@/pages/JobNew'
import { JobApplicants } from '@/pages/JobApplicants'
import { Login } from '@/pages/Login'
import { Signup } from '@/pages/Signup'
import { Profile } from '@/pages/Profile'
import { Guides } from '@/pages/Guides'
import { Contracts } from '@/pages/Contracts'
import { ContractNew } from '@/pages/ContractNew'
import { ContractDetail } from '@/pages/ContractDetail'
import { Mentorships } from '@/pages/Mentorships'
import { PublicProfile } from '@/pages/PublicProfile'
import { Payments } from '@/pages/Payments'
import { PaymentNew } from '@/pages/PaymentNew'
import { PaymentDetail } from '@/pages/PaymentDetail'
import { Messages } from '@/pages/Messages'
import { MessageThread } from '@/pages/MessageThread'
import { Terms } from '@/pages/Terms'
import { Privacy } from '@/pages/Privacy'
import { Footer } from '@/components/Footer'
import { VerifyEmailBanner } from '@/components/VerifyEmailBanner'
import { ForgotPassword } from '@/pages/ForgotPassword'
import { ResetPassword } from '@/pages/ResetPassword'
import { VerifyEmail } from '@/pages/VerifyEmail'
import { Mentors } from '@/pages/Mentors'
import { Admin } from '@/pages/Admin'
import { useEffect } from 'react'
import { getMe } from '@/services/auth'
import { useAuthStore } from '@/store/authStore'

// On a full page load, restore the signed-in user from the stored token so the
// UI doesn't render as logged-out while a valid session exists. A 401 here is
// handled by the api interceptor (refresh, or clear the session).
function AuthBootstrap() {
  const setUser = useAuthStore((s) => s.setUser)
  useEffect(() => {
    if (!localStorage.getItem('access_token')) return
    getMe()
      .then(setUser)
      .catch(() => {
        /* session already cleared by the interceptor */
      })
  }, [setUser])
  return null
}

export function App() {
  return (
    <BrowserRouter>
      <AuthBootstrap />
      <Navbar />
      <VerifyEmailBanner />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/new" element={<JobNew />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/jobs/:id/applicants" element={<JobApplicants />} />
        <Route path="/guides" element={<Guides />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/contracts" element={<Contracts />} />
        <Route path="/contracts/new" element={<ContractNew />} />
        <Route path="/contracts/:id" element={<ContractDetail />} />
        <Route path="/mentorships" element={<Mentorships />} />
        <Route path="/mentors" element={<Mentors />} />
        <Route path="/users/:id" element={<PublicProfile />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/payments/new" element={<PaymentNew />} />
        <Route path="/payments/:id" element={<PaymentDetail />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/messages/:userId" element={<MessageThread />} />
        <Route path="/terms" element={<Terms />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
      <Footer />
    </BrowserRouter>
  )
}
