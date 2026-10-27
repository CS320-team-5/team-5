import { Link } from 'react-router';
import { CartList } from './CartList';
import { FilterList } from './FilterList';
import { type CartDetails } from '../../types/cart';

export function DashboardContent({ cartList, filterList }: { cartList: CartDetails[], filterList: string[] }) {
  return (
    <>
      <header id="banner">
        <Link id="left-banner-part" to="/" aria-label="CoCart home">
          <svg aria-hidden="true" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#00855B"/>
            <path d="M10.6042 23.9167C10.2292 23.9167 9.89583 23.8021 9.60416 23.573C9.3125 23.3438 9.11111 23.0487 9 22.6875L6.875 14.9792C6.80555 14.7153 6.85069 14.4723 7.01041 14.25C7.17013 14.0278 7.38888 13.9167 7.66666 13.9167H11.625L15.2917 8.45837C15.3611 8.34726 15.4583 8.25699 15.5833 8.18754C15.7083 8.1181 15.8403 8.08337 15.9792 8.08337C16.1181 8.08337 16.25 8.1181 16.375 8.18754C16.5 8.25699 16.5972 8.34726 16.6667 8.45837L20.3333 13.9167H24.3333C24.6111 13.9167 24.8299 14.0278 24.9896 14.25C25.1493 14.4723 25.1944 14.7153 25.125 14.9792L23 22.6875C22.8889 23.0487 22.6875 23.3438 22.3958 23.573C22.1042 23.8021 21.7708 23.9167 21.3958 23.9167H10.6042ZM10.5833 22.25H21.4167L23.25 15.5834H8.75L10.5833 22.25ZM16 20.5834C16.4583 20.5834 16.8507 20.4202 17.1771 20.0938C17.5035 19.7674 17.6667 19.375 17.6667 18.9167C17.6667 18.4584 17.5035 18.066 17.1771 17.7396C16.8507 17.4132 16.4583 17.25 16 17.25C15.5417 17.25 15.1493 17.4132 14.8229 17.7396C14.4965 18.066 14.3333 18.4584 14.3333 18.9167C14.3333 19.375 14.4965 19.7674 14.8229 20.0938C15.1493 20.4202 15.5417 20.5834 16 20.5834ZM13.6458 13.9167H18.3333L15.9792 10.4167L13.6458 13.9167Z" fill="#F5FFF6"/>
          </svg>
          <span id="logo-title">Co-Cart</span>
        </Link>
        <nav id="center-banner-part" aria-label="Dashboard navigation">
          <Link className="banner-button" to="/dashboard" aria-current="page">Browse Carts</Link>
          <button className="banner-button" type="button">Start a Cart</button>
          <button className="banner-button" type="button">Messages</button>
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
