// Configuration for API endpoints
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  NOTIFICATION_URL: process.env.REACT_APP_NOTIFICATION_URL || 'http://localhost:5002',
  ENDPOINTS: {
    auth: {
      login: '/api/auth/login',
      register: '/api/auth/register',
      google: '/api/auth/google',
    },
    sessions: '/api/sessions',
    bookings: {
      create: '/api/bookings',
      my: '/api/bookings/my',
      facilitator: '/api/facilitator/bookings',
    },
  },
};

// Helper function to build full URL
export const buildApiUrl = (endpoint: string) => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export default API_CONFIG;
