import React from 'react';
import { CreditCard, Banknote } from 'lucide-react';

// Payment modal component with card and cash options
interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPayment: () => void;
  isProcessing: boolean;
}

export const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  onPayment,
  isProcessing
}) => {
  // Don't render if modal is not open
  if (!isOpen) return null;

  return (
    // Modal overlay with semi-transparent background
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      {/* Modal content container */}
      <div className="bg-white p-6 rounded-lg w-96">
        <h2 className="text-xl font-bold mb-4">Método de Pago</h2>
        <div className="space-y-3">
          <button 
            className="w-full p-4 bg-blue-500 text-white rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
            onClick={onPayment}
            disabled={isProcessing}
          >
            <CreditCard size={20} />
            <span>
              {isProcessing ? 'Procesando...' : 'Pagar con tarjeta'}
            </span>
          </button>
          <button 
            className="w-full p-4 bg-green-500 text-white rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
            onClick={onPayment}
            disabled={isProcessing}
          >
            <Banknote size={20} />
            <span>
              {isProcessing ? 'Procesando...' : 'Pagar en efectivo'}
            </span>
          </button>
        </div>
        <button 
          className="w-full p-2 mt-4 border border-gray-300 rounded-lg disabled:opacity-50"
          onClick={onClose}
          disabled={isProcessing}
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}; 