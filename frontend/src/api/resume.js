import api from './index';

export const generateResume = (data) => api.post('/resume/generate', data);
export const getResumeScore = (jobId) => api.get(`/resume/score/${jobId}`);
export const scoreATS = (data) => api.post('/score/ats', data);
export const analyzeJD = (data) => api.post('/analyze/jd', data);
