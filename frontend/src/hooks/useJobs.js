import { useState, useEffect, useCallback } from 'react';
import { getJobs } from '../api/jobs';

export default function useJobs(initialParams = {}) {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getJobs(params);
      setJobs(res.data.jobs || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [JSON.stringify(params)]);

  useEffect(() => { fetchJobs(); }, [fetchJobs]);

  return { jobs, total, loading, error, refetch: fetchJobs, setParams };
}
