import { 
  Carrot, 
  Apple, 
  Beef, 
  Milk, 
  Beer, 
  ShoppingBag,
  LucideIcon 
} from 'lucide-react';

export interface Category {
  id: string;
  name: string;
  icon: LucideIcon;
}

export const categories: Category[] = [
  { id: 'all', name: 'Todos', icon: ShoppingBag },
  { id: 'vegetables', name: 'Verduras', icon: Carrot },
  { id: 'fruits', name: 'Frutas', icon: Apple },
  { id: 'meat', name: 'Carnes', icon: Beef },
  { id: 'dairy', name: 'Lácteos', icon: Milk },
  { id: 'beverages', name: 'Bebidas', icon: Beer },
]; 