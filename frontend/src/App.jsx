import { Route, Routes } from 'react-router'
import DashboardPage from './pages/DashboardPage.tsx'
import LandingPage from './pages/LandingPage.jsx'
import MessagingPage from './pages/MessagingPage.jsx'
import SignUpPage from './pages/SignUpPage.jsx'
import LoginPage from './pages/LoginPage.jsx'
import SettingsPage from './pages/SettingsPage.tsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/messages" element={<MessagingPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route path="*" element={<LandingPage />} />
    </Routes>
  )
}

export default App
