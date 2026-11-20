import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { supabase } from '../lib/supabase'
import { getSession } from '../services/auth'
import theme from "../styles/theme.module.css"

export default function AppHomeLink({ children, label }) {
  const [signedIn, setSignedIn] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => setSignedIn(Boolean(session)),
    )
    return () => subscription.unsubscribe()
  }, [])

  async function handleClick(event) {
    if (signedIn !== null || event.defaultPrevented || event.button !== 0 ||
      event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return

    // Wait for session restoration if the logo is clicked as the page loads.
    event.preventDefault()
    const link = event.currentTarget
    const session = await getSession().catch(() => null)
    if (link.isConnected) navigate(session ? '/dashboard' : '/')
  }

  return (
    <Link className={theme["left-banner-part"]} to={signedIn ? '/dashboard' : '/'} aria-label={label} onClick={handleClick}>
      {children}
    </Link>
  )
}
