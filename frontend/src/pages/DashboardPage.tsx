import { useState, useEffect } from 'react'
import { DashboardContent } from '../components/dashboard/DashboardContent';
import { sampleCarts, sampleFilters } from '../data/dashboard';
import { type CartDetails } from '../types/cart';
import '../styles/dashboard.css';

function DashboardPage() {
  const [results, setCartList] = useState<CartDetails[]>([]);
  const [filters, setFilterList] = useState<string[]>([]);
  useEffect (() => {
    // Simulate loading until the cart and filter APIs are connected.
    const cartsTimeout = window.setTimeout(
      () => setCartList(sampleCarts),
      2000
    );
    const filtersTimeout = window.setTimeout(
      () => setFilterList(sampleFilters),
      1500
    );
    return () => {
      window.clearTimeout(cartsTimeout);
      window.clearTimeout(filtersTimeout);
    };
  }, []); // indicate that this should load on mount

  return (
    <div className="dashboard-page">
      <DashboardContent cartList={results} filterList={filters} />
    </div>
  );
}

export default DashboardPage
