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
  ['/signup', 'Create Account'],
])('loading %s directly shows the right page', (url, expected) => {
  window.history.replaceState(null, '', url)
  renderApp()
  expect(screen.getByRole('heading', { name: expected })).toBeTruthy()
})