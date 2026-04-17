import { useState } from 'react';
import { scoreATS } from '../api/resume';

export default function useATSScore() {
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calculateScore = async (data) => {
    setLoading(true);
    setError(null);
    try {
      const res = await scoreATS(data);
      setScore(res.data);
      return res.data;
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { score, loading, error, calculateScore };
}
