import { useState } from 'react';
import useJobs from '../hooks/useJobs';
import JobCard from '../components/JobCard';
import FilterBar from '../components/FilterBar';
import StatusBadge from '../components/StatusBadge';
import { addManualJob } from '../api/jobs';
import { runScrape, getScrapeStatus } from '../api/tracker';
import toast from 'react-hot-toast';

export default function JobsList() {
  const { jobs, total, loading, refetch, setParams } = useJobs({ limit: 50 });
  const [showAdd, setShowAdd] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [addForm, setAddForm] = useState({ title: '', company: '', job_url: '', jd_text: '' });

  const handleFilter = (filters) => setParams({ ...filters, limit: 50 });

  const handleScrape = async () => {
    setScraping(true);
    try {
      const res = await runScrape({
        sources: ['remotive'],
        keywords: ['software engineer', 'python developer'],
        max_per_source: 20,
      });
      const taskId = res.data.task_id;
      toast.success('Scraping started!');

      // Poll status
      const poll = setInterval(async () => {
        const status = await getScrapeStatus(taskId);
        if (status.data.status === 'completed' || status.data.status === 'failed') {
          clearInterval(poll);
          setScraping(false);
          toast.success(`Scrape done: ${status.data.jobs_added} jobs added`);
          refetch();
        }
      }, 3000);
    } catch (e) {
      setScraping(false);
      toast.error('Scrape failed');
    }
  };

  const handleAddJob = async () => {
    if (!addForm.title || !addForm.company) {
      toast.error('Title and company are required');
      return;
    }
    try {
      const res = await addManualJob(addForm);
      toast.success(`Job added! Match: ${Math.round((res.data.match_score || 0) * 100)}%`);
      setShowAdd(false);
      setAddForm({ title: '', company: '', job_url: '', jd_text: '' });
      refetch();
    } catch (e) {
      toast.error('Failed to add job');
    }
  };

  return (
    <div className="slide-up">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Jobs</h2>
          <p>{total} jobs found</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary" onClick={() => setShowAdd(!showAdd)} id="add-job-btn">
            ➕ Add Job
          </button>
          <button className="btn btn-primary" onClick={handleScrape} disabled={scraping} id="scrape-btn">
            {scraping ? '⏳ Scraping...' : '🔍 Scrape Jobs'}
          </button>
        </div>
      </div>

      <FilterBar onFilter={handleFilter} />

      {/* Add Job Form */}
      {showAdd && (
        <div className="card fade-in" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 16, fontSize: '1rem' }}>Add Job Manually</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label>Job Title *</label>
              <input className="input" value={addForm.title} id="add-job-title"
                onChange={e => setAddForm({ ...addForm, title: e.target.value })} />
            </div>
            <div className="form-group">
              <label>Company *</label>
              <input className="input" value={addForm.company} id="add-job-company"
                onChange={e => setAddForm({ ...addForm, company: e.target.value })} />
            </div>
          </div>
          <div className="form-group">
            <label>Job URL</label>
            <input className="input" value={addForm.job_url} id="add-job-url"
              onChange={e => setAddForm({ ...addForm, job_url: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Job Description</label>
            <textarea className="textarea" value={addForm.jd_text} id="add-job-jd"
              onChange={e => setAddForm({ ...addForm, jd_text: e.target.value })}
              placeholder="Paste the full job description here..." />
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-primary" onClick={handleAddJob} id="submit-job-btn">Save Job</button>
            <button className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Job List */}
      {loading ? (
        <div className="loading-page"><div className="spinner" /></div>
      ) : jobs.length > 0 ? (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 16 }}>
          {jobs.map(job => (
            <JobCard key={job.id} job={job} onClick={(j) => window.open(j.job_url, '_blank')} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <h3>No jobs found</h3>
          <p>Try scraping jobs or adding one manually</p>
        </div>
      )}
    </div>
  );
}
