import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Jobs
export const uploadJobCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/jobs/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const summarizeJobs = () => api.post('/jobs/summarize');
export const getJobs = () => api.get('/jobs');

// Candidates
export const uploadCVs = (files) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  return api.post('/candidates/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const getCandidates = () => api.get('/candidates');

// Matching
export const triggerMatching = () => api.post('/matching/match');
export const getMatchResults = () => api.get('/matching/results');
export const triggerShortlisting = () => api.post('/matching/shortlist');
export const getShortlist = () => api.get('/matching/shortlist');
export const triggerScheduling = () => api.post('/matching/schedule');

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats');

// Utility
export const clearAllData = () => api.post('/jobs/clear');

// API Service object for unified upload flow
export const apiService = {
  uploadJobDescriptions: (formData) => {
    // FormData is already prepared, just send it
    return api.post('/jobs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  uploadResumes: uploadCVs,
  summarizeJobs: summarizeJobs,
  triggerMatching: triggerMatching
};

export default api;