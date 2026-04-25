interface MetricCardProps {
  label: string
  value: string
  sublabel?: string
}

export function MetricCard({ label, value, sublabel }: MetricCardProps) {
  return (
    <div
      style={{
        backgroundColor: '#162E4B',
        borderLeft: '3px solid #C8861E',
        borderTop: '1px solid rgba(200,134,30,0.2)',
        borderRight: '1px solid rgba(200,134,30,0.2)',
        borderBottom: '1px solid rgba(200,134,30,0.2)',
        borderRadius: 8,
        padding: '20px 24px',
      }}
    >
      <div
        style={{
          fontSize: 11,
          letterSpacing: 3,
          textTransform: 'uppercase',
          color: '#6B8FAD',
          marginBottom: 8,
          fontWeight: 500,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 32,
          fontWeight: 800,
          color: '#D5E8F5',
          fontFamily: "'Helvetica Neue', Arial, sans-serif",
          lineHeight: 1,
        }}
      >
        {value}
      </div>
      {sublabel && (
        <div
          style={{
            fontSize: 12,
            color: '#C8861E',
            marginTop: 4,
          }}
        >
          {sublabel}
        </div>
      )}
    </div>
  )
}
