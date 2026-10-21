//import { CartList } from "../CartList";
import { test, expect } from "../../../node_modules/vitest";
import { CartDetails } from "../types";

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

const carts: CartDetails[] = arr.map((obj, i) => ({...obj, id: i }));

test("Cart Tests", () => {
  const x = 4*6;
  expect(x).toEqual(20);
});