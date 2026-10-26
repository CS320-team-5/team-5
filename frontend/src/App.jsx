import DashboardPage from './pages/DashboardPage.tsx'
import LandingPage from './pages/LandingPage.jsx'
import SignUpPage from './pages/SignUpPage.jsx'

function App() {
  const pathname = window.location.pathname.replace(/\/+$/, '') || '/'

  if (pathname === '/dashboard') return <DashboardPage />
  if (pathname === '/signup') return <SignUpPage />

  return <LandingPage />
}

export default App
