import React from 'react';
import { Plus, Minus, Trash2, Receipt } from 'lucide-react';
import { CartItem } from '../../api';
import { DEFAULT_PRODUCT_IMAGE } from '../../config/images';
import { getCartItemImage } from '../../services/imageService';

interface ShoppingCartProps {
  cartItems: CartItem[];
  onUpdateQuantity: (itemId: number, quantity: number) => void;
  onClearCart: () => void;
  onCheckout: () => void;
  isLoading: boolean;
}

export const ShoppingCart: React.FC<ShoppingCartProps> = ({
  cartItems,
  onUpdateQuantity,
  onClearCart,
  onCheckout,
  isLoading
}) => {
  const calculateTotal = () => {
    return cartItems.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
  };

  const calculateTax = () => calculateTotal() * 0.16;
  const calculateGrandTotal = () => calculateTotal() + calculateTax();

  return (
    <div className="w-96 bg-white shadow-lg p-4 flex flex-col">
      <h2 className="text-xl font-bold mb-4">Shopping Cart</h2>
      
      <div className="flex-1 overflow-auto">
        {cartItems.map(item => (
          <div key={item.id} className="flex items-center gap-2 mb-4 p-2 border-b">
            <img 
              src={getCartItemImage(item.id, item.product_id)} 
              alt={item.product_name} 
              className="w-16 h-16 object-cover rounded" 
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = DEFAULT_PRODUCT_IMAGE;
              }}
            />
            <div className="flex-1">
              <h3 className="font-medium">{item.product_name}</h3>
              <p className="text-blue-600">${item.unit_price.toFixed(2)}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                className="p-1 hover:bg-gray-100 rounded"
                disabled={isLoading}
              >
                <Minus size={16} />
              </button>
              <span className="w-8 text-center">{item.quantity}</span>
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                className="p-1 hover:bg-gray-100 rounded"
                disabled={isLoading}
              >
                <Plus size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-4 mt-4">
        <div className="flex justify-between mb-2">
          <span>Subtotal:</span>
          <span>${calculateTotal().toFixed(2)}</span>
        </div>
        <div className="flex justify-between mb-2">
          <span>IVA (16%):</span>
          <span>${calculateTax().toFixed(2)}</span>
        </div>
        <div className="flex justify-between mb-4 text-lg font-bold">
          <span>Total:</span>
          <span>${calculateGrandTotal().toFixed(2)}</span>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button 
            onClick={onClearCart}
            className="p-2 bg-red-500 text-white rounded-lg flex items-center justify-center gap-2"
            disabled={isLoading || cartItems.length === 0}
          >
            <Trash2 size={20} />
            <span>Limpiar</span>
          </button>
          <button 
            onClick={onCheckout}
            className="p-2 bg-green-500 text-white rounded-lg flex items-center justify-center gap-2"
            disabled={isLoading || cartItems.length === 0}
          >
            <Receipt size={20} />
            <span>Pagar</span>
          </button>
        </div>
      </div>
    </div>
  );
}; 