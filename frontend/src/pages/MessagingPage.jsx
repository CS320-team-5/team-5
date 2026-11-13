import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router'
import { MapPin, Send, ShoppingBasket } from 'lucide-react'
import { getMyProfile, getMyMessageCarts, getCartMessages, getCartMembers, getPublicUser, sendCartMessage } from '../services/message'
import '../styles/dashboard.css'
import '../styles/messaging.css'
import Banner from "../components/Banner";

const initialsFor = (name) => (name || '?').split(/\s+/).slice(0, 2).map(part => part[0] || '').join('').toUpperCase()
const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
const isOpen = (cart) => cart?.status === 'Active' && Date.parse(cart.deadline) > Date.now()

function MessagingPage() {
  const { cartId: routeId } = useParams()
  const navigate = useNavigate()
  const selectedId = routeId ? Number(routeId) : null
  const validId = selectedId != null && Number.isSafeInteger(selectedId) && selectedId > 0
  const [carts, setCarts] = useState([])
  const [profile, setProfile] = useState(null)
  const [members, setMembers] = useState([])
  const [messages, setMessages] = useState([])
  const [names, setNames] = useState({})
  const [drafts, setDrafts] = useState({})
  const [loadingCarts, setLoadingCarts] = useState(true)
  const [loadingChat, setLoadingChat] = useState(false)
  const [error, setError] = useState('')
  const [chatError, setChatError] = useState('')
  const [sending, setSending] = useState(false)
  const messageList = useRef(null)
  const cart = carts.find(item => item.cartid === selectedId)
  const draft = drafts[selectedId] ?? ''
  const canSend = isOpen(cart)
  const percentage = cart?.minimumamount ? Math.round(Number(cart.currentamount) / Number(cart.minimumamount) * 100) : 0

  useEffect(() => {
    let active = true
    Promise.all([getMyProfile(), getMyMessageCarts()]).then(([user, result]) => {
      if (!active) return
      setProfile(user)
      setNames({ [user.userid]: user.name || 'You' })
      setCarts(result)
    }).catch(reason => { if (active) setError(reason.message) })
      .finally(() => { if (active) setLoadingCarts(false) })
    return () => { active = false }
  }, [])

  useEffect(() => {
    setMessages([])
    setMembers([])
    setChatError('')
    if (!validId || loadingCarts || !cart) return
    let active = true
    setLoadingChat(true)
    const refresh = async () => {
      try {
        const received = await getCartMessages(selectedId)
        if (active) { setMessages(received); setChatError('') }
      } catch (reason) { if (active) setChatError(reason.message) }
      finally { if (active) setLoadingChat(false) }
    }
    refresh()
    getCartMembers(selectedId).then(result => { if (active) setMembers(result) })
      .catch(reason => { if (active) setChatError(reason.message) })
    const interval = window.setInterval(refresh, 5000)
    return () => { active = false; window.clearInterval(interval) }
  }, [selectedId, validId, loadingCarts, cart?.cartid])

  useEffect(() => {
    if (!profile) return
    let active = true
    const ids = [...new Set([cart?.owneruserid, ...members.map(member => member.userid), ...messages.map(message => message.userid)])]
      .filter(id => id != null && id !== profile.userid && !(id in names))
    if (ids.length) Promise.all(ids.map(async id => {
      try { const person = await getPublicUser(id); return [id, person.name || `User ${id}`] }
      catch { return [id, `User ${id}`] }
    })).then(entries => { if (active) setNames(previous => ({ ...previous, ...Object.fromEntries(entries) })) })
    return () => { active = false }
  }, [cart?.owneruserid, members, messages, names, profile])

  useEffect(() => {
    if (messageList.current) messageList.current.scrollTop = messageList.current.scrollHeight
  }, [messages, selectedId])

  function setDraft(text) { setDrafts(previous => ({ ...previous, [selectedId]: text })) }

  async function sendMessage(text) {
    const trimmed = text.trim()
    if (!trimmed || !canSend || sending || loadingChat) return
    setSending(true)
    setChatError('')
    try {
      const saved = await sendCartMessage(selectedId, trimmed)
      setMessages(previous => previous.some(message => message.messageid === saved.messageid) ? previous : [...previous, saved])
      setDrafts(previous => ({ ...previous, [selectedId]: '' }))
    } catch (reason) { setChatError(reason.message) }
    finally { setSending(false) }
  }

  const memberIds = new Set([cart?.owneruserid, ...members.map(member => member.userid)].filter(Boolean))
  const listMembers = [...memberIds].map(id => ({ id, name: id === profile?.userid ? (profile.name || 'You') : (names[id] || `User ${id}`), host: id === cart?.owneruserid, own: id === profile?.userid }))

  return (
    <div className="dashboard-page messaging-page">
      <header id="banner">
        <Link id="left-banner-part" to="/" aria-label="CoCart home">
          <ShoppingBasket className="brand-icon" size={32} aria-hidden="true" />
          <span id="logo-title">Co-Cart</span>
        </Link>
        <nav id="center-banner-part" aria-label="Main navigation">
          <Link className="banner-button" to="/dashboard">Browse Carts</Link>
          <Link className="banner-button" to="/create">Start a Cart</Link>
          <Link className="banner-button" to="/messages" aria-current="page">Messages</Link>
        </nav>
        <div id="right-banner-part"><span className="pill">{profile?.name || 'CoCart'}</span></div>
      </header>
      <main>
        {cart && <section className="cart-cell order-summary">
          <div>
            <span className="badge">{isOpen(cart) ? 'Active' : 'Closed'}</span> <span className="badge group-badge">Cart #{cart.cartid}</span>
            <h1>Cart #{cart.cartid} · {cart.location || 'Pickup location not specified'}</h1>
          </div>
        </section>}
        <div className="messaging-layout">
          <aside className="cart-cell conversation-list" aria-labelledby="chats-title">
            <div className="details-row"><h2 id="chats-title">Cart Conversations</h2><span className="badge">{carts.length} Carts</span></div>
            {loadingCarts && <p role="status">Loading carts…</p>}
            {error && <p role="alert">{error}</p>}
            {!loadingCarts && !error && carts.length === 0 && <p>No cart conversations yet.</p>}
            <ul>
              {carts.map(conversation => (
                <li key={conversation.cartid}>
                  <button type="button" className="conversation-button" aria-current={conversation.cartid === selectedId ? 'true' : undefined} onClick={() => navigate(`/messages/${conversation.cartid}`)}>
                    <strong>Cart #{conversation.cartid}</strong>
                    <span>{conversation.location || 'Pickup location not specified'} · {isOpen(conversation) ? 'Active' : 'Closed'}</span>
                  </button>
                </li>
              ))}
            </ul>
          </aside>
          {cart && <div className="cart-details">
            <section className="cart-cell cart-progress" aria-labelledby="progress-title">
              <div className="details-row"><h2 id="progress-title">Group Cart Progress</h2><strong>{percentage}% of goal</strong></div>
              <div className="progress-track" role="progressbar" aria-label="Group cart delivery minimum" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.max(0, Math.min(percentage, 100))} aria-valuetext={`${percentage}% of goal`}>
                <div className="progress-fill" style={{ width: `${Math.max(0, Math.min(percentage, 100))}%` }} />
              </div>
              <div className="details-row"><div><strong className="cart-total">${Number(cart.currentamount).toFixed(2)}</strong><p>Target: ${Number(cart.minimumamount).toFixed(2)} minimum</p></div></div>
            </section>
            <section className="cart-cell" aria-labelledby="members-title">
              <div className="details-row"><h2 id="members-title">Who's in this cart</h2><span className="badge">{listMembers.length} neighbors</span></div>
              <ul className="cart-members">
                {listMembers.map(member => <li className="status-cell" key={member.id}>
                  <span className="other-account-initials avatar" aria-hidden="true">{initialsFor(member.name)}</span>
                  <strong>{member.name}{member.own ? ' (You)' : ''}</strong>
                  {member.host && <span className="badge">Host</span>}
                </li>)}
              </ul>
            </section>
            <section className="cart-cell pickup-details" aria-labelledby="pickup-title">
              <div className="details-row"><h2 id="pickup-title"><MapPin size={16} aria-hidden="true" />Meetup Hand-off Location</h2></div>
              <strong>Common Pickup Spot: {cart.location || 'Not specified'}</strong>
            </section>
          </div>}
          <section className="cart-cell group-chat" aria-labelledby="chat-title">
            <div className="details-row chat-heading"><div>
              <h2 id="chat-title">{cart ? `Cart #${cart.cartid} Group Chat` : 'Select a cart conversation'}</h2>
              {cart && <p>{listMembers.length} neighbors · {isOpen(cart) ? 'Active' : 'Closed'}</p>}
            </div></div>
            {!loadingCarts && routeId && (!validId || !cart) && !error && <p role="alert">This cart conversation is not available to your account.</p>}
            {chatError && <p role="alert">{chatError}</p>}
            {loadingChat && <p role="status">Loading messages…</p>}
            <div className="message-list" role="log" aria-labelledby="chat-title" tabIndex={0} ref={messageList}>
              {cart && !loadingChat && !chatError && messages.length === 0 && <p>No messages yet. Say hello to your cart!</p>}
              {cart && messages.map(message => {
                const own = message.userid === profile?.userid
                const name = own ? 'You' : names[message.userid] || `User ${message.userid}`
                return <div className={`chat-message${own ? ' own-message' : ''}`} key={message.messageid}>
                  <span className="other-account-initials avatar" aria-hidden="true">{initialsFor(name)}</span>
                  <div className="message-content">
                    <small className="message-meta"><strong>{name}</strong> {formatTime(message.timestamp)}</small>
                    <p className="message-bubble">{message.messagetext}</p>
                  </div>
                </div>
              })}
            </div>
            {cart && canSend && <>
              <div className="quick-replies"><small>Quick:</small>
                {['Heading down now', "I'm in the lobby"].map(reply => <button className="filter-button" key={reply} type="button" disabled={sending || loadingChat} onClick={() => sendMessage(reply)}>{reply}</button>)}
              </div>
              <form className="composer" onSubmit={event => { event.preventDefault(); sendMessage(draft) }}>
                <input aria-label="Message" placeholder={`Message Cart #${cart.cartid}…`} maxLength={2000} value={draft} onChange={event => setDraft(event.target.value)} />
                <button className="join-button" type="submit" disabled={!draft.trim() || sending || loadingChat}>Send <Send size={16} aria-hidden="true" /></button>
              </form>
            </>}
            {cart && !canSend && <p>This cart is closed. Previous messages remain available.</p>}
          </section>
        </div>
      </main>
      <footer>Co-Cart · Neighborhood group order cart</footer>
    </div>
  )
}

export default MessagingPage
