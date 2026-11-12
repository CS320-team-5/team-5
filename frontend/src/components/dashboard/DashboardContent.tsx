import { Link } from 'react-router';
import { CartList } from './CartList';
import { FilterList } from './FilterList';
import Banner from '../Banner';
import { type CartDetails } from '../../types/cart';
import "../../styles/theme.css";
import "../../styles/dashboard.css";
import { ShoppingCartPlus } from "lucide-react";

export function DashboardContent({ cartList, filterList }: { cartList: CartDetails[], filterList: string[], }) {
  return (
    <div className="theme dashboard-page">
      <Banner />
      <br /><br />
      <main>
        <div>
          <div style={{display: "flex", alignItems: "center", gap: "4px"}}>
            <div id="circle"></div>
            <div style={{color: "#006947", fontFamily: "Plus Jakarta Sans", fontWeight: "bold", fontSize: "11px"}}>
              LIVE ORDERING
            </div>
          </div>
          <h1 id="page-title">Active Community Carts</h1>
          <div id="summary-and-btn">
            <div className="info-text">
              Find a nearby group order to hit free delivery minimums and split costs.
            </div>
            <Link id="start-cart-button" className="info-text" to="/create" aria-current="page">
              <ShoppingCartPlus size={16} /> Start a Cart
            </Link>
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
    </div>
  );
}
