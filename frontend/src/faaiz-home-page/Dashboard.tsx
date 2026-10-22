import { useState, useEffect } from 'react'
import { Template } from "./Template";
import { CartDetails } from './types';

const url = "my-url";

/*
The url endpoint is expected to return an array of JSON objects
*/


/*
Here is a simple example of the carts JSON
const carts = [
  {
    owner: "Alex M.",
    timeLeft: 15,
    store: "Local Grocery Mart",
    pickupLocation: "Building 4 Mailroom",
    openSpots: 2,
    threshold: 50,
    curr: 34,
  }
];
*/

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
  const [results, setCartList] = useState(Array<CartDetails>());
  const [filters, setFilterList] = useState(Array<string>());
  useEffect (() => {
    const controller = new AbortController();
    const { signal } = controller;
    function fetchData() {
      fetch(url, { signal })
        .then(res => res.ok ? res.json() : Promise.reject(new Error(res.statusText)))
        .then(carts =>
          // we create an abort controller to handle quitting fetch
          // here, we modify the results object to store the acquired carts
          setCartList(carts)
        )
        .catch(e => {
          if (e.name === 'AbortError') {
            console.log("page switched from dashboard, quitting fetch");
          } else {
            console.log("fetch request failed");
          }
        });
    }
    setTimeout(
      () => setCartList(cartArray),
      2000
    );
    setTimeout(
      () => setFilterList(filterArray),
      1500
    );
    return () => { controller.abort(); };
  }, []); // indicate that this should load on mount
  console.log(results);

  return <><Template cartList={results} filterList={filters}></Template></>;
}

export default Dashboard