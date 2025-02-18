// Validate environment variables
const validateEnvVars = () => {
  if (!process.env.REACT_APP_API_URL) {
    console.warn('REACT_APP_API_URL not found in environment variables, using default');
  }
};

// Run validation
validateEnvVars();

export const apiConfig = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  endpoints: {
    cart: '/carts',
    products: '/products',
    checkout: (cartId: number) => `/carts/${cartId}/checkout`,
    cartItems: (cartId: number) => `/carts/${cartId}/items`,
  }
} as const;

// Type for the config object
export type ApiConfig = typeof apiConfig;

// Type for the endpoints
export type ApiEndpoints = typeof apiConfig.endpoints; 