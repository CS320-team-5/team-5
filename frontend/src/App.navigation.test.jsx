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
const subscription = { data: { subscription: { unsubscribe() {} } } }

function setSession(currentSession) {
  supabase.auth.getSession.mockResolvedValue({ data: { session: currentSession }, error: null })
  supabase.auth.onAuthStateChange.mockImplementation(callback => {
    callback('INITIAL_SESSION', currentSession)
    return subscription
  })
}

beforeEach(() => setSession(null))

afterEach(() => {
  cleanup()
  vi.resetAllMocks()
  vi.unstubAllGlobals()
})

function renderApp(path = '/') {
  window.history.replaceState(null, '', path)
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

test.each(['/settings', '/messages'])('signed-in logo on %s opens the dashboard', async path => {
  setSession(session)
  vi.stubGlobal('fetch', async url => Response.json(
    url === '/api/user/me' ? { userid: 1, name: 'Test User' } : [],
  ))
  renderApp(path)

  await userEvent.click(screen.getByRole('link', { name: /co-?cart home/i }))
  expect(window.location.pathname).toBe('/dashboard')
  expect(supabase.auth.signOut).not.toHaveBeenCalled()
})

test('logo waits for the session on first click', async () => {
  setSession(session)
  supabase.auth.onAuthStateChange.mockReturnValueOnce(subscription)
  renderApp('/settings')

  await userEvent.click(screen.getByLabelText('Co-Cart home'))
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
  renderApp(url)
  expect(screen.getByRole('heading', { name: expected })).toBeTruthy()
})

test('dashboard messages link opens cart conversation selection', async () => {
  const user = userEvent.setup()
  renderApp('/dashboard')
  await user.click(screen.getByRole('link', { name: 'Messages' }))
  expect(window.location.pathname).toBe('/messages')
  expect(screen.getByRole('heading', { name: 'Select a cart conversation' })).toBeTruthy()
})
