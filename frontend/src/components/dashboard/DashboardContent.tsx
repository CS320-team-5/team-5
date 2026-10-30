import { Link } from 'react-router';
import { CartList } from './CartList';
import { FilterList } from './FilterList';
import { type CartDetails } from '../../types/cart';

export function DashboardContent({ cartList, filterList }: { cartList: CartDetails[], filterList: string[] }) {
  return (
    <>
      <header id="banner">
        <Link id="left-banner-part" to="/" aria-label="CoCart home">
          <img src="/hero_logo.svg" />
          <span id="logo-title">Co-Cart</span>
        </Link>
        <nav id="center-banner-part" aria-label="Dashboard navigation">
          <Link className="banner-button" to="/dashboard" aria-current="page">Browse Carts</Link>
          <Link className="banner-button" to="/create" aria-current="page">Start a Cart</Link>
          <Link className="banner-button" to="/messages">Messages</Link>
        </nav>
        <div id="right-banner-part">
          <button className="pill" type="button">
            <span className="initials">ML</span>
            <span className="name">Maya (Building 4)</span>
          </button>
        </div>
      </header>
      <br /><br />
      <main>
        <div>
          <div style={{display: "flex", alignItems: "center", gap: "4px"}}>
            <div id="circle"></div>
            <div style={{color: "#006947", fontFamily: "Plus Jakarta Sans", fontWeight: 700, fontSize: "11px"}}>
              LIVE ORDERING
            </div>
          </div>
          <h1 id="main-title">Active Community Carts</h1>
          <div id="summary-and-btn">
            <div id="summary-text">
              Find a nearby group order to hit free delivery minimums and split costs.
            </div>
            <button id="start-cart-button" type="button">+ Start a Cart</button>
          </div>
        </div>
        <br />
        <div id="filter-list">
          <FilterList filterList={filterList} />
        </div>
        <br />
        <div id="cart-list">
          <CartList cartList={cartList} />
        </div>
      </main>
    </>
  );
}
