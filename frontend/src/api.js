import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';  // FastAPI 서버 주소

export const getUserPath = () => axios.get(`${BASE_URL}/user/path`);

export const setUserPath = (path) =>
  axios.post(`${BASE_URL}/user/path`, { base_path: path });

export const scanFiles = () => axios.post(`${BASE_URL}/scan`);

export const downloadNewZip = () =>
  axios.post(`${BASE_URL}/download-new-zip`, {}, {
    responseType: 'blob'
  });

export const downloadAll = () =>
  axios.post(`${BASE_URL}/download-all`, {}, {
    responseType: 'blob'
  });
