import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  googleLogin: (data) => api.post('/auth/google', data),
  getMe: () => api.get('/auth/me'),
};

// User API
export const userAPI = {
  updateProfile: (data) => api.put('/user/profile', data),
  setupHome: (data) => api.post('/user/home-setup', data),
  getHomeStatus: () => api.get('/user/home-setup/status'),
};

// Sources API
export const sourcesAPI = {
  getAll: () => api.get('/sources'),
  getOne: (id) => api.get(`/sources/${id}`),
  create: (data) => api.post('/sources', data),
  update: (id, data) => api.put(`/sources/${id}`, data),
  delete: (id) => api.delete(`/sources/${id}`),
};

// Dashboard API
export const dashboardAPI = {
  getSummary: () => api.get('/dashboard/summary'),
  getLatest: (sourceId) => api.get(`/dashboard/latest/${sourceId}`),
  getHistory: (sourceId, hours = 24) => api.get(`/dashboard/history/${sourceId}?hours=${hours}`),
};

// Alerts API
export const alertsAPI = {
  getAll: (params = {}) => api.get('/alerts', { params }),
  acknowledge: (id) => api.put(`/alerts/${id}/acknowledge`),
  resolve: (id) => api.put(`/alerts/${id}/resolve`),
  getUnreadCount: () => api.get('/alerts/unread-count'),
};

// Analytics API
export const analyticsAPI = {
  getStats: (sourceId, days = 7) => api.get(`/analytics/stats/${sourceId}?days=${days}`),
  getTrends: (sourceId, days = 30) => api.get(`/analytics/trends/${sourceId}?days=${days}`),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
