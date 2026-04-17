import { formatMatchPercent } from '../utils/formatters';

export default function JobCard({ job, onClick }) {
  const scoreColor = job.ats_score >= 80
    ? 'var(--success)' : job.ats_score >= 60
    ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className="job-card fade-in" onClick={() => onClick?.(job)} id={`job-card-${job.id}`}>
      <div className="job-card-header">
        <div>
          <div className="job-card-title">{job.title}</div>
          <div className="job-card-company">{job.company}</div>
        </div>
        {job.ats_score != null && (
          <div style={{
            fontSize: '1.3rem', fontWeight: 800, color: scoreColor,
            minWidth: 44, textAlign: 'right'
          }}>
            {job.ats_score}
          </div>
        )}
      </div>
      <div className="job-card-meta">
        {job.location && <span>📍 {job.location}</span>}
        {job.source && <span>🔗 {job.source}</span>}
        {job.match_score != null && (
          <span>🎯 {formatMatchPercent(job.match_score)} match</span>
        )}
      </div>
      {job.required_skills?.length > 0 && (
        <div className="job-card-skills">
          {job.required_skills.slice(0, 6).map((s) => (
            <span key={s} className="skill-tag">{s}</span>
          ))}
          {job.required_skills.length > 6 && (
            <span className="skill-tag" style={{ opacity: 0.5 }}>
              +{job.required_skills.length - 6}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
