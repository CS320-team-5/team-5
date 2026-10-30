// @vitest-environment jsdom
import { render, screen, cleanup, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router'
import { afterEach, beforeEach, expect, test } from 'vitest'
import App from './App.jsx'

beforeEach(() => window.history.replaceState(null, '', '/'))
afterEach(cleanup)

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

  await user.click(screen.getByLabelText('CoCart home'))
  expect(window.location.pathname).toBe('/')
  expect(screen.getByText('Meet the delivery minimum, together.')).toBeTruthy()
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
  ['/messages', "Trader Joe's Cart · Main Building Lobby"],
  ['/signup', 'Create Account'],
])('loading %s directly shows the right page', (url, expected) => {
  window.history.replaceState(null, '', url)
  renderApp()
  expect(screen.getByRole('heading', { name: expected })).toBeTruthy()
})

test('dashboard messages link opens a chat that can send messages', async () => {
  const user = userEvent.setup()
  window.history.replaceState(null, '', '/dashboard')
  renderApp()

  await user.click(screen.getByRole('link', { name: 'Messages' }))
  expect(window.location.pathname).toBe('/messages')
  expect(screen.getByRole('button', { name: 'Send' }).disabled).toBe(true)

  await user.type(screen.getByRole('textbox', { name: 'Message' }), '  Heading down!  {Enter}')
  expect(screen.getByRole('log').textContent).toContain('Heading down!')
  expect(screen.getByRole('textbox', { name: 'Message' }).value).toBe('')

  await user.click(screen.getByRole('button', { name: 'Sent Venmo ✓' }))
  expect(screen.getByRole('log').textContent).toContain('Sent Venmo ✓')
})
