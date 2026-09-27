'use client'

import { Component, type ErrorInfo, type ReactNode, useState } from 'react'

type ChatMessage = { role: 'assistant' | 'user'; content: string }

async function mockSendMessage(message: string, signal: AbortSignal) {
  const apiUrl = process.env.NEXT_PUBLIC_CHAT_API_URL ?? 'http://localhost:8000'
  const response = await fetch(`${apiUrl}/assistant/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  })
  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}`)
  }
  const data = await response.json()
  return data.reply as string
}

export class ChatWidgetErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Chat widget error', error, info)
  }

  render() {
    return this.state.hasError ? null : this.props.children
  }
}

export default function ChatWidget() {
  const enabled = process.env.NEXT_PUBLIC_CHAT_ENABLED !== 'false'
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState('')
  const [sending, setSending] = useState(false)
  const [unavailable, setUnavailable] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: "Hi, I'm assistant here. What are you curious about?" },
  ])

  if (!enabled) return null

  async function sendMessage() {
    const trimmed = value.trim()
    if (!trimmed || sending) return
    setMessages((current) => [...current, { role: 'user', content: trimmed }])
    setValue('')
    setSending(true)
    setUnavailable(false)
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 10000)
    try {
      const response = await mockSendMessage(trimmed, controller.signal)
      setMessages((current) => [...current, { role: 'assistant', content: response }])
    } catch {
      setUnavailable(true)
    } finally {
      window.clearTimeout(timeout)
      setSending(false)
    }
  }

  return (
    <div className="chat-widget" aria-live="polite">
      {open && (
        <section className="chat-panel" aria-label="Assistant chat">
          <div className="chat-panel__header">
            <span>assistant here</span>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
          </div>
          <div className="chat-panel__messages">
            {messages.map((message, index) => (
              <p key={`${message.role}-${index}`} className={`chat-message chat-message--${message.role}`}>
                {message.content}
              </p>
            ))}
            {sending && <p className="chat-message chat-message--assistant">thinking…</p>}
            {unavailable && (
              <p className="chat-error">
                This assistant runs on a locally-hosted AI model for privacy, so it's offline in this hosted
                preview. See it working live in the demo video on{' '}
                <a href="https://github.com/sri-jahnavi21/KadambariProject" target="_blank" rel="noopener noreferrer">
                  GitHub
                </a>
                .
              </p>
            )}
          </div>
          <form className="chat-panel__form" onSubmit={(event) => { event.preventDefault(); void sendMessage() }}>
            <input value={value} onChange={(event) => setValue(event.target.value)} placeholder="Ask me anything" aria-label="Message assistant" />
            <button type="submit" aria-label="Send message">Send</button>
          </form>
        </section>
      )}
      <button type="button" className={`chat-bubble${open ? ' chat-bubble--open' : ''}`} onClick={() => setOpen((current) => !current)}>
        assistant here
      </button>
    </div>
  )
}

export { mockSendMessage }