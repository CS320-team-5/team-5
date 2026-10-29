import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'
import { MapPin, Send, ShieldCheck, ShoppingBasket } from 'lucide-react'
import '../styles/dashboard.css'
import '../styles/messaging.css'

const initialMessages = [
  { id: 1, sender: 'Alex', initials: 'AM', time: '1:12 PM', text: "Order placed on DoorDash! Will drop by the lobby when it's here." },
  { id: 2, sender: 'Maya', initials: 'ML', time: '1:15 PM', text: 'Awesome, just sent you $14.50 on Venmo.', own: true },
  { id: 3, sender: 'Carlos', initials: 'CR', time: '1:18 PM', text: 'Heading to the lobby now, will bring cash or Venmo.' },
  { id: 4, sender: 'Alex', initials: 'AM', time: 'Just now', text: '🚗 Driver just pulled up outside!', alert: true },
]

const people = [
  { name: 'Alex', initials: 'AM', amount: '$28.00', status: 'Placed order' },
  { name: 'Maya (You)', initials: 'ML', amount: '$14.50', status: '✓ Paid' },
  { name: 'Carlos', initials: 'CR', amount: '$9.50', status: 'Unpaid' },
]

function MessagingPage() {
  const [messages, setMessages] = useState(initialMessages)
  const [draft, setDraft] = useState('')
  const [copyStatus, setCopyStatus] = useState('')
  const messageList = useRef(null)

  useEffect(() => {
    messageList.current.scrollTop = messageList.current.scrollHeight
  }, [messages])

  function sendMessage(text) {
    if (!text.trim()) return
    setMessages(previous => [...previous, {
      id: previous.length + 1, sender: 'Maya', initials: 'ML',
      time: 'Just now', text: text.trim(), own: true,
    }])
  }

  async function copyVenmo() {
    try {
      await navigator.clipboard.writeText('@alex-m')
      setCopyStatus('Copied!')
    } catch {
      setCopyStatus('Select @alex-m to copy it manually.')
    }
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
          <button className="banner-button" type="button">Start a Cart</button>
          <Link className="banner-button" to="/messages" aria-current="page">Messages</Link>
        </nav>
        <div id="right-banner-part">
          <span className="pill"><span className="initials">ML</span><span className="name">Maya (Building 4)</span></span>
        </div>
      </header>

      <main>
        <section className="cart-cell order-summary">
          <div>
            <span className="badge">✓ Order Placed</span> <span className="badge group-badge">DoorDash Group #4928</span>
            <h1>Trader Joe's Cart · Main Building Lobby</h1>
          </div>
          <div className="delivery-estimate">
            <small>ESTIMATED DELIVERY</small>
            <div><strong>~1:30 PM</strong> <small>(12 mins away)</small></div>
          </div>
        </section>

        <div className="messaging-layout">
          <aside className="cart-cell conversation-list" aria-labelledby="chats-title">
            <div className="details-row"><h2 id="chats-title">Chats &amp; Carts</h2><span className="badge">3 Carts</span></div>
            <ul>
              <li className="selected"><strong>Trader Joe's Cart</strong><p>3 neighbors · Active</p><small>Alex: 🚗 Driver just pulled up…</small></li>
              <li><strong>Sweetgreen Order</strong><p>4 neighbors · Completed</p></li>
              <li><strong>Chipotle Run</strong><p>2 neighbors · Ordering</p></li>
              <li><strong>Carlos M.</strong><p>Direct · Settled up Venmo</p></li>
            </ul>
          </aside>

          <div className="cart-details">
            <section className="cart-cell cart-progress" aria-labelledby="progress-title">
              <div className="details-row"><h2 id="progress-title">Group Cart Progress</h2><strong>104% of goal</strong></div>
              <div className="progress-track" role="progressbar" aria-label="Group cart delivery minimum" aria-valuemin={0} aria-valuemax={100} aria-valuenow={100} aria-valuetext="104% of goal">
                <div className="progress-fill" style={{ width: '100%' }} />
              </div>
              <div className="details-row">
                <div><strong className="cart-total">$52.00</strong><p>Target was $50.00 minimum</p></div>
                <div className="savings"><strong>SAVED $7.99</strong><p>Zero delivery split</p></div>
              </div>
            </section>

            <section className="cart-cell" aria-labelledby="split-title">
              <div className="details-row"><h2 id="split-title">Cart Split (3 people)</h2><small>Host: Alex M.</small></div>
              <ul className="split-list">
                {people.map(person => (
                  <li className="status-cell" key={person.initials}>
                    <span className={`other-account-initials avatar avatar-${person.initials}`} aria-hidden="true">{person.initials}</span>
                    <strong>{person.name}</strong>
                    <div className={`person-amount${person.status === 'Unpaid' ? ' unpaid' : ''}`}><strong>{person.amount}</strong><small>{person.status}</small></div>
                  </li>
                ))}
              </ul>
              <div className="status-cell venmo-details">
                <small>Alex's Venmo: <strong>@alex-m</strong></small>
                <button type="button" onClick={copyVenmo}>Copy</button>
              </div>
              {copyStatus && <small role="status">{copyStatus}</small>}
            </section>

            <section className="cart-cell pickup-details" aria-labelledby="pickup-title">
              <div className="details-row"><h2 id="pickup-title"><MapPin size={16} aria-hidden="true" />Meetup Hand-off Location</h2><span className="badge">Privacy Protected</span></div>
              <strong>Common Pickup Spot: Main Building Lobby (Package Area Shelves)</strong>
              <div className="status-cell"><small><ShieldCheck size={13} aria-hidden="true" /> Common area pickup — private apartment numbers are never shared.</small></div>
              <p>Host will drop items here and ping the cart chat once delivered.</p>
            </section>
          </div>

          <section className="cart-cell group-chat" aria-labelledby="chat-title">
            <div className="details-row chat-heading">
              <div><h2 id="chat-title">Group Chat</h2><p>3 neighbors · Active</p></div>
              <span className="badge">● Lobby pickup</span>
            </div>
            <div className="message-list" role="log" aria-labelledby="chat-title" tabIndex={0} ref={messageList}>
              {messages.map(message => (
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
              <input aria-label="Message" placeholder="Type a message to the cart…" value={draft} onChange={event => setDraft(event.target.value)} />
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
