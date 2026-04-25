interface StatusBadgeProps {
  status: string
}

function getStatusStyle(status: string): {
  background: string
  border: string
  color: string
  label: string
} {
  switch (status) {
    case 'healthy':
      return {
        background: 'rgba(74,222,128,0.15)',
        border: '1px solid #4ADE80',
        color: '#4ADE80',
        label: 'HEALTHY',
      }
    case 'degraded':
      return {
        background: 'rgba(232,160,32,0.15)',
        border: '1px solid #E8A020',
        color: '#E8A020',
        label: 'DEGRADED',
      }
    case 'error':
      return {
        background: 'rgba(240,80,80,0.15)',
        border: '1px solid #F05050',
        color: '#F05050',
        label: 'ERROR',
      }
    case 'dead':
      return {
        background: 'rgba(240,80,80,0.10)',
        border: '1px solid rgba(240,80,80,0.4)',
        color: 'rgba(240,80,80,0.6)',
        label: 'DEAD',
      }
    default:
      return {
        background: 'rgba(107,143,173,0.15)',
        border: '1px solid rgba(107,143,173,0.4)',
        color: '#6B8FAD',
        label: status.toUpperCase(),
      }
  }
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const s = getStatusStyle(status)
  return (
    <span
      style={{
        background: s.background,
        border: s.border,
        color: s.color,
        borderRadius: 3,
        padding: '3px 8px',
        fontSize: 10,
        letterSpacing: 1.5,
        fontWeight: 600,
        display: 'inline-block',
        whiteSpace: 'nowrap',
      }}
    >
      {s.label}
    </span>
  )
}
