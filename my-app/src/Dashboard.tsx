import '../../dashboard.css'
import { useState, useEffect } from 'react'

const url = "my-url";

/*
The url endpoint is expected to return an array of JSON objects
*/


/*
Here is a simple example of the carts JSON
const carts = [
  {
    owner: "Alex M.",
    time_left: 15,
    store: "Local Grocery Mart",
    pickup_location: "Building 4 Mailroom",
    open_spots: 2,
    threshold: 50,
    curr: 34,
  }
];
*/

function Dashboard() {
  const [results, setCartList] = useState([]);
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

    fetchData();
    return () => { controller.abort(); };
  }, []); // indicate that this should load on mount



}

export default Dashboard