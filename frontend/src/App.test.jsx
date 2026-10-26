import { renderToStaticMarkup } from 'react-dom/server'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App.jsx'

afterEach(() => vi.unstubAllGlobals())

test('keeps the landing page at the home URL and links to the dashboard', () => {
  vi.stubGlobal('window', { location: { pathname: '/' } })

  const html = renderToStaticMarkup(<App />)

  expect(html).toContain('Meet the delivery minimum, together.')
  expect(html).toContain('href="/dashboard"')
  expect(html).toContain('href="/signup"')
  expect(html).not.toContain('Active Community Carts')
})

test.each(['/dashboard', '/dashboard/'])('renders the dashboard at %s with a link home', pathname => {
  vi.stubGlobal('window', { location: { pathname } })

  const html = renderToStaticMarkup(<App />)

  expect(html).toContain('Active Community Carts')
  expect(html).toContain('aria-label="CoCart home"')
  expect(html).toContain('href="/"')
  expect(html).not.toContain('Meet the delivery minimum, together.')
})

test.each(['/signup', '/signup/'])('renders the signup page at %s through the shared app', pathname => {
  vi.stubGlobal('window', { location: { pathname } })

  const html = renderToStaticMarkup(<App />)

  expect(html).toContain('Create Account')
  expect(html).toContain('type="email"')
  expect(html).toContain('type="password"')
  expect(html).not.toContain('Active Community Carts')
  expect(html).not.toContain('Meet the delivery minimum, together.')
})
