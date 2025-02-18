import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { StateCreator } from 'zustand';

interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
}

interface POSStore {
  // UI State
  paymentInProgress: boolean;
  connectionError: string | null;
  activeCategory: string;
  searchTerm: string;
  
  // Cart State
  cartItems: CartItem[];
  
  // Actions
  setPaymentInProgress: (status: boolean) => void;
  setConnectionError: (error: string | null) => void;
  setActiveCategory: (category: string) => void;
  setSearchTerm: (term: string) => void;
  addToCart: (item: CartItem) => void;
  removeFromCart: (itemId: number) => void;
  clearCart: () => void;
}

type POSStoreMiddleware = [
  ["zustand/devtools", never],
  ["zustand/persist", unknown]
];

const createPOSStore: StateCreator<
  POSStore,
  POSStoreMiddleware,
  [],
  POSStore
> = (set) => ({
  // Initial state
  paymentInProgress: false,
  connectionError: null,
  activeCategory: 'all',
  searchTerm: '',
  cartItems: [],

  // Actions
  setPaymentInProgress: (status: boolean) => 
    set({ paymentInProgress: status }),
  setConnectionError: (error: string | null) => 
    set({ connectionError: error }),
  setActiveCategory: (category: string) => 
    set({ activeCategory: category }),
  setSearchTerm: (term: string) => 
    set({ searchTerm: term }),
  addToCart: (item: CartItem) => 
    set((state) => ({ 
      cartItems: [...state.cartItems, item] 
    })),
  removeFromCart: (itemId: number) => 
    set((state) => ({
      cartItems: state.cartItems.filter(item => item.id !== itemId)
    })),
  clearCart: () => set({ cartItems: [] })
});

export const usePOSStore = create<POSStore>()(
  devtools(
    persist(
      createPOSStore,
      {
        name: 'pos-storage',
        partialize: (state: POSStore) => ({ cartItems: state.cartItems })
      }
    )
  )
); 