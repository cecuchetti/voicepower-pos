const TOTAL_IMAGES = 15;

export const getProductImage = (productId: number): string => {
  // Usar el ID del producto para obtener una imagen consistente
  const imageNumber = (productId % TOTAL_IMAGES) + 1;
  return `/images/products/${imageNumber}.png`;
};

export const getCartItemImage = (itemId: number, productId?: number): string => {
  if (productId) {
    return getProductImage(productId);
  }
  // Si no hay product_id, usar el itemId para mantener consistencia
  const imageNumber = (itemId % TOTAL_IMAGES) + 1;
  return `/images/products/${imageNumber}.png`;
};

export const getRandomImageForNewProduct = (): string => {
  const randomNumber = Math.floor(Math.random() * TOTAL_IMAGES) + 1;
  return `/images/products/${randomNumber}.png`;
}; 