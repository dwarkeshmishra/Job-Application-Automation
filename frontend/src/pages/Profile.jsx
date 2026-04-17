import { useState, useEffect } from 'react';
import { getProfile, updateProfile, uploadResume } from '../api/tracker';
import toast from 'react-hot-toast';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', location: '',
    linkedin_url: '', github_url: '', years_exp: '',
    target_roles: '', target_locations: '', skills: '',
  });
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  useEffect(() => {
    getProfile().then(res => {
      const p = res.data;
      if (p && !p.message) {
        setProfile(p);
        setForm({
          full_name: p.full_name || '',
          email: p.email || '',
          phone: p.phone || '',
          location: p.location || '',
          linkedin_url: p.linkedin_url || '',
          github_url: p.github_url || '',
          years_exp: p.years_exp || '',
          target_roles: (p.target_roles || []).join(', '),
          target_locations: (p.target_locations || []).join(', '),
          skills: (p.skills || []).join(', '),
        });
      }
    }).catch(() => {});
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    try {
      const res = await uploadResume(file);
      setUploadResult(res.data);
      toast.success(`Resume parsed! ${res.data.skills_detected?.length || 0} skills detected`);
      // Refresh profile
      const p = await getProfile();
      if (p.data && !p.data.message) setProfile(p.data);
    } catch (e) {
      toast.error('Upload failed');
    }
    setUploading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile({
        ...form,
        years_exp: form.years_exp ? parseFloat(form.years_exp) : null,
        target_roles: form.target_roles.split(',').map(s => s.trim()).filter(Boolean),
        target_locations: form.target_locations.split(',').map(s => s.trim()).filter(Boolean),
        skills: form.skills.split(',').map(s => s.trim()).filter(Boolean),
      });
      toast.success('Profile saved!');
    } catch (e) {
      toast.error('Save failed');
    }
    setSaving(false);
  };

  return (
    <div className="slide-up">
      <div className="page-header">
        <h2>Profile</h2>
        <p>Your master resume and career preferences</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* Upload Resume */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>Master Resume</h3>
          <div style={{
            border: '2px dashed var(--border-color)',
            borderRadius: 'var(--radius-lg)',
            padding: '40px 20px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'var(--transition)',
          }}
            onClick={() => document.getElementById('resume-upload').click()}
            onDragOver={e => e.preventDefault()}
          >
            <input type="file" id="resume-upload" accept=".pdf,.docx,.doc"
              onChange={handleUpload} style={{ display: 'none' }} />
            {uploading ? (
              <div className="spinner" style={{ margin: '0 auto' }} />
            ) : (
              <>
                <div style={{ fontSize: '2rem', marginBottom: 8 }}>📄</div>
                <div style={{ fontWeight: 500 }}>Upload Resume</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  PDF or DOCX • Click or drag
                </div>
              </>
            )}
          </div>

          {uploadResult && (
            <div className="fade-in" style={{ marginTop: 16 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--success)', marginBottom: 8 }}>
                ✅ Resume Parsed Successfully
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Experience: {uploadResult.years_experience} years
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 8 }}>
                {uploadResult.skills_detected?.map(s => (
                  <span key={s} className="skill-tag">{s}</span>
                ))}
              </div>
            </div>
          )}

          {profile?.skills && !uploadResult && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>
                DETECTED SKILLS
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {(typeof profile.skills === 'string' ? JSON.parse(profile.skills) : profile.skills)
                  .map(s => <span key={s} className="skill-tag">{s}</span>)}
              </div>
            </div>
          )}
        </div>

        {/* Profile Form */}
        <div className="card">
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>Personal Info</h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label>Full Name</label>
              <input className="input" value={form.full_name} id="profile-name"
                onChange={e => setForm({...form, full_name: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input className="input" value={form.email} id="profile-email"
                onChange={e => setForm({...form, email: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input className="input" value={form.phone} id="profile-phone"
                onChange={e => setForm({...form, phone: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Experience (years)</label>
              <input className="input" type="number" value={form.years_exp} id="profile-exp"
                onChange={e => setForm({...form, years_exp: e.target.value})} />
            </div>
          </div>

          <div className="form-group">
            <label>LinkedIn URL</label>
            <input className="input" value={form.linkedin_url} id="profile-linkedin"
              onChange={e => setForm({...form, linkedin_url: e.target.value})} />
          </div>
          <div className="form-group">
            <label>GitHub URL</label>
            <input className="input" value={form.github_url} id="profile-github"
              onChange={e => setForm({...form, github_url: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Target Roles (comma separated)</label>
            <input className="input" value={form.target_roles} id="profile-roles"
              placeholder="Software Engineer, Backend Developer"
              onChange={e => setForm({...form, target_roles: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Target Locations (comma separated)</label>
            <input className="input" value={form.target_locations} id="profile-locations"
              placeholder="Bangalore, Remote, Hyderabad"
              onChange={e => setForm({...form, target_locations: e.target.value})} />
          </div>
          <div className="form-group">
            <label>Skills (comma separated)</label>
            <input className="input" value={form.skills} id="profile-skills"
              placeholder="Python, React, SQL, Docker"
              onChange={e => setForm({...form, skills: e.target.value})} />
          </div>

          <button className="btn btn-primary" onClick={handleSave} disabled={saving} id="save-profile-btn"
            style={{ width: '100%', justifyContent: 'center' }}>
            {saving ? 'Saving...' : '💾 Save Profile'}
          </button>
        </div>
      </div>
    </div>
  );
}
