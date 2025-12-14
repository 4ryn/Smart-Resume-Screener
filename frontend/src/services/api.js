import axios from 'axios';

// ✅ Use your actual backend base URL + /api prefix
const API_BASE_URL = 'https://smart-resume-screener-9po9-7ln25xbmn-aryans-projects-77cc5ed8.vercel.app/';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ======================
// 🧠 JOBS API
// ======================
export const uploadJobCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/jobs/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const summarizeJobs = () => api.post('/jobs/summarize');
export const getJobs = () => api.get('/jobs');

// ======================
// 👤 CANDIDATES API
// ======================
export const uploadCVs = (files) => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  return api.post('/candidates/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getCandidates = () => api.get('/candidates');

// ======================
// 🔍 MATCHING API
// ======================
export const triggerMatching = () => api.post('/matching/match');
export const getMatchResults = () => api.get('/matching/results');
export const triggerShortlisting = () => api.post('/matching/shortlist');
export const getShortlist = () => api.get('/matching/shortlist');
export const triggerScheduling = () => api.post('/matching/schedule');

// ======================
// 📊 DASHBOARD API
// ======================
export const getDashboardStats = () => api.get('/dashboard/stats');

// ======================
// 🧹 UTILITY API
// ======================
export const clearAllData = () => api.post('/jobs/clear');

// ======================
// 🔗 Unified API Service
// ======================
export const apiService = {
  uploadJobDescriptions: (formData) =>
    api.post('/jobs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  uploadResumes: uploadCVs,
  summarizeJobs: summarizeJobs,
  triggerMatching: triggerMatching,
};

export default api;
