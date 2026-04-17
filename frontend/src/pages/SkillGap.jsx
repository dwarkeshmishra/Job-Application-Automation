import { useState } from 'react';
import SkillGapCard from '../components/SkillGapCard';
import api from '../api/index';
import toast from 'react-hot-toast';

export default function SkillGap() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      // Fetch profile first
      const profileRes = await api.get('/profile');
      const profile = profileRes.data;
      if (profile.message) {
        toast.error('Upload your resume first');
        setLoading(false);
        return;
      }
      // For now, use mock data structure — in production this would call Gemini
      // via a dedicated endpoint
      setAnalysis({
        critical_gaps: [
          { skill: 'Docker', demand_percentage: 78, learning_resource: 'Docker official docs + TechWorld with Nana YouTube', estimated_hours: 20, priority: 'high' },
          { skill: 'Kubernetes', demand_percentage: 65, learning_resource: 'Kubernetes.io tutorials + KodeKloud', estimated_hours: 30, priority: 'high' },
          { skill: 'CI/CD', demand_percentage: 72, learning_resource: 'GitHub Actions docs + FreeCodeCamp', estimated_hours: 15, priority: 'high' },
        ],
        optional_gaps: [
          { skill: 'Redis', demand_percentage: 45, learning_resource: 'Redis University (free)', estimated_hours: 10, priority: 'medium' },
          { skill: 'GraphQL', demand_percentage: 35, learning_resource: 'How to GraphQL (howtographql.com)', estimated_hours: 12, priority: 'low' },
        ],
        strengths: profile.skills || ['Python', 'React', 'SQL'],
        '30_day_plan': [
          'Week 1: Docker fundamentals — containerize your existing projects',
          'Week 2: Kubernetes basics with minikube locally',
          'Week 3: CI/CD with GitHub Actions — automate builds',
          'Week 4: Add all to resume + 1 demo project showcasing all',
        ],
      });
      toast.success('Analysis complete!');
    } catch (e) {
      toast.error('Analysis failed');
    }
    setLoading(false);
  };

  return (
    <div className="slide-up">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Skill Gap Analysis</h2>
          <p>Identify missing skills and get a learning plan</p>
        </div>
        <button className="btn btn-primary" onClick={runAnalysis} disabled={loading} id="run-analysis-btn">
          {loading ? '⏳ Analyzing...' : '🎯 Run Analysis'}
        </button>
      </div>

      {analysis ? (
        <div className="fade-in">
          {/* Strengths */}
          <div className="card" style={{ marginBottom: 20 }}>
            <h3 style={{ marginBottom: 12, fontSize: '0.9rem', fontWeight: 600, color: 'var(--success)' }}>
              💪 Your Strengths
            </h3>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {analysis.strengths.map(s => (
                <span key={s} className="badge badge-success">{s}</span>
              ))}
            </div>
          </div>

          {/* Critical Gaps */}
          <h3 style={{ marginBottom: 12, fontSize: '0.95rem', fontWeight: 600, color: 'var(--danger)' }}>
            🔴 Critical Gaps
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16, marginBottom: 24 }}>
            {analysis.critical_gaps.map(g => <SkillGapCard key={g.skill} gap={g} />)}
          </div>

          {/* Optional Gaps */}
          <h3 style={{ marginBottom: 12, fontSize: '0.95rem', fontWeight: 600, color: 'var(--warning)' }}>
            🟡 Nice to Have
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16, marginBottom: 24 }}>
            {analysis.optional_gaps.map(g => <SkillGapCard key={g.skill} gap={g} />)}
          </div>

          {/* 30-Day Plan */}
          <div className="card">
            <h3 style={{ marginBottom: 12, fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-primary)' }}>
              📅 30-Day Learning Plan
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {analysis['30_day_plan'].map((step, i) => (
                <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <span style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: 'var(--accent-gradient)', color: 'white',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.75rem', fontWeight: 700, flexShrink: 0,
                  }}>
                    {i + 1}
                  </span>
                  <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', paddingTop: 4 }}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <div style={{ fontSize: '3rem', marginBottom: 16 }}>📈</div>
          <h3>No analysis yet</h3>
          <p>Click "Run Analysis" to compare your skills against market demand</p>
        </div>
      )}
    </div>
  );
}
