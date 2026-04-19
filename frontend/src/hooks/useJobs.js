import { useState, useEffect, useCallback } from 'react';
import { getJobs } from '../api/jobs';
import useStore from '../store/useStore';

export default function useJobs(initialParams = {}) {
  const { jobs: cachedJobs, totalJobs: cachedTotal, setJobs: setGlobalJobs } = useStore();
  const [jobs, setJobs] = useState(cachedJobs || []);
  const [total, setTotal] = useState(cachedTotal || 0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getJobs(params);
      const fetchedJobs = res.data.jobs || [];
      const fetchedTotal = res.data.total || 0;
      setJobs(fetchedJobs);
      setTotal(fetchedTotal);
      setGlobalJobs(fetchedJobs, fetchedTotal);  // Persist to Zustand → localStorage
    } catch (err) {
      setError(err.message);
      // On fetch failure, keep showing cached data if available
      if (cachedJobs?.length > 0 && jobs.length === 0) {
        setJobs(cachedJobs);
        setTotal(cachedTotal);
      }
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetchJobs(); }, [fetchJobs]);

  return { jobs, total, loading, error, refetch: fetchJobs, setParams };
}
