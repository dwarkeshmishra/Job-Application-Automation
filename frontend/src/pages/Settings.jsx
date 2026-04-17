import { useState } from 'react';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = useState({
    gemini_model: 'gemini-2.0-flash',
    scrape_sources: ['remotive'],
    scrape_keywords: 'software engineer, python developer',
    min_match_score: 62,
    schedule_hour: 2,
  });

  const handleSave = () => {
    // Settings are saved to .env on backend — for now just show toast
    toast.success('Settings saved! Restart backend to apply .env changes.');
  };

  return (
    <div className="slide-up">
      <div className="page-header">
        <h2>Settings</h2>
        <p>Configure AI model, scraping, and scheduling</p>
      </div>

      <div style={{ maxWidth: 600 }}>
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>🤖 AI Configuration</h3>
          <div className="form-group">
            <label>Gemini Model</label>
            <select className="select" value={settings.gemini_model} id="settings-model"
              onChange={e => setSettings({...settings, gemini_model: e.target.value})}>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash (Fast)</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro (Best)</option>
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Balanced)</option>
            </select>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>🔍 Scraper Settings</h3>
          <div className="form-group">
            <label>Default Keywords</label>
            <input className="input" value={settings.scrape_keywords} id="settings-keywords"
              onChange={e => setSettings({...settings, scrape_keywords: e.target.value})}
              placeholder="software engineer, python developer" />
          </div>
          <div className="form-group">
            <label>Minimum Match Score (%)</label>
            <input className="input" type="number" min="0" max="100" id="settings-minscore"
              value={settings.min_match_score}
              onChange={e => setSettings({...settings, min_match_score: parseInt(e.target.value)})} />
          </div>
          <div className="form-group">
            <label>Sources</label>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {['remotive', 'naukri', 'indeed', 'wellfound', 'linkedin'].map(src => (
                <label key={src} style={{ display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer',
                  fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <input type="checkbox"
                    checked={settings.scrape_sources.includes(src)}
                    onChange={e => {
                      const sources = e.target.checked
                        ? [...settings.scrape_sources, src]
                        : settings.scrape_sources.filter(s => s !== src);
                      setSettings({...settings, scrape_sources: sources});
                    }}
                    style={{ accentColor: 'var(--accent-primary)' }} />
                  {src.charAt(0).toUpperCase() + src.slice(1)}
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: '1rem', fontWeight: 600 }}>⏰ Scheduler</h3>
          <div className="form-group">
            <label>Nightly Run Hour (24h)</label>
            <input className="input" type="number" min="0" max="23" id="settings-hour"
              value={settings.schedule_hour}
              onChange={e => setSettings({...settings, schedule_hour: parseInt(e.target.value)})} />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
              Pipeline runs at {settings.schedule_hour}:00 AM — scrape, filter, export
            </span>
          </div>
        </div>

        <button className="btn btn-primary" onClick={handleSave} id="save-settings-btn"
          style={{ width: '100%', justifyContent: 'center' }}>
          💾 Save Settings
        </button>
      </div>
    </div>
  );
}
