// @vitest-environment jsdom
import { render, screen, cleanup, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router'
import { afterEach, beforeEach, expect, test, vi } from 'vitest'
import App from './App.jsx'
import { supabase } from './lib/supabase'

vi.mock('./lib/supabase', () => ({
  supabase: { auth: { getSession: vi.fn(), onAuthStateChange: vi.fn(), signOut: vi.fn() } },
}))

const session = { access_token: 'test-access-token' }

function setSession(currentSession) {
  supabase.auth.getSession.mockResolvedValue({ data: { session: currentSession }, error: null })
  supabase.auth.onAuthStateChange.mockImplementation(callback => {
    callback('INITIAL_SESSION', currentSession)
    return { data: { subscription: { unsubscribe: vi.fn() } } }
  })
}

beforeEach(() => {
  window.history.replaceState(null, '', '/')
  setSession(null)
})

afterEach(() => {
  cleanup()
  vi.resetAllMocks()
  vi.unstubAllGlobals()
})

function renderApp() {
  return render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  )
}

test('clicking nav links changes the page', async () => {
  const user = userEvent.setup()
  renderApp()

  await user.click(screen.getByRole('link', { name: /browse carts/i }))
  expect(window.location.pathname).toBe('/dashboard')
  expect(screen.getByText('Active Community Carts')).toBeTruthy()

  await user.click(screen.getByLabelText('Co-Cart home'))
  expect(window.location.pathname).toBe('/')
  expect(screen.getByText('Meet the delivery minimum, together.')).toBeTruthy()
})

test.each([
  ['/create', 'Co-Cart home'],
  ['/settings', 'Co-Cart home'],
  ['/messages', 'CoCart home'],
])('clicking the logo on %s while signed in opens the dashboard', async (url, label) => {
  const user = userEvent.setup()
  setSession(session)
  vi.stubGlobal('fetch', vi.fn(async path => ({
    ok: true,
    json: async () => path === '/api/user/me' ? { userid: 1, name: 'Test User' } : [],
  })))
  window.history.replaceState(null, '', url)
  renderApp()

  const logo = screen.getByRole('link', { name: label })
  expect(logo.getAttribute('href')).toBe('/dashboard')
  await user.click(logo)

  expect(window.location.pathname).toBe('/dashboard')
  expect(screen.getByRole('heading', { name: 'Active Community Carts' })).toBeTruthy()
  expect(supabase.auth.signOut).not.toHaveBeenCalled()
})

test('clicking the logo before the initial auth event uses the restored session', async () => {
  const user = userEvent.setup()
  setSession(session)
  supabase.auth.onAuthStateChange.mockReturnValueOnce({
    data: { subscription: { unsubscribe: vi.fn() } },
  })
  window.history.replaceState(null, '', '/settings')
  renderApp()

  await user.click(screen.getByRole('link', { name: 'Co-Cart home' }))

  expect(window.location.pathname).toBe('/dashboard')
})

test('back button goes to the previous page', async () => {
  const user = userEvent.setup()
  renderApp()

  await user.click(screen.getByRole('link', { name: /browse carts/i }))
  expect(window.location.pathname).toBe('/dashboard')

  act(() => window.history.back())
  await waitFor(() => expect(window.location.pathname).toBe('/'))
  expect(screen.getByText('Meet the delivery minimum, together.')).toBeTruthy()
})

test.each([
  ['/dashboard', 'Active Community Carts'],
  ['/messages', 'Select a cart conversation'],
  ['/signup', 'Create Account'],
])('loading %s directly shows the right page', (url, expected) => {
  window.history.replaceState(null, '', url)
  renderApp()
  expect(screen.getByRole('heading', { name: expected })).toBeTruthy()
})

test('dashboard messages link opens cart conversation selection', async () => {
  const user = userEvent.setup()
  window.history.replaceState(null, '', '/dashboard')
  renderApp()
  await user.click(screen.getByRole('link', { name: 'Messages' }))
  expect(window.location.pathname).toBe('/messages')
  expect(screen.getByRole('heading', { name: 'Select a cart conversation' })).toBeTruthy()
})
