import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import POSSystem from './components/POSSystem';
import './index.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <POSSystem />
    </QueryClientProvider>
  );
}

export default App;
