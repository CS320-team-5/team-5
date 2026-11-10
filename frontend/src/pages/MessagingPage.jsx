import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import { MapPin, Send, ShoppingBasket } from 'lucide-react'
import { cartConversations, initialMessages } from '../data/messaging'
import '../styles/dashboard.css'
import '../styles/messaging.css'

function MessagingPage() {
  const [messages, setMessages] = useState(initialMessages)
  const [cartId, setCartId] = useState(cartConversations[0].cartId)
  const [drafts, setDrafts] = useState({})
  const cart = cartConversations.find(conversation => conversation.cartId === cartId)
  const cartMessages = messages.filter(message => message.cartId === cartId)
  const draft = drafts[cartId] ?? ''
  const percentage = Math.round(cart.total / cart.target * 100)
  function setDraft(text) {
    setDrafts(previous => ({ ...previous, [cartId]: text }))
  }
  const messageList = useRef(null)

  useEffect(() => {
    messageList.current.scrollTop = messageList.current.scrollHeight
  }, [messages, cartId])

  function sendMessage(text) {
    if (!text.trim()) return
    // Backend integration: POST { messagetext: text.trim() } to /api/message/cart/{cartId}.
    setMessages(previous => [...previous, {
      id: crypto.randomUUID(), cartId, sender: 'Maya', initials: 'ML',
      time: 'Just now', text: text.trim(), own: true,
    }])
  }

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
        <div id="right-banner-part">
          <span className="pill"><span className="initials">ML</span><span className="name">Maya (Building 4)</span></span>
        </div>
      </header>

      <main>
        <section className="cart-cell order-summary">
          <div>
            <span className="badge">{cart.status}</span> <span className="badge group-badge">Cart #{cart.cartId}</span>
            <h1>{cart.title} · {cart.pickupLocation}</h1>
          </div>
          {cart.estimatedDelivery && <div className="delivery-estimate">
            <small>ESTIMATED DELIVERY</small>
            <strong>{cart.estimatedDelivery}</strong>
          </div>}
        </section>

        <div className="messaging-layout">
          <aside className="cart-cell conversation-list" aria-labelledby="chats-title">
            <div className="details-row"><h2 id="chats-title">Cart Conversations</h2><span className="badge">{cartConversations.length} Carts</span></div>
            <ul>
              {cartConversations.map(conversation => (
                <li key={conversation.cartId}>
                  <button type="button" className="conversation-button" aria-current={conversation.cartId === cartId ? 'true' : undefined} onClick={() => setCartId(conversation.cartId)}>
                    <strong>{conversation.title}</strong>
                    <span>{conversation.members.length} neighbors · {conversation.status}</span>
                  </button>
                </li>
              ))}
            </ul>
          </aside>

          <div className="cart-details">
            <section className="cart-cell cart-progress" aria-labelledby="progress-title">
              <div className="details-row"><h2 id="progress-title">Group Cart Progress</h2><strong>{percentage}% of goal</strong></div>
              <div className="progress-track" role="progressbar" aria-label="Group cart delivery minimum" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.min(percentage, 100)} aria-valuetext={`${percentage}% of goal`}>
                <div className="progress-fill" style={{ width: `${Math.min(percentage, 100)}%` }} />
              </div>
              <div className="details-row">
                <div><strong className="cart-total">${cart.total.toFixed(2)}</strong><p>Target: ${cart.target.toFixed(2)} minimum</p></div>
                {cart.deliverySavings && <div className="savings"><strong>SAVED ${cart.deliverySavings.toFixed(2)}</strong></div>}
              </div>
            </section>

            <section className="cart-cell" aria-labelledby="members-title">
              <div className="details-row"><h2 id="members-title">Who's in this cart</h2><span className="badge">{cart.members.length} neighbors</span></div>
              <ul className="cart-members">
                {cart.members.map(member => (
                  <li className="status-cell" key={member.id}>
                    <span className={`other-account-initials avatar avatar-${member.initials}`} aria-hidden="true">{member.initials}</span>
                    <strong>{member.name}{member.own ? ' (You)' : ''}</strong>
                    {member.host && <span className="badge">Host</span>}
                  </li>
                ))}
              </ul>
            </section>

            <section className="cart-cell pickup-details" aria-labelledby="pickup-title">
              <div className="details-row"><h2 id="pickup-title"><MapPin size={16} aria-hidden="true" />Meetup Hand-off Location</h2></div>
              <strong>Common Pickup Spot: {cart.pickupLocation}</strong>
              <p>Host will drop items here and ping the cart chat once delivered.</p>
            </section>
          </div>

          <section className="cart-cell group-chat" aria-labelledby="chat-title">
            <div className="details-row chat-heading">
              <div><h2 id="chat-title">{cart.title} Group Chat</h2><p>{cart.members.length} neighbors · {cart.status}</p></div>
            </div>
            <div className="message-list" role="log" aria-labelledby="chat-title" tabIndex={0} ref={messageList}>
              {cartMessages.length === 0 && <p>No messages yet. Say hello to your cart!</p>}
              {cartMessages.map(message => (
                <div className={`chat-message${message.own ? ' own-message' : ''}`} key={message.id}>
                  <span className={`other-account-initials avatar avatar-${message.initials}`} aria-hidden="true">{message.initials}</span>
                  <div className="message-content">
                    <small className="message-meta"><strong>{message.sender}</strong> {message.time}</small>
                    <p className={`message-bubble${message.alert ? ' message-alert' : ''}`}>{message.text}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="quick-replies">
              <small>Quick:</small>
              {['Heading down now 🏃', "I'm in the lobby 📍", 'Sent Venmo ✓'].map(reply => (
                <button className="filter-button" key={reply} type="button" onClick={() => sendMessage(reply)}>{reply}</button>
              ))}
            </div>
            <form className="composer" onSubmit={event => {
              event.preventDefault()
              sendMessage(draft)
              setDraft('')
            }}>
              <input aria-label="Message" placeholder={`Message ${cart.title}…`} maxLength={2000} value={draft} onChange={event => setDraft(event.target.value)} />
              <button className="join-button" type="submit" disabled={!draft.trim()}>Send <Send size={16} aria-hidden="true" /></button>
            </form>
          </section>
        </div>
      </main>
      <footer>Co-Cart · Neighborhood group order cart</footer>
    </div>
  )
}

export default MessagingPage
