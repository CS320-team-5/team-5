import { useState, useEffect } from 'react'
import { Template } from "./Template";
import { type CartDetails } from './types';
import './dashboard.css';

const arr = [
  {
    owner: "Alex M.",
    timeLeft: 15,
    store: "Local Grocery Mart",
    pickupLocation: "Building 4 Mailroom",
    openSpots: 2,
    threshold: 50,
    curr: 34
  },
  {
    owner: "Sarah T.",
    timeLeft: 25,
    store: "Burrito Grill",
    pickupLocation: "Central Park West Benches",
    openSpots: 3,
    threshold: 40,
    curr: 22
  },
  {
    owner: "Kevin C.",
    timeLeft: 8,
    store: "Campus Boba House",
    pickupLocation: "Building Lobby Rack",
    openSpots: 1,
    threshold: 30,
    curr: 28
  },
  {
    owner: "Devin K.",
    timeLeft: 40,
    store: "Healthy Bowls Cafe",
    pickupLocation: "Pineapple Cafe Patio",
    openSpots: 2,
    threshold: 35,
    curr: 31
  }
];

const filterArray = [
  "All Carts",
  "Apartments & Condos",
  "Groceries",
  "Takeout",
  "Coffee & Boba"
];

const cartArray: CartDetails[] = arr.map((obj, i) => ({...obj, id: i }));

function Dashboard() {
  const [results, setCartList] = useState<CartDetails[]>([]);
  const [filters, setFilterList] = useState<string[]>([]);
  useEffect (() => {
    // Simulate loading until the cart and filter APIs are connected.
    const cartsTimeout = window.setTimeout(
      () => setCartList(cartArray),
      2000
    );
    const filtersTimeout = window.setTimeout(
      () => setFilterList(filterArray),
      1500
    );
    return () => {
      window.clearTimeout(cartsTimeout);
      window.clearTimeout(filtersTimeout);
    };
  }, []); // indicate that this should load on mount

  return (
    <div className="dashboard-page">
      <Template cartList={results} filterList={filters} />
    </div>
  );
}

export default Dashboard
