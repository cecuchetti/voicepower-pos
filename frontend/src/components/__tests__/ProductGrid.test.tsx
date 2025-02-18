import { render, screen, fireEvent } from '@testing-library/react';
import { ProductGrid } from '../ProductGrid';
import { mockProducts } from '../../mocks/data';

describe('ProductGrid', () => {
  it('renders products correctly', () => {
    render(<ProductGrid products={mockProducts} onAddToCart={jest.fn()} />);
    
    mockProducts.forEach(product => {
      expect(screen.getByText(product.name)).toBeInTheDocument();
      expect(screen.getByText(`$${product.price}`)).toBeInTheDocument();
    });
  });

  it('calls onAddToCart when product is clicked', () => {
    const onAddToCart = jest.fn();
    render(<ProductGrid products={mockProducts} onAddToCart={onAddToCart} />);
    
    const firstProduct = screen.getByText(mockProducts[0].name);
    fireEvent.click(firstProduct);
    
    expect(onAddToCart).toHaveBeenCalledWith(mockProducts[0].id);
  });
}); 