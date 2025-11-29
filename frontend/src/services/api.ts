import axios from 'axios';

const envBase = process.env.NEXT_PUBLIC_API_BASE_URL;
const PRIMARY_BASE = envBase && envBase.startsWith('http') ? envBase : 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: PRIMARY_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor for debugging
api.interceptors.request.use(
    (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
    },
    (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor for debugging
api.interceptors.response.use(
    (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
    },
    (error) => {
        console.error('API Response Error:', error.message, error.config?.url);
        if (error.response) {
            console.error('Error Status:', error.response.status);
            console.error('Error Data:', error.response.data);
        }
        return Promise.reject(error);
    }
);

export default api;
