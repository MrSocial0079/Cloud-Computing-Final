export function LiveBadge() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div
        className="animate-pulse"
        style={{
          width: 14,
          height: 14,
          borderRadius: '50%',
          border: '1.5px solid #C8861E',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: '#C8861E',
          }}
        />
      </div>
      <span
        style={{
          color: '#C8861E',
          fontSize: 11,
          letterSpacing: 2,
          textTransform: 'uppercase',
          fontWeight: 600,
        }}
      >
        LIVE
      </span>
    </div>
  )
}
