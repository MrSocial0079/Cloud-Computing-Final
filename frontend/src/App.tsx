import { useState } from 'react'
import { useFleet } from './hooks/useFleet'
import { LiveBadge } from './components/LiveBadge'
import { MetricCard } from './components/MetricCard'
import { FleetTable } from './components/FleetTable'

const LogoSVG = ({ height = 44 }: { height?: number }) => (
  <svg viewBox="0 0 680 210" xmlns="http://www.w3.org/2000/svg" height={height}>
    <polygon fill="none" stroke="#4A7AA0" strokeWidth="1.2"
      points="90,42 140,71 140,129 90,158 40,129 40,71"/>
    <polygon fill="none" stroke="#4A7AA0" strokeWidth="0.7" opacity="0.35"
      points="90,70 116,85 116,115 90,130 64,115 64,85"/>
    <line fill="none" stroke="#5A8AB0" strokeWidth="2" strokeLinecap="round"
      x1="40" y1="71" x2="140" y2="129"/>
    <line fill="none" stroke="#5A8AB0" strokeWidth="2" strokeLinecap="round"
      x1="140" y1="71" x2="40" y2="129"/>
    <line fill="none" stroke="#C8861E" strokeWidth="2.5" strokeLinecap="round"
      x1="90" y1="36" x2="90" y2="164"/>
    <circle fill="#4A7AA0" cx="40" cy="71" r="3.5"/>
    <circle fill="#4A7AA0" cx="140" cy="71" r="3.5"/>
    <circle fill="#4A7AA0" cx="40" cy="129" r="3.5"/>
    <circle fill="#4A7AA0" cx="140" cy="129" r="3.5"/>
    <circle fill="#C8861E" cx="90" cy="36" r="5"/>
    <circle fill="#C8861E" cx="90" cy="164" r="5"/>
    <circle fill="#C8861E" cx="90" cy="100" r="10"/>
    <circle cx="90" cy="100" r="4" fill="white" opacity="0.75"/>
    <text x="178" y="120"
      fontFamily="'Helvetica Neue',Arial,sans-serif"
      fontSize="62" fontWeight="800" letterSpacing="3"
      fill="#D5E8F5">INVEXS</text>
    <text x="455" y="120"
      fontFamily="'Helvetica Neue',Arial,sans-serif"
      fontSize="62" fontWeight="300" letterSpacing="3"
      fill="#C8861E">AI</text>
    <line x1="178" y1="133" x2="530" y2="133"
      stroke="#C8861E" strokeWidth="1" opacity="0.4"/>
    <text x="180" y="153"
      fontFamily="'Helvetica Neue',Arial,sans-serif"
      fontSize="13" fontWeight="400" letterSpacing="6"
      fill="#C8861E" opacity="0.85">INTELLIGENT MANAGEMENT SYSTEMS</text>
  </svg>
)

function TokenGate({ onConnect }: { onConnect: (token: string) => void }) {
  const [draft, setDraft] = useState('')
  const trimmed = draft.trim()

  return (
    <div
      style={{
        backgroundColor: '#0C1E35',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: "'Helvetica Neue', Arial, sans-serif",
        padding: 24,
      }}
    >
      <div
        style={{
          backgroundColor: '#162E4B',
          borderLeft: '3px solid #C8861E',
          border: '1px solid rgba(200,134,30,0.2)',
          borderRadius: 8,
          padding: '48px 40px',
          width: '100%',
          maxWidth: 520,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32 }}>
          <LogoSVG height={56} />
        </div>

        <div
          style={{
            fontSize: 11,
            letterSpacing: 4,
            color: '#6B8FAD',
            textTransform: 'uppercase',
            textAlign: 'center',
            marginBottom: 8,
          }}
        >
          Fleet Authentication Required
        </div>

        <div style={{ height: 1, backgroundColor: 'rgba(200,134,30,0.15)', marginBottom: 28 }} />

        <div
          style={{
            backgroundColor: 'rgba(12,30,53,0.7)',
            border: '1px solid rgba(200,134,30,0.2)',
            borderRadius: 6,
            padding: '14px 16px',
            marginBottom: 20,
          }}
        >
          <div
            style={{
              fontSize: 11,
              letterSpacing: 2,
              color: '#6B8FAD',
              textTransform: 'uppercase',
              marginBottom: 8,
            }}
          >
            Step 1 — Run this in your terminal:
          </div>
          <code
            style={{
              display: 'block',
              fontSize: 13,
              color: '#C8861E',
              fontFamily: "'Menlo', 'Monaco', 'Courier New', monospace",
            }}
          >
            gcloud auth print-identity-token
          </code>
        </div>

        <div
          style={{
            fontSize: 11,
            letterSpacing: 2,
            color: '#6B8FAD',
            textTransform: 'uppercase',
            marginBottom: 8,
          }}
        >
          Step 2 — Paste the token below:
        </div>

        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="eyJhbGciOiJSUzI1NiIsImtpZCI6..."
          rows={4}
          style={{
            width: '100%',
            backgroundColor: 'rgba(12,30,53,0.8)',
            border: '1px solid rgba(200,134,30,0.3)',
            borderRadius: 6,
            padding: '10px 12px',
            color: '#D5E8F5',
            fontSize: 12,
            fontFamily: "'Menlo', 'Monaco', 'Courier New', monospace",
            resize: 'vertical',
            outline: 'none',
            marginBottom: 16,
            boxSizing: 'border-box',
          }}
        />

        <button
          onClick={() => onConnect(trimmed)}
          disabled={!trimmed}
          style={{
            width: '100%',
            padding: '12px 0',
            backgroundColor: trimmed ? '#C8861E' : 'rgba(200,134,30,0.2)',
            border: 'none',
            borderRadius: 6,
            color: trimmed ? '#0C1E35' : '#6B8FAD',
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: 3,
            textTransform: 'uppercase',
            cursor: trimmed ? 'pointer' : 'not-allowed',
            fontFamily: "'Helvetica Neue', Arial, sans-serif",
          }}
        >
          Connect to Fleet
        </button>
      </div>
    </div>
  )
}

function Dashboard({ token, onReconnect }: { token: string; onReconnect: () => void }) {
  const { data, lastUpdated, loading, error } = useFleet(token)

  const sortedAgents = data
    ? [...data.agents].sort((a, b) => b.cost_usd_30d - a.cost_usd_30d)
    : []

  return (
    <div style={{ backgroundColor: '#0C1E35', minHeight: '100vh', fontFamily: "'Helvetica Neue', Arial, sans-serif" }}>
      <header
        style={{
          backgroundColor: '#0C1E35',
          borderBottom: '1px solid rgba(200,134,30,0.3)',
          padding: '0 32px',
          height: 72,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <LogoSVG />
        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          <LiveBadge />
          <div style={{ width: 1, height: 20, backgroundColor: 'rgba(200,134,30,0.3)' }} />
          <span style={{ fontSize: 10, letterSpacing: 3, color: '#6B8FAD', textTransform: 'uppercase' }}>
            FLEET CONTROL
          </span>
          <div style={{ width: 1, height: 20, backgroundColor: 'rgba(200,134,30,0.3)' }} />
          <button
            onClick={onReconnect}
            style={{
              backgroundColor: 'transparent',
              border: '1px solid rgba(200,134,30,0.4)',
              borderRadius: 4,
              color: '#C8861E',
              fontSize: 10,
              letterSpacing: 2,
              textTransform: 'uppercase',
              padding: '5px 10px',
              cursor: 'pointer',
              fontFamily: "'Helvetica Neue', Arial, sans-serif",
            }}
          >
            Reconnect
          </button>
        </div>
      </header>

      {error && (
        <div
          style={{
            backgroundColor: 'rgba(240,80,80,0.12)',
            borderBottom: '1px solid rgba(240,80,80,0.4)',
            padding: '10px 32px',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
          }}
        >
          <span style={{ color: '#F05050', fontSize: 11, letterSpacing: 1.5, fontWeight: 600 }}>
            API ERROR
          </span>
          <span style={{ color: '#F05050', fontSize: 12 }}>{error}</span>
          <span style={{ color: 'rgba(240,80,80,0.6)', fontSize: 11, marginLeft: 'auto' }}>
            Token may have expired — click Reconnect to refresh
          </span>
        </div>
      )}

      <main style={{ padding: 32 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
          <MetricCard
            label="TOTAL AGENTS"
            value={data ? String(data.total_agents) : '—'}
            sublabel="registered"
          />
          <MetricCard
            label="FLEET COST (30D)"
            value={data ? (() => {
            const usd = data.total_cost_usd
            if (usd === 0) return '$0.00'
            if (usd >= 0.01) return '$' + usd.toFixed(2)
            const decimals = Math.min(Math.max(2, Math.ceil(-Math.log10(usd)) + 2), 8)
            return '$' + usd.toFixed(decimals)
          })() : '—'}
            sublabel="across all agents"
          />
          <MetricCard
            label="ACTIVE AGENTS"
            value={data ? String(data.agents.filter((a) => a.status !== 'dead').length) : '—'}
            sublabel="healthy or degraded"
          />
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', color: '#C8861E', letterSpacing: 4, fontSize: 13, paddingTop: 60 }}>
            INITIALIZING...
          </div>
        ) : (
          <FleetTable agents={sortedAgents} />
        )}

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 10, letterSpacing: 3, color: 'rgba(107,143,173,0.5)' }}>
            INVEXSAI INTELLIGENT MANAGEMENT SYSTEMS
          </span>
          <span style={{ fontSize: 10, letterSpacing: 2, color: '#6B8FAD' }}>
            LAST SYNC {lastUpdated ? lastUpdated.toLocaleTimeString() : '—'}
          </span>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  // 'local' sentinel bypasses the Cloud Run token gate for local demo mode.
  // The proxy targets localhost:8080 which only checks X-API-Key (no Bearer).
  const [token, setToken] = useState<string>('local')

  if (!token) {
    return <TokenGate onConnect={setToken} />
  }

  return <Dashboard token={token} onReconnect={() => setToken('')} />
}
