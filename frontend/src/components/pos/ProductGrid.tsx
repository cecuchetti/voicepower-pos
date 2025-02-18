import React from 'react';
import { Product } from '../../api';
import { DEFAULT_PRODUCT_IMAGE } from '../../config/images';
import { getProductImage } from '../../services/imageService';

interface ProductGridProps {
  products: Product[];
  onAddToCart: (productId: number) => void;
  isLoading: boolean;
}

export const ProductGrid: React.FC<ProductGridProps> = ({ products, onAddToCart, isLoading }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {products.map(product => (
        <button
          key={product.id}
          onClick={() => onAddToCart(product.id)}
          className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-all duration-200 hover:scale-105"
          disabled={isLoading}
        >
          <div className="aspect-square w-full mb-3 overflow-hidden rounded-lg">
            <img 
              src={product.image || getProductImage(product.id)} 
              alt={product.name} 
              className="w-full h-full object-contain p-2 hover:scale-110 transition-transform duration-200"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = DEFAULT_PRODUCT_IMAGE;
              }}
            />
          </div>
          <div className="text-left">
            <h3 className="font-medium text-gray-800 truncate">{product.name}</h3>
            <p className="text-blue-600 font-bold">${product.price.toFixed(2)}</p>
          </div>
        </button>
      ))}
    </div>
  );
}; 