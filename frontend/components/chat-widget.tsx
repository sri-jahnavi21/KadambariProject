'use client'

import { Component, type ErrorInfo, type ReactNode, useEffect, useState } from 'react'

type ChatMessage = { role: 'assistant' | 'user'; content: string; guard?: string }

// Starter questions. They only cover facts the assistant actually knows
// (products, price, the craft), so they do not invite made-up policies.
const SUGGESTIONS = [
  'What shoes do you sell?',
  'How much do they cost?',
  'Tell me about Kalamkari art',
  'Are the shoes hand-painted?',
]

// Looks for the name of the guard that fired in the backend's answer.
// If the backend sends no such field, this returns undefined and nothing extra is shown.
function readGuard(data: unknown): string | undefined {
  if (!data || typeof data !== 'object') return undefined
  const record = data as Record<string, unknown>
  const candidates = [record.triggered_categories, record.blocked_by, record.guard, record.triggered_guard, record.guards_triggered, record.flags]
  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate.trim()) return candidate.trim().replace(/[_-]+/g, ' ')
    if (Array.isArray(candidate)) {
      const names = candidate.filter((item): item is string => typeof item === 'string' && item.trim() !== '')
      if (names.length) return names.join(', ').replace(/[_-]+/g, ' ')
    }
  }
  return undefined
}

async function sendToBackend(message: string, signal: AbortSignal) {
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
  return { reply: data.reply as string, guard: readGuard(data) }
}

// Kept with the same name and the same return value (just the reply text) as before.
async function mockSendMessage(message: string, signal: AbortSignal) {
  const result = await sendToBackend(message, signal)
  return result.reply
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

  async function sendText(text: string) {
    const trimmed = text.trim()
    if (!trimmed || sending) return
    setMessages((current) => [...current, { role: 'user', content: trimmed }])
    setSending(true)
    setUnavailable(false)
    const controller = new AbortController()
    // Local model replies can take 6-20 seconds, so allow up to 60 seconds.
    const timeout = window.setTimeout(() => controller.abort(), 60000)
    try {
      const result = await sendToBackend(trimmed, controller.signal)
      setMessages((current) => [...current, { role: 'assistant', content: result.reply, guard: result.guard }])
    } catch {
      setUnavailable(true)
    } finally {
      window.clearTimeout(timeout)
      setSending(false)
    }
  }

  async function sendMessage() {
    const trimmed = value.trim()
    if (!trimmed || sending) return
    setValue('')
    await sendText(trimmed)
  }

  // Lets the "Ask about this shoe" buttons on the page open the chat with a question.
  useEffect(() => {
    function handleAsk(event: Event) {
      const text = (event as CustomEvent<string>).detail
      if (typeof text === 'string' && text.trim()) {
        setOpen(true)
        void sendText(text)
      }
    }
    window.addEventListener('kadambari:ask', handleAsk)
    return () => window.removeEventListener('kadambari:ask', handleAsk)
  })

  if (!enabled) return null

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
              <div key={`${message.role}-${index}`} style={{ display: 'flex', flexDirection: 'column', alignItems: message.role === 'user' ? 'flex-end' : 'flex-start', gap: '4px' }}>
                <p className={`chat-message chat-message--${message.role}`}>{message.content}</p>
                {message.guard && (
                  <span style={{ fontSize: '0.72rem', fontWeight: 700, border: '1.5px solid #111', borderRadius: '999px', padding: '1px 8px', background: '#ffd400' }}>
                    Guard triggered: {message.guard}
                  </span>
                )}
              </div>
            ))}
            {messages.length === 1 && !sending && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginTop: '0.5rem' }}>
                {SUGGESTIONS.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => void sendText(question)}
                    style={{ border: '1.5px solid #111', background: 'transparent', color: 'inherit', font: 'inherit', fontSize: '0.85rem', padding: '0.3rem 0.7rem', borderRadius: '999px', cursor: 'pointer' }}
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
            {sending && <p className="chat-message chat-message--assistant">thinking… this can take a few seconds</p>}
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
