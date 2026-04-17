export default function SkillGapCard({ gap }) {
  const priorityColor = gap.priority === 'high' ? 'var(--danger)'
    : gap.priority === 'medium' ? 'var(--warning)' : 'var(--success)';

  return (
    <div className="card fade-in" style={{ padding: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{gap.skill}</span>
        <span className="badge" style={{
          background: `${priorityColor}18`,
          color: priorityColor,
        }}>
          {gap.priority}
        </span>
      </div>
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6 }}>
        Demand: {gap.demand_percentage}% of job postings
      </div>
      <div style={{
        height: 4, background: 'var(--border-color)', borderRadius: 2,
        marginBottom: 10, overflow: 'hidden'
      }}>
        <div style={{
          height: '100%', width: `${gap.demand_percentage}%`,
          background: priorityColor, borderRadius: 2,
          transition: 'width 0.8s ease'
        }} />
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
        📚 {gap.learning_resource}
      </div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4 }}>
        ⏱ ~{gap.estimated_hours}h to learn
      </div>
    </div>
  );
}
