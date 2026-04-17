import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/',            icon: '📊', label: 'Dashboard' },
  { to: '/jobs',        icon: '💼', label: 'Jobs' },
  { to: '/tracker',     icon: '📋', label: 'Tracker' },
  { to: '/resume',      icon: '📄', label: 'Resume Studio' },
  { to: '/profile',     icon: '👤', label: 'Profile' },
  { to: '/skill-gap',   icon: '📈', label: 'Skill Gap' },
  { to: '/settings',    icon: '⚙️', label: 'Settings' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>Job Copilot</h1>
        <span>AI-Powered Career Assistant</span>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={to === '/'}
          >
            <span className="nav-icon">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-color)' }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
          Powered by Gemini AI
        </div>
      </div>
    </aside>
  );
}
