import Dashboard from './faaiz-home-page/Dashboard.tsx'
import LandingPage from './pages/LandingPage.jsx'

function App() {
  const pathname = window.location.pathname.replace(/\/+$/, '') || '/'

  return pathname === '/dashboard' ? <Dashboard /> : <LandingPage />
}

export default App
