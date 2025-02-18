import axios from 'axios';
import { AppError, errorCodes } from '../utils/error-handling';

export const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Request made but server responded with error
      throw new AppError(
        error.response.data.message || 'Server error',
        error.response.data.code || errorCodes.SERVER_ERROR,
        error.response.status
      );
    } else if (error.request) {
      // Request made but no response received
      throw new AppError(
        'No se pudo conectar con el servidor',
        errorCodes.NETWORK_ERROR,
        0
      );
    } else {
      // Error setting up request
      throw new AppError(
        'Error en la configuración de la petición',
        errorCodes.CLIENT_ERROR,
        0
      );
    }
  }
); 