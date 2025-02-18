import React, { useState } from 'react';
import { Search } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { getCart, clearCart, checkout, getProducts, addToCart, updateQuantity, CartItem, Product } from '../api';
import { ProductGrid } from './pos/ProductGrid';
import { CategoryBar } from './pos/CategoryBar';
import { ShoppingCart } from './pos/ShoppingCart';
import { PaymentModal } from './pos/PaymentModal';

// Interface for cart items with product details
interface CartItemWithProduct extends CartItem {
  product?: Product;
}

export const POSSystem: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentInProgress, setPaymentInProgress] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  const queryClient = useQueryClient();
  
  // Get cart items with 5-second polling
  const { data: cartItems = [], isLoading: isLoadingCart } = useQuery('cart', getCart, {
    refetchInterval: 5000,
    refetchOnWindowFocus: true,
    retry: 3,
    keepPreviousData: true,
    onError: (error) => {
      console.error('Error loading cart:', error);
      if (error instanceof Error) {
        setConnectionError(error.message);
      }
    }
  });

  // Get products
  const { data: products = [], isLoading: isLoadingProducts } = useQuery('products', getProducts, {
    staleTime: 60000, // Consider data fresh for 1 minute
    cacheTime: 3600000, // Keep in cache for 1 hour
  });

  // Combine cart items with product details
  const cartItemsWithProducts: CartItemWithProduct[] = cartItems.map(item => {
    const product = products.find(p => p.id === item.product_id);
    return {
      ...item,
      product
    };
  });

  // Add to cart mutation
  const addToCartMutation = useMutation(addToCart, {
    onSuccess: () => {
      queryClient.invalidateQueries('cart');
    },
  });

  // Update quantity mutation
  const updateQuantityMutation = useMutation(
    ({ itemId, quantity }: { itemId: number; quantity: number }) => 
      updateQuantity({ itemId, quantity }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('cart');
      },
    }
  );

  // Clear cart mutation
  const clearMutation = useMutation(clearCart, {
    onSuccess: () => {
      queryClient.invalidateQueries('cart');
    },
  });

  // Checkout mutation
  const checkoutMutation = useMutation(checkout, {
    onMutate: () => {
      console.log('Starting checkout process');
      setPaymentInProgress(true);
    },
    onSuccess: () => {
      console.log('Checkout successful');
      queryClient.invalidateQueries('cart');
      setShowPaymentModal(false);
      setPaymentInProgress(false);
    },
    onError: (error) => {
      console.error('Payment error:', error);
      setPaymentInProgress(false);
      // Show error to user
      alert('Error processing payment. Please try again.');
    }
  });

  // Handle payment process
  const handlePayment = async () => {
    try {
      console.log('Payment button clicked');
      await checkoutMutation.mutateAsync();
    } catch (error) {
      console.error('Payment handler error:', error);
    }
  };

  // Filter products by category and search term
  const filteredProducts = products.filter(product => {
    const matchesCategory = activeCategory === 'all' || product.category === activeCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (connectionError) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center p-4">
          <h2 className="text-xl font-bold text-red-600 mb-2">Error de Conexión</h2>
          <p>{connectionError}</p>
          <button 
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg"
            onClick={() => window.location.reload()}
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  if (isLoadingCart || isLoadingProducts) {
    return <div className="flex h-screen items-center justify-center">Cargando...</div>;
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <div className="flex-1 p-4 overflow-auto">
        <div className="mb-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Buscar productos..."
              className="w-full p-3 border rounded-lg pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          </div>
        </div>

        <CategoryBar 
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />

        <ProductGrid 
          products={filteredProducts}
          onAddToCart={(id) => addToCartMutation.mutate(id)}
          isLoading={addToCartMutation.isLoading}
        />
      </div>

      <ShoppingCart 
        cartItems={cartItemsWithProducts}
        onUpdateQuantity={(itemId, quantity) => 
          updateQuantityMutation.mutate({ itemId, quantity })}
        onClearCart={() => clearMutation.mutate()}
        onCheckout={() => setShowPaymentModal(true)}
        isLoading={updateQuantityMutation.isLoading}
      />

      <PaymentModal 
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        onPayment={handlePayment}
        isProcessing={paymentInProgress}
      />
    </div>
  );
};

export default POSSystem; 