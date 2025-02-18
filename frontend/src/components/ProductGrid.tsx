import React, { useRef } from 'react';
import { memo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { Product } from '../api';

interface ProductGridProps {
  products: Product[];
  onAddToCart: (id: number) => void;
  isLoading: boolean;
}

interface ProductCardProps {
  product: Product;
  style: React.CSSProperties;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, style }) => (
  <div style={style} className="p-4">
    <h3>{product.name}</h3>
    <p>${product.price}</p>
  </div>
);

export const ProductGrid = memo<ProductGridProps>(({ products, onAddToCart, isLoading }) => {
  const parentRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: products.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
    overscan: 5
  });

  return (
    <div ref={parentRef} className="h-screen overflow-auto">
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {rowVirtualizer.getVirtualItems().map((virtualRow) => (
          <ProductCard
            key={virtualRow.key}
            product={products[virtualRow.index]}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          />
        ))}
      </div>
    </div>
  );
});

ProductGrid.displayName = 'ProductGrid'; 