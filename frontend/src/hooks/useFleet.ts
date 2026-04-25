import { useEffect, useState } from 'react'
import { FleetResponse } from '../types/types'
import { fetchFleet } from '../api/fleet'

export function useFleet(identityToken: string) {
  const [data, setData] = useState<FleetResponse | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Always fetch — local backend only needs X-API-Key, not a Bearer token

    let cancelled = false

    const load = () => {
      fetchFleet(identityToken)
        .then((result) => {
          if (!cancelled) {
            setData(result)
            setLastUpdated(new Date())
            setLoading(false)
            setError(null)
          }
        })
        .catch((err: Error) => {
          if (!cancelled) {
            setError(err.message)
            setLoading(false)
          }
        })
    }

    load()
    const interval = setInterval(load, 10000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [identityToken])

  return { data, lastUpdated, loading, error }
}
