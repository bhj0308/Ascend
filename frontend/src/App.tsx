import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { Home } from '@/pages/Home'
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

export function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/new" element={<JobNew />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/jobs/:id/applicants" element={<JobApplicants />} />
        <Route path="/guides" element={<Guides />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/contracts" element={<Contracts />} />
        <Route path="/contracts/new" element={<ContractNew />} />
        <Route path="/contracts/:id" element={<ContractDetail />} />
        <Route path="/mentorships" element={<Mentorships />} />
        <Route path="/users/:id" element={<PublicProfile />} />
        <Route path="/payments" element={<Payments />} />
        <Route path="/payments/new" element={<PaymentNew />} />
        <Route path="/payments/:id" element={<PaymentDetail />} />
        <Route path="/messages" element={<Messages />} />
        <Route path="/messages/:userId" element={<MessageThread />} />
      </Routes>
    </BrowserRouter>
  )
}
