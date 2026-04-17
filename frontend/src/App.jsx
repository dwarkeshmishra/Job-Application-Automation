import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import JobsList from './pages/JobsList';
import ApplicationTracker from './pages/ApplicationTracker';
import ResumeStudio from './pages/ResumeStudio';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import SkillGap from './pages/SkillGap';

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1a1f35',
            color: '#f1f5f9',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            borderRadius: '10px',
            fontSize: '0.85rem',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#1a1f35' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#1a1f35' } },
        }}
      />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<JobsList />} />
          <Route path="/tracker" element={<ApplicationTracker />} />
          <Route path="/resume" element={<ResumeStudio />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/skill-gap" element={<SkillGap />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
