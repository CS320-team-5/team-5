import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router'
import { expect, test } from 'vitest'
import App from './App.jsx'

const HOME = 'Meet the delivery minimum, together.'
const DASH = 'Active Community Carts'

//no browser here just render the app to an html string at a url
//and check what's in it. fast, but it can't click anything
function page(url) {
  return renderToStaticMarkup(
    <MemoryRouter initialEntries={[url]}>
      <App />
    </MemoryRouter>,
  )
}

test('home page shows the landing page + links to dashboard and signup', () => {
  const html = page('/')

  expect(html).toContain(HOME)
  expect(html).toContain('href="/dashboard"')
  expect(html).toContain('href="/signup"')
  expect(html).not.toContain(DASH)
})

//trailing slash should land on the same page
test.each(['/dashboard', '/dashboard/'])('dashboard at %s, has a way back home', url => {
  const html = page(url)

  expect(html).toContain(DASH)
  expect(html).toContain('aria-label="CoCart home"')
  expect(html).toContain('href="/"')
  expect(html).not.toContain(HOME)
})

test.each(['/signup', '/signup/'])('signup at %s has the form', url => {
  const html = page(url)

  expect(html).toContain('Create Account')
  expect(html).toContain('type="email"')
  expect(html).toContain('type="password"')
  expect(html).not.toContain(DASH)
  expect(html).not.toContain(HOME)
})