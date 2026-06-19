import axios from 'axios';

// Base API URL config
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "https://logidispatch.onrender.com";

// Create a configured Axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor for centralized error logging/handling (optional)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
