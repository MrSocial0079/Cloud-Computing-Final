import { AgentSummary } from '../types/types'
import { StatusBadge } from './StatusBadge'

interface AgentRowProps {
  agent: AgentSummary
}

function formatCost(usd: number): string {
  if (usd === 0) return '$0.00'
  if (usd >= 0.01) return '$' + usd.toFixed(2)
  const decimals = Math.min(Math.max(2, Math.ceil(-Math.log10(usd)) + 2), 8)
  return '$' + usd.toFixed(decimals)
}

function formatHeartbeat(lastHeartbeatAt: string | null): { text: string; color: string } {
  if (!lastHeartbeatAt) return { text: 'offline', color: '#F05050' }
  const diffMs = Date.now() - new Date(lastHeartbeatAt).getTime()
  const diffSec = Math.floor(diffMs / 1000)
  if (diffSec < 60) return { text: `${diffSec}s ago`, color: '#4ADE80' }
  if (diffSec < 180) return { text: `${Math.floor(diffSec / 60)}m ago`, color: '#E8A020' }
  if (diffSec < 3600) return { text: `${Math.floor(diffSec / 60)}m ago`, color: '#F05050' }
  return { text: `${Math.floor(diffSec / 3600)}h ago`, color: '#F05050' }
}

export function AgentRow({ agent }: AgentRowProps) {
  const hb = formatHeartbeat(agent.last_heartbeat_at)

  const envStyle =
    agent.environment === 'production'
      ? {
          background: 'rgba(200,134,30,0.15)',
          border: '1px solid rgba(200,134,30,0.4)',
          color: '#C8861E',
        }
      : {
          background: 'rgba(107,143,173,0.15)',
          border: '1px solid rgba(107,143,173,0.4)',
          color: '#6B8FAD',
        }

  return (
    <tr
      style={{ backgroundColor: '#162E4B', borderBottom: '1px solid rgba(200,134,30,0.1)', cursor: 'default' }}
      onMouseEnter={(e) => {
        ;(e.currentTarget as HTMLTableRowElement).style.backgroundColor = '#1E3D60'
      }}
      onMouseLeave={(e) => {
        ;(e.currentTarget as HTMLTableRowElement).style.backgroundColor = '#162E4B'
      }}
    >
      {/* Agent name + owner */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div
            style={{
              width: 8,
              height: 8,
              backgroundColor: '#C8861E',
              borderRadius: 2,
              transform: 'rotate(45deg)',
              flexShrink: 0,
            }}
          />
          <div>
            <div style={{ fontWeight: 600, color: '#D5E8F5', fontSize: 14 }}>{agent.name}</div>
            <div style={{ color: '#6B8FAD', fontSize: 12, marginTop: 2 }}>{agent.owner}</div>
          </div>
        </div>
      </td>

      {/* Framework */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle', color: '#D5E8F5', fontSize: 13 }}>
        {agent.framework}
      </td>

      {/* Model */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle', color: '#D5E8F5', fontSize: 13 }}>
        {agent.model}
      </td>

      {/* Environment */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle' }}>
        <span
          style={{
            ...envStyle,
            borderRadius: 3,
            padding: '2px 8px',
            fontSize: 10,
            letterSpacing: 1,
            fontWeight: 600,
            display: 'inline-block',
          }}
        >
          {agent.environment}
        </span>
      </td>

      {/* Status */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle' }}>
        <StatusBadge status={agent.status} />
      </td>

      {/* Cost 30d */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle', color: '#D5E8F5', fontSize: 13, fontWeight: 600 }}>
        {formatCost(agent.cost_usd_30d)}
      </td>

      {/* Last heartbeat */}
      <td style={{ padding: '14px 16px', verticalAlign: 'middle', color: hb.color, fontSize: 13 }}>
        {hb.text}
      </td>
    </tr>
  )
}
