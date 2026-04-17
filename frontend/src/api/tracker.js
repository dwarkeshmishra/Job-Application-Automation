import api from './index';

export const getTracker = (params = {}) => api.get('/tracker', { params });
export const updateApplication = (id, data) => api.patch(`/tracker/${id}`, data);
export const deleteApplication = (id) => api.delete(`/tracker/${id}`);
export const exportExcel = () => api.get('/export/excel', { responseType: 'blob' });

export const getProfile = () => api.get('/profile');
export const updateProfile = (data) => api.put('/profile', data);
export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/profile/upload-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const runScrape = (data) => api.post('/scrape/run', data);
export const getScrapeStatus = (taskId) => api.get(`/scrape/status/${taskId}`);
