import { Link } from "react-router";
import "../styles/theme.css";
import { ShoppingBasket } from "lucide-react";

/**
 * Banner appearing on the Active Carts, Cart Creation, Messaging, and Settings pages
 */
function Banner() {
  return (
    <header id="banner">
      <Link id="left-banner-part" to="/" aria-label="Co-Cart home">
        <ShoppingBasket color="var(--primary-green)"/>
        <span id="logo-title">Co-Cart</span>
      </Link>
      <nav id="center-banner-part" aria-label="Dashboard navigation">
        <Link className="banner-button" to="/dashboard" aria-current="page">Browse Carts</Link>
        <Link className="banner-button" to="/create" aria-current="page">Start a Cart</Link>
        <Link className="banner-button" to="/messages" aria-current="page">Messages</Link>
      </nav>
      <Link 
        id="right-banner-part" to="/settings" 
        aria-current="page" aria-label="Account Settings" 
        className="account-pill" type="button"
      >
          <span className="account-initials">ML</span>
          <span className="name">Maya (Building 4)</span>
      </Link>
    </header>
  );
}

export default Banner