export interface AgentSummary {
  agent_id: string
  name: string
  owner: string
  framework: string
  model: string
  environment: string
  status: string
  tools: string[]
  tags: Record<string, string>
  registered_at: string
  last_heartbeat_at: string | null
  cost_usd_total: number
  cost_usd_30d: number
  call_count_total: number
}

export interface FleetResponse {
  total_agents: number
  total_cost_usd: number
  agents: AgentSummary[]
}
