import { Route, Routes } from 'react-router'
import DashboardPage from './pages/DashboardPage.tsx'
import LandingPage from './pages/LandingPage.jsx'
import SignUpPage from './pages/SignUpPage.jsx'
import { CreateCartPage } from './pages/CreateCartPage.tsx'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/create" element={<CreateCartPage />}/>
      <Route path="*" element={<LandingPage />} />
    </Routes>
  )
}

export default App
