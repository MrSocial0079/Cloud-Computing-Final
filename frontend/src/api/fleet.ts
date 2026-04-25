import { FleetResponse } from '../types/types'

export async function fetchFleet(identityToken: string): Promise<FleetResponse> {
  const headers: Record<string, string> = {
    'X-API-Key': 'invexsai_dev_testkey123',
  }
  if (identityToken) {
    headers['Authorization'] = `Bearer ${identityToken}`
  }
  const res = await fetch('/v1/fleet', { headers })
  if (!res.ok) {
    throw new Error(`Fleet fetch failed: ${res.status}`)
  }
  return res.json()
}
