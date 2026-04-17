import { useState, useEffect } from 'react';
import { getJobs } from '../api/jobs';
import { getTracker } from '../api/tracker';
import { getProfile } from '../api/tracker';
import ATSGauge from '../components/ATSGauge';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#3b82f6', '#10b981', '#ef4444', '#64748b'];

export default function Dashboard() {
  const [stats, setStats] = useState({ summary: {}, recentJobs: [], topScores: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [jobsRes, trackerRes] = await Promise.all([
          getJobs({ limit: 5 }),
          getTracker(),
        ]);
        const summary = trackerRes.data.summary || {};
        const jobs = jobsRes.data.jobs || [];
        const topScores = trackerRes.data.applications
          ?.filter(a => a.ats_score)
          ?.sort((a, b) => b.ats_score - a.ats_score)
          ?.slice(0, 5) || [];

        setStats({ summary, recentJobs: jobs, topScores });
      } catch (e) {
        console.error('Dashboard load error:', e);
      }
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return <div className="loading-page"><div className="spinner" /><span>Loading dashboard...</span></div>;
  }

  const { summary } = stats;
  const pieData = [
    { name: 'Not Applied', value: summary.not_applied || 0 },
    { name: 'Applied', value: summary.applied || 0 },
    { name: 'Interview', value: summary.interview || 0 },
    { name: 'Offer', value: summary.offer || 0 },
    { name: 'Rejected', value: summary.rejected || 0 },
  ].filter(d => d.value > 0);

  const barData = stats.topScores.map(a => ({
    name: `${a.company?.substring(0, 12)}`,
    score: a.ats_score,
  }));

  return (
    <div className="slide-up">
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Your job application overview at a glance</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{summary.total || 0}</div>
          <div className="stat-label">Total Applications</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.applied || 0}</div>
          <div className="stat-label">Applied</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.interview || 0}</div>
          <div className="stat-label">Interviews</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{summary.offer || 0}</div>
          <div className="stat-label">Offers</div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 28 }}>
        {/* Status Breakdown */}
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
            Application Status
          </h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
                     dataKey="value" paddingAngle={3}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#1a1f35', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, color: '#f1f5f9' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: 40 }}>
              <h3>No data yet</h3>
              <p>Start adding jobs to see your stats</p>
            </div>
          )}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
            {pieData.map((d, i) => (
              <span key={d.name} style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: COLORS[i] }} />
                {d.name} ({d.value})
              </span>
            ))}
          </div>
        </div>

        {/* Top ATS Scores */}
        <div className="card">
          <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
            Top ATS Scores
          </h3>
          {barData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData}>
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#1a1f35', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 8, color: '#f1f5f9' }} />
                <Bar dataKey="score" fill="url(#scoreGradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#8b5cf6" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state" style={{ padding: 40 }}>
              <h3>No scores yet</h3>
              <p>Generate resumes to see ATS scores</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="card">
        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 16, color: 'var(--text-secondary)' }}>
          Recent Jobs
        </h3>
        {stats.recentJobs.length > 0 ? (
          <div className="table-wrapper" style={{ border: 'none' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Role</th><th>Company</th><th>Source</th><th>Match</th><th>ATS</th>
                </tr>
              </thead>
              <tbody>
                {stats.recentJobs.map(j => (
                  <tr key={j.id}>
                    <td style={{ fontWeight: 500 }}>{j.title}</td>
                    <td style={{ color: 'var(--accent-primary)' }}>{j.company}</td>
                    <td><span className="badge badge-info">{j.source}</span></td>
                    <td>{j.match_score ? `${Math.round(j.match_score * 100)}%` : '—'}</td>
                    <td><ATSGauge score={j.ats_score} size={36} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <h3>No jobs yet</h3>
            <p>Scrape jobs or add them manually to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}
