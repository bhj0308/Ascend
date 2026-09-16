import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { Home } from '@/pages/Home'
import { Jobs } from '@/pages/Jobs'
import { JobDetail } from '@/pages/JobDetail'
import { JobNew } from '@/pages/JobNew'
import { Login } from '@/pages/Login'
import { Signup } from '@/pages/Signup'
import { Profile } from '@/pages/Profile'
import { Guides } from '@/pages/Guides'

export function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/jobs/new" element={<JobNew />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/guides" element={<Guides />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </BrowserRouter>
  )
}
