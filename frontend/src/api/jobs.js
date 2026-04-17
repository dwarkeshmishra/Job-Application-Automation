import api from './index';

export const getJobs = (params = {}) => api.get('/jobs', { params });
export const getJob = (id) => api.get(`/jobs/${id}`);
export const addManualJob = (data) => api.post('/jobs/manual', data);
export const deleteJob = (id) => api.delete(`/jobs/${id}`);
