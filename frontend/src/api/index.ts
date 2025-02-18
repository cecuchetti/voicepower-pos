import axios, { AxiosError } from 'axios';
import { apiConfig } from '../config/api';

export interface CartItem {
  id: number;
  product_id?: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  cart_id: number;
}

export interface Cart {
  id: number;
  status: string;
  created_at: string;
  updated_at: string;
  items: CartItem[];
}

export interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
  image: string;
}

interface ApiErrorResponse {
  message: string;
  status?: number;
}

const api = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
});

const isApiErrorResponse = (data: unknown): data is ApiErrorResponse => {
  return (
    typeof data === 'object' &&
    data !== null &&
    'message' in data &&
    typeof (data as ApiErrorResponse).message === 'string'
  );
};

const handleError = (error: AxiosError) => {
  if (error.response) {
    const errorData = error.response.data;
    console.error('Response error:', errorData);
    
    if (isApiErrorResponse(errorData)) {
      throw new Error(errorData.message);
    }
    throw new Error('Server response error');
  } else if (error.request) {
    console.error('Request error:', error.request);
    throw new Error('Could not connect to server');
  } else {
    console.error('Error:', error.message);
    throw new Error('Error processing request');
  }
};

export const getCart = async (): Promise<CartItem[]> => {
  try {
    const response = await api.get(apiConfig.endpoints.cart, {
      params: { status: 'active' }
    });
    const carts = response.data as Cart[];
    // Get the most recent active cart
    const activeCart = carts[carts.length - 1];
    return activeCart?.items || [];
  } catch (error) {
    if (axios.isAxiosError(error) && !error.response) {
      // Error de conexión
      console.error('Connection error:', error.message);
      throw new Error('No se pudo conectar al servidor. Por favor, verifica que el servidor esté corriendo.');
    }
    return handleError(error as AxiosError);
  }
};

export const addToCart = async (productId: number): Promise<void> => {
  try {
    // Get or create active cart
    const cartsResponse = await api.get(apiConfig.endpoints.cart, {
      params: { status: 'active' }
    });
    const carts = cartsResponse.data as Cart[];
    let activeCart = carts[carts.length - 1];

    if (!activeCart) {
      // Create new cart
      const newCartResponse = await api.post(apiConfig.endpoints.cart);
      activeCart = newCartResponse.data;
    }

    // Add item to cart
    await api.post(apiConfig.endpoints.cartItems(activeCart.id), {
      product_id: productId,
      quantity: 1
    });
  } catch (error) {
    handleError(error as AxiosError);
  }
};

interface UpdateQuantityParams {
  itemId: number;
  quantity: number;
}

export const updateQuantity = async ({ itemId, quantity }: UpdateQuantityParams): Promise<void> => {
  try {
    const cartsResponse = await api.get(apiConfig.endpoints.cart, {
      params: { status: 'active' }
    });
    const carts = cartsResponse.data as Cart[];
    const activeCart = carts[carts.length - 1];

    if (activeCart) {
      const item = activeCart.items.find(item => item.id === itemId);
      if (item) {
        await api.post(apiConfig.endpoints.cartItems(activeCart.id), {
          product_id: item.product_id,
          product_name: item.product_name,
          quantity: quantity,
          unit_price: item.unit_price
        });
      }
    }
  } catch (error) {
    handleError(error as AxiosError);
  }
};

export const clearCart = async (): Promise<void> => {
  try {
    const cartsResponse = await api.get(apiConfig.endpoints.cart, {
      params: { status: 'active' }
    });
    const carts = cartsResponse.data as Cart[];
    const activeCart = carts[carts.length - 1];

    if (activeCart) {
      await api.delete(apiConfig.endpoints.cartItems(activeCart.id));
    }
  } catch (error) {
    handleError(error as AxiosError);
  }
};

export const checkout = async (): Promise<void> => {
  try {
    const cartsResponse = await api.get(apiConfig.endpoints.cart, {
      params: { status: 'active' }
    });
    console.log('Active carts:', cartsResponse.data);

    const carts = cartsResponse.data as Cart[];
    const activeCart = carts[carts.length - 1];

    if (!activeCart) {
      throw new Error('No active cart found');
    }

    console.log('Processing checkout for cart:', activeCart.id);

    // Solo llamamos al endpoint de checkout, que se encargará de todo
    await api.post(apiConfig.endpoints.checkout(activeCart.id));
    
    // No necesitamos llamar a delete porque el checkout ya se encarga de eso
    console.log('Checkout completed successfully');

  } catch (error) {
    console.error('Checkout error details:', error);
    handleError(error as AxiosError);
  }
};

export const getProducts = async (): Promise<Product[]> => {
  try {
    const response = await api.get(apiConfig.endpoints.products);
    return response.data;
  } catch (error) {
    return handleError(error as AxiosError);
  }
}; 