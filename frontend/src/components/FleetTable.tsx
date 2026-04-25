import { AgentSummary } from '../types/types'
import { AgentRow } from './AgentRow'

interface FleetTableProps {
  agents: AgentSummary[]
}

const HEADERS = ['Agent', 'Framework', 'Model', 'Environment', 'Status', 'Cost (30d)', 'Last Heartbeat']

export function FleetTable({ agents }: FleetTableProps) {
  return (
    <div
      style={{
        backgroundColor: '#0C1E35',
        borderRadius: 8,
        border: '1px solid rgba(200,134,30,0.2)',
        overflow: 'hidden',
      }}
    >
      {/* Section header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(200,134,30,0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span
          style={{
            fontSize: 11,
            letterSpacing: 4,
            color: '#6B8FAD',
            textTransform: 'uppercase',
            fontWeight: 600,
          }}
        >
          AGENT FLEET
        </span>
        <span style={{ color: '#C8861E', fontSize: 12, fontWeight: 600 }}>
          {agents.length} agents
        </span>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead style={{ backgroundColor: '#0C1E35' }}>
          <tr>
            {HEADERS.map((h) => (
              <th
                key={h}
                style={{
                  padding: '10px 16px',
                  fontSize: 10,
                  letterSpacing: 2,
                  textTransform: 'uppercase',
                  color: '#6B8FAD',
                  textAlign: 'left',
                  borderBottom: '1px solid rgba(200,134,30,0.15)',
                  fontWeight: 600,
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {agents.map((agent) => (
            <AgentRow key={agent.agent_id} agent={agent} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
