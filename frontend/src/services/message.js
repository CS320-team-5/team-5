import { getSession } from './auth'

async function api(path, options = {}) {
  const session = await getSession()
  if (!session?.access_token) throw new Error('Please log in to use cart messages.')
  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = data?.detail
    throw new Error(typeof detail === 'string' ? detail : 'Could not load cart messages.')
  }
  return data
}

export const getMyProfile = () => api('/api/user/me')
export const getMyMessageCarts = () => api('/api/message/carts')
export const getCartMessages = (id) => api(`/api/message/cart/${id}`)
export const getCartMembers = (id) => api(`/api/cart/${id}/participants`)
export const getPublicUser = (id) => api(`/api/user/${id}`)
export const sendCartMessage = (id, text) => api(`/api/message/cart/${id}`, {
  method: 'POST', body: JSON.stringify({ messagetext: text.trim() }),
})
