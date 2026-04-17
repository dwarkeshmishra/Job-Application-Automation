import { getScoreColor } from '../utils/formatters';

export default function ATSGauge({ score, size = 64 }) {
  if (score == null) return <span style={{ color: 'var(--text-muted)' }}>—</span>;

  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = getScoreColor(score);

  return (
    <div className="score-ring" style={{ width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="bg"
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" strokeWidth="4"
        />
        <circle
          className="progress"
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth="4"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
      <span className="score-value" style={{ color, fontSize: size > 50 ? '0.85rem' : '0.65rem' }}>
        {Math.round(score)}
      </span>
    </div>
  );
}
