import { useState } from 'react';
import useJobs from '../hooks/useJobs';
import { generateResume } from '../api/resume';
import { TEMPLATE_OPTIONS } from '../utils/constants';
import ATSGauge from '../components/ATSGauge';
import toast from 'react-hot-toast';

export default function ResumeStudio() {
  const { jobs } = useJobs({ limit: 100 });
  const [selectedJob, setSelectedJob] = useState(null);
  const [template, setTemplate] = useState('modern');
  const [includeCover, setIncludeCover] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    if (!selectedJob) {
      toast.error('Select a job first');
      return;
    }
    setGenerating(true);
    setResult(null);
    try {
      const res = await generateResume({
        job_id: selectedJob,
        template,
        include_cover_letter: includeCover,
      });
      setResult(res.data);
      toast.success(`Resume generated! ATS Score: ${res.data.ats_score}`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Generation failed');
    }
    setGenerating(false);
  };

  return (
    <div className="slide-up">
      <div className="page-header">
        <h2>Resume Studio</h2>
        <p>Generate tailored resumes with AI</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Controls */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>Generate Resume</h3>

          <div className="form-group">
            <label>Select Job</label>
            <select className="select" value={selectedJob || ''} id="resume-job-select"
              onChange={e => setSelectedJob(parseInt(e.target.value))}>
              <option value="">Choose a job...</option>
              {jobs.map(j => (
                <option key={j.id} value={j.id}>
                  {j.title} — {j.company}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Template</label>
            <div style={{ display: 'flex', gap: 10 }}>
              {TEMPLATE_OPTIONS.map(t => (
                <button key={t.value}
                  className={`btn ${template === t.value ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                  onClick={() => setTemplate(t.value)}>
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input type="checkbox" checked={includeCover}
                onChange={e => setIncludeCover(e.target.checked)}
                style={{ width: 16, height: 16, accentColor: 'var(--accent-primary)' }} />
              Include Cover Letter
            </label>
          </div>

          <button className="btn btn-primary" onClick={handleGenerate}
            disabled={generating || !selectedJob} id="generate-resume-btn"
            style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
            {generating ? (
              <><div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> Generating...</>
            ) : (
              '🚀 Generate Tailored Resume'
            )}
          </button>
        </div>

        {/* Result */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>Result</h3>

          {result ? (
            <div className="fade-in">
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
                <ATSGauge score={result.ats_score} size={80} />
                <div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>ATS Score: {result.ats_score}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    {result.ats_score >= 80 ? '✅ Great match!' :
                     result.ats_score >= 60 ? '⚡ Good, can improve' :
                     '⚠️ Needs more work'}
                  </div>
                </div>
              </div>

              {result.tailored_summary && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4 }}>
                    TAILORED SUMMARY
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    {result.tailored_summary}
                  </p>
                </div>
              )}

              {result.keywords_added?.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 6 }}>
                    KEYWORDS ADDED
                  </div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {result.keywords_added.map(k => (
                      <span key={k} className="skill-tag">{k}</span>
                    ))}
                  </div>
                </div>
              )}

              {result.missing_skills?.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--danger)', marginBottom: 6 }}>
                    MISSING SKILLS
                  </div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {result.missing_skills.map(s => (
                      <span key={s} className="badge badge-danger">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Download links */}
              <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                {result.resume_pdf_url && (
                  <a href={result.resume_pdf_url} target="_blank" rel="noreferrer"
                    className="btn btn-primary btn-sm">📄 Download PDF</a>
                )}
                {result.resume_docx_url && (
                  <a href={result.resume_docx_url} target="_blank" rel="noreferrer"
                    className="btn btn-secondary btn-sm">📝 Download DOCX</a>
                )}
                {result.cover_letter_url && (
                  <a href={result.cover_letter_url} target="_blank" rel="noreferrer"
                    className="btn btn-secondary btn-sm">✉️ Cover Letter</a>
                )}
              </div>
            </div>
          ) : (
            <div className="empty-state" style={{ padding: 40 }}>
              <h3>No resume generated</h3>
              <p>Select a job and click Generate to create a tailored resume</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
