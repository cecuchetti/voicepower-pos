import random

class ImageService:
    TOTAL_IMAGES = 15
    
    @staticmethod
    def get_random_product_image() -> str:
        image_number = random.randint(1, ImageService.TOTAL_IMAGES)
        return f"/images/products/{image_number}.png"
    
    @staticmethod
    def get_image_for_product(product_id: int) -> str:
        # Usar el ID del producto para obtener una imagen consistente
        image_number = (product_id % ImageService.TOTAL_IMAGES) + 1
        return f"/images/products/{image_number}.png" 