import { useState, useEffect } from 'react';
import { getTracker, updateApplication, exportExcel } from '../api/tracker';
import StatusBadge from '../components/StatusBadge';
import ATSGauge from '../components/ATSGauge';
import { formatDate } from '../utils/formatters';
import { STATUS_OPTIONS } from '../utils/constants';
import toast from 'react-hot-toast';

export default function ApplicationTracker() {
  const [data, setData] = useState({ summary: {}, applications: [] });
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  const load = async () => {
    setLoading(true);
    try {
      const res = await getTracker();
      setData(res.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleStatusChange = async (appId, newStatus) => {
    try {
      await updateApplication(appId, { status: newStatus });
      toast.success('Status updated');
      load();
    } catch (e) {
      toast.error('Update failed');
    }
  };

  const handleEdit = (app) => {
    setEditingId(app.id);
    setEditForm({ notes: app.notes || '', status: app.status });
  };

  const saveEdit = async () => {
    try {
      await updateApplication(editingId, editForm);
      toast.success('Updated');
      setEditingId(null);
      load();
    } catch (e) {
      toast.error('Update failed');
    }
  };

  const handleExport = async () => {
    try {
      const res = await exportExcel();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `job_tracker_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Excel exported!');
    } catch (e) {
      toast.error('Export failed');
    }
  };

  const { summary } = data;

  return (
    <div className="slide-up">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Application Tracker</h2>
          <p>Track your job application progress</p>
        </div>
        <button className="btn btn-primary" onClick={handleExport} id="export-excel-btn">
          📥 Export Excel
        </button>
      </div>

      {/* Summary Stats */}
      <div className="stats-grid">
        {[
          { label: 'Total', value: summary.total, color: '#6366f1' },
          { label: 'Applied', value: summary.applied, color: '#3b82f6' },
          { label: 'Interview', value: summary.interview, color: '#f59e0b' },
          { label: 'Offers', value: summary.offer, color: '#10b981' },
          { label: 'Rejected', value: summary.rejected, color: '#ef4444' },
        ].map(s => (
          <div className="stat-card" key={s.label}>
            <div className="stat-value" style={{ background: s.color, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {s.value || 0}
            </div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Applications Table */}
      {loading ? (
        <div className="loading-page"><div className="spinner" /></div>
      ) : data.applications.length > 0 ? (
        <div className="table-wrapper">
          <table className="table">
            <thead>
              <tr>
                <th>Company</th><th>Role</th><th>ATS</th><th>Status</th>
                <th>Applied</th><th>Notes</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {data.applications.map(app => (
                <tr key={app.id}>
                  <td style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{app.company}</td>
                  <td>{app.role}</td>
                  <td><ATSGauge score={app.ats_score} size={40} /></td>
                  <td>
                    {editingId === app.id ? (
                      <select className="select" value={editForm.status}
                        onChange={e => setEditForm({ ...editForm, status: e.target.value })}
                        style={{ width: 140, padding: '4px 8px', fontSize: '0.8rem' }}>
                        {STATUS_OPTIONS.map(o => (
                          <option key={o.value} value={o.value}>{o.label}</option>
                        ))}
                      </select>
                    ) : (
                      <StatusBadge status={app.status} />
                    )}
                  </td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {formatDate(app.applied_date)}
                  </td>
                  <td style={{ maxWidth: 200, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    {editingId === app.id ? (
                      <input className="input" value={editForm.notes || ''}
                        onChange={e => setEditForm({ ...editForm, notes: e.target.value })}
                        style={{ padding: '4px 8px', fontSize: '0.8rem' }} />
                    ) : (
                      app.notes || '—'
                    )}
                  </td>
                  <td>
                    {editingId === app.id ? (
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button className="btn btn-primary btn-sm" onClick={saveEdit}>Save</button>
                        <button className="btn btn-secondary btn-sm" onClick={() => setEditingId(null)}>✕</button>
                      </div>
                    ) : (
                      <button className="btn btn-secondary btn-sm" onClick={() => handleEdit(app)}>Edit</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">
          <h3>No applications yet</h3>
          <p>Generate resumes for jobs to start tracking</p>
        </div>
      )}
    </div>
  );
}
