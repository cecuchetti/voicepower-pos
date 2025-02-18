import React from 'react';
import { categories } from '../../config/categories';

interface CategoryBarProps {
  activeCategory: string;
  onCategoryChange: (categoryId: string) => void;
}

export const CategoryBar: React.FC<CategoryBarProps> = ({ activeCategory, onCategoryChange }) => {
  return (
    <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
      {categories.map(category => {
        const Icon = category.icon;
        return (
          <button
            key={category.id}
            onClick={() => onCategoryChange(category.id)}
            className={`
              px-4 py-2 rounded-lg whitespace-nowrap 
              flex items-center gap-2 
              transition-all duration-200 ease-in-out
              ${activeCategory === category.id
                ? 'bg-blue-500 text-white shadow-md scale-105'
                : 'bg-white text-gray-600 hover:bg-gray-50 hover:scale-105 hover:shadow-sm'
              }
            `}
          >
            <Icon size={20} className="transition-transform group-hover:rotate-3" />
            <span>{category.name}</span>
          </button>
        );
      })}
    </div>
  );
}; 