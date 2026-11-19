#!/usr/bin/env python3
"""Apply focused messaging race-condition fixes to current CoCart main.

Run from repo root: python3 fix_cocart_messaging.py
Fails without modifying anything when expected source snippets are missing.
"""
from pathlib import Path

path = Path('frontend/src/pages/MessagingPage.jsx')
source = path.read_text()
changes = []

def replace(old, new):
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f'Expected exactly one match, found {count}: {old[:100]!r}. No files changed.')
    source = source.replace(old, new)
    changes.append(old[:60])

replace("  const [messages, setMessages] = useState([])", """  // Chat data is keyed by cart so responses for cart A cannot appear in cart B.
  const [messagesByCart, setMessagesByCart] = useState({})""")
replace("  const [sending, setSending] = useState(false)\n", "")
replace("  const draft = drafts[selectedId] ?? ''\n", """  const draft = drafts[selectedId] ?? ''
  const messages = messagesByCart[selectedId] ?? []
  const hasPendingMessages = messages.some(message => message.localStatus === 'pending')
""")
replace("""    setMessages([])
    setMembers([])
    setChatError('')""", """    setMembers([])
    setChatError('')""")
replace("""        if (active) { setMessages(received); setChatError('') }""", """        if (active) {
          // Retain pending/failed local messages, and confirmed sends that a
          // concurrent/older poll hasn't returned yet.
          setMessagesByCart(previous => {
            const existing = previous[selectedId] ?? []
            const receivedIds = new Set(received.map(message => message.messageid))
            const local = existing.filter(message =>
              message.localStatus || !receivedIds.has(message.messageid)
            )
            return { ...previous, [selectedId]: [...received, ...local] }
          })
          setChatError('')
        }""")
replace("""  async function sendMessage(text) {
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
  }""", """  async function sendMessage(text, clearDraft = false) {
    const trimmed = text.trim()
    if (!trimmed || !canSend || loadingChat || !validId) return

    // Capture the cart at submission time: navigation must not redirect this POST.
    const targetCartId = selectedId
    const temporaryId = `pending-${crypto.randomUUID()}`
    const optimistic = {
      messageid: temporaryId,
      cartid: targetCartId,
      userid: profile?.userid,
      messagetext: trimmed,
      timestamp: new Date().toISOString(),
      localStatus: 'pending',
    }

    // Clear only what was submitted, immediately, not when the request completes.
    // Quick replies do not disturb a draft the user is typing.
    if (clearDraft) {
      setDrafts(previous => ({ ...previous, [targetCartId]: '' }))
    }
    setChatError('')
    setMessagesByCart(previous => ({
      ...previous,
      [targetCartId]: [...(previous[targetCartId] ?? []), optimistic],
    }))

    try {
      const saved = await sendCartMessage(targetCartId, trimmed)
      setMessagesByCart(previous => {
        const withoutTemporary = (previous[targetCartId] ?? [])
          .filter(message => message.messageid !== temporaryId)
        const alreadyPresent = withoutTemporary.some(message => message.messageid === saved.messageid)
        return {
          ...previous,
          [targetCartId]: alreadyPresent ? withoutTemporary : [...withoutTemporary, saved],
        }
      })
    } catch (reason) {
      setMessagesByCart(previous => ({
        ...previous,
        [targetCartId]: (previous[targetCartId] ?? []).map(message =>
          message.messageid === temporaryId
            ? { ...message, localStatus: 'failed', failureReason: reason.message }
            : message
        ),
      }))
    }
  }

  function retryMessage(message) {
    const targetCartId = message.cartid
    if (targetCartId !== selectedId || !canSend) return
    setMessagesByCart(previous => ({
      ...previous,
      [targetCartId]: (previous[targetCartId] ?? []).filter(
        item => item.messageid !== message.messageid
      ),
    }))
    sendMessage(message.messagetext)
  }""")
replace("""                    <p className="message-bubble">{message.messagetext}</p>""", """                    <p className="message-bubble">{message.messagetext}</p>
                    {message.localStatus === 'pending' && <small>Sending…</small>}
                    {message.localStatus === 'failed' && <small role="alert">
                      Not sent: {message.failureReason || 'Request failed.'}{' '}
                      <button type="button" onClick={() => retryMessage(message)}>Retry</button>
                    </small>}""")
replace("""disabled={sending || loadingChat} onClick={() => sendMessage(reply)}""", """disabled={loadingChat} onClick={() => sendMessage(reply)}""")
replace("""onSubmit={event => { event.preventDefault(); sendMessage(draft) }}""", """onSubmit={event => { event.preventDefault(); sendMessage(draft, true) }}""")
replace("""disabled={!draft.trim() || sending || loadingChat}""", """disabled={!draft.trim() || loadingChat}""")
replace("""  const hasPendingMessages = messages.some(message => message.localStatus === 'pending')
""", "")
path.write_text(source)
print(f'Updated {path} ({len(changes)} focused replacements).')
