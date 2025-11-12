import axios from 'axios';

const API_BASE = 'http://localhost:8008';

// Token refresh interceptor
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE}/api/auth/refresh/`, {
          refresh: refreshToken,
        });
        const { access } = response.data;
        localStorage.setItem('accessToken', access);
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        return axios(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Collections CRUD
  getCollections: async () => {
    const response = await axios.get(`${API_BASE}/api/collections/`);
    return response.data;
  },

  getCollection: async (slug) => {
    const response = await axios.get(`${API_BASE}/api/collections/${slug}/`);
    return response.data;
  },

  createCollection: async (data) => {
    const response = await axios.post(`${API_BASE}/api/collections/`, data);
    return response.data;
  },

  updateCollection: async (slug, data) => {
    const response = await axios.put(`${API_BASE}/api/collections/${slug}/`, data);
    return response.data;
  },

  deleteCollection: async (slug) => {
    await axios.delete(`${API_BASE}/api/collections/${slug}/`);
  },

  // Endpoints CRUD
  getEndpoints: async (collectionSlug) => {
    const response = await axios.get(
      `${API_BASE}/api/endpoints/?collection=${collectionSlug}`
    );
    return response.data;
  },

  getEndpoint: async (id) => {
    const response = await axios.get(`${API_BASE}/api/endpoints/${id}/`);
    return response.data;
  },

  createEndpoint: async (data) => {
    const response = await axios.post(`${API_BASE}/api/endpoints/`, data);
    return response.data;
  },

  updateEndpoint: async (id, data) => {
    const response = await axios.put(`${API_BASE}/api/endpoints/${id}/`, data);
    return response.data;
  },

  deleteEndpoint: async (id) => {
    await axios.delete(`${API_BASE}/api/endpoints/${id}/`);
  },

  // Endpoint Responses CRUD
  getResponses: async (endpointId) => {
    const response = await axios.get(
      `${API_BASE}/api/responses/?endpoint=${endpointId}`
    );
    return response.data;
  },

  createResponse: async (data) => {
    const response = await axios.post(`${API_BASE}/api/responses/`, data);
    return response.data;
  },

  updateResponse: async (id, data) => {
    const response = await axios.put(`${API_BASE}/api/responses/${id}/`, data);
    return response.data;
  },

  deleteResponse: async (id) => {
    await axios.delete(`${API_BASE}/api/responses/${id}/`);
  },

  // Test endpoint
  testEndpoint: async (collectionSlug, path, method, body = null, headers = {}) => {
    const startTime = Date.now();
    try {
      const response = await axios({
        method: method.toLowerCase(),
        url: `${API_BASE}/${collectionSlug}/${path}`,
        data: body,
        headers: headers,
        validateStatus: () => true,
      });

      return {
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        data: response.data,
        time: Date.now() - startTime,
      };
    } catch (error) {
      return {
        status: 0,
        statusText: 'Network Error',
        headers: {},
        data: { error: error.message },
        time: Date.now() - startTime,
      };
    }
  },
};
