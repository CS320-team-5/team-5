import { type CartDetails } from '../types/cart';

// Sample data until the dashboard is connected to the backend.
export const sampleCarts: CartDetails[] = [
  {
    id: 0,
    owner: "Alex M.",
    timeLeft: 15,
    store: "Local Grocery Mart",
    pickupLocation: "Building 4 Mailroom",
    openSpots: 2,
    threshold: 50,
    curr: 34
  },
  {
    id: 1,
    owner: "Sarah T.",
    timeLeft: 25,
    store: "Burrito Grill",
    pickupLocation: "Central Park West Benches",
    openSpots: 3,
    threshold: 40,
    curr: 22
  },
  {
    id: 2,
    owner: "Kevin C.",
    timeLeft: 8,
    store: "Campus Boba House",
    pickupLocation: "Building Lobby Rack",
    openSpots: 1,
    threshold: 30,
    curr: 28
  },
  {
    id: 3,
    owner: "Devin K.",
    timeLeft: 40,
    store: "Healthy Bowls Cafe",
    pickupLocation: "Pineapple Cafe Patio",
    openSpots: 2,
    threshold: 35,
    curr: 31
  }
];

export const sampleFilters = [
  "All Carts",
  "Apartments & Condos",
  "Groceries",
  "Takeout",
  "Coffee & Boba"
];
