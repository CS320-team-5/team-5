import { useState, useEffect } from 'react'
import { DashboardContent } from '../components/dashboard/DashboardContent';
import { sampleCarts, sampleFilters } from '../data/dashboard';
import { type CartDetails } from '../types/cart';
import { getActiveCart, toCard } from '../services/cart';

function DashboardPage() {
  const [results, setCartList] = useState<CartDetails[]>([]);
  const [filters, setFilterList] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  useEffect (() => {
    const controller = new AbortController();
    async function loadCarts(){
      try{
        const carts = await getActiveCart(controller.signal);

        if(!controller.signal.aborted){
          setCartList(carts.map(toCard))
        }
      }
      catch(error:unknown){
        if(!controller.signal.aborted){
          setLoadError(
            error instanceof Error ? error.message : "Could not load carts.",
          );
        }
      } finally {
        if(!controller.signal.aborted){
          setIsLoading(false);
      }
    }
  }

  void loadCarts();
  return () => controller.abort();

  }, []); 

  return (
    <>
      {isLoading && <p role="status">Loading carts…</p>}
      {loadError && <p role="alert">{loadError}</p>}
      {!isLoading && !loadError && results.length === 0 && (
        <p role="status">No active carts right now.</p>
      )}
      <DashboardContent cartList={results} filterList={sampleFilters} />
    </>
  );
}

export default DashboardPage
