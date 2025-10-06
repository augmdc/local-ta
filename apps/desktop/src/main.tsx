import React, { useEffect, useMemo, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ingest, query, uploadAssignment, uploadRubric } from './lib/api'

type Message = { role: 'user' | 'assistant' | 'system'; content: string }

type UploadInfo = { stored_as: string; sha256: string } | null

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', content: 'Welcome to Local TA. Ask a question or build the index.' },
  ])
  const [busy, setBusy] = useState(false)
  const [assignment, setAssignment] = useState<UploadInfo>(null)
  const [rubric, setRubric] = useState<UploadInfo>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const canSend = useMemo(() => input.trim().length > 0 && !busy, [input, busy])

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const handleIngest = async () => {
    setBusy(true)
    try {
      await ingest()
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Index built successfully.' }])
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: 'assistant', content: e?.message ?? 'Ingest failed' }])
    } finally {
      setBusy(false)
    }
  }

  const handleAsk = async () => {
    if (!canSend) return
    const question = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setBusy(true)
    try {
      const res = await query(question)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer }])
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: 'assistant', content: e?.message ?? 'Query failed' }])
    } finally {
      setBusy(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleAsk()
    }
  }

  const onUploadAssignment = async (file: File) => {
    setBusy(true)
    try {
      const res = await uploadAssignment(file)
      setAssignment({ stored_as: res.stored_as, sha256: res.sha256 })
      setMessages((prev) => [...prev, { role: 'assistant', content: `Assignment uploaded: ${res.stored_as}` }])
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: 'assistant', content: e?.message ?? 'Assignment upload failed' }])
    } finally {
      setBusy(false)
    }
  }

  const onUploadRubric = async (file: File) => {
    setBusy(true)
    try {
      const res = await uploadRubric(file)
      setRubric({ stored_as: res.stored_as, sha256: res.sha256 })
      setMessages((prev) => [...prev, { role: 'assistant', content: `Rubric uploaded: ${res.stored_as}` }])
    } catch (e: any) {
      setMessages((prev) => [...prev, { role: 'assistant', content: e?.message ?? 'Rubric upload failed' }])
    } finally {
      setBusy(false)
    }
  }

  const onFilePick = (e: React.ChangeEvent<HTMLInputElement>, type: 'assignment' | 'rubric') => {
    const f = e.target.files?.[0]
    if (!f) return
    if (type === 'assignment') onUploadAssignment(f)
    else onUploadRubric(f)
    // reset input so same file can be chosen again
    e.currentTarget.value = ''
  }

  return (
    <div style={{ padding: 16, maxWidth: 920, margin: '0 auto', fontFamily: 'Inter, system-ui, sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
        <h1 style={{ marginBottom: 8, marginTop: 0 }}>Local TA</h1>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <input type="file" accept="application/pdf" onChange={(e) => onFilePick(e, 'assignment')} disabled={busy} />
            <span>Upload assignment (PDF)</span>
          </label>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <input type="file" accept="application/pdf,.txt,.md" onChange={(e) => onFilePick(e, 'rubric')} disabled={busy} />
            <span>Upload rubric (PDF/TXT/MD)</span>
          </label>
          <button onClick={handleIngest} disabled={busy} style={{ height: 32 }}>Build index</button>
        </div>
      </div>

      <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>
        {assignment && <span>Assignment: {assignment.stored_as} </span>}
        {rubric && <span style={{ marginLeft: 8 }}>Rubric: {rubric.stored_as}</span>}
      </div>

      <div ref={listRef} style={{ flex: 1, overflowY: 'auto', padding: 12, border: '1px solid #eee', borderRadius: 8, background: '#fafafa' }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
            <div style={{ fontWeight: 600, color: m.role === 'user' ? '#2563eb' : m.role === 'assistant' ? '#16a34a' : '#6b7280', minWidth: 80, textAlign: 'right' }}>
              {m.role}
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>
          </div>
        ))}
        {busy && (
          <div style={{ marginTop: 8, color: '#666' }}>Working…</div>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
        <input
          type="text"
          placeholder="Ask a question… (Cmd/Ctrl+Enter to send)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          style={{ flex: 1, padding: 10, border: '1px solid #ccc', borderRadius: 6 }}
        />
        <button onClick={handleAsk} disabled={!canSend} style={{ minWidth: 80 }}>Send</button>
      </div>
    </div>
  )
}

const container = document.getElementById('root')!
const root = createRoot(container)
root.render(<App />)