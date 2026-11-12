import { Link } from "react-router";
import theme from "../styles/theme.module.css";

function Banner() {
  return (
    <header id="banner">
      <Link id="left-banner-part" to="/" aria-label="CoCart home">
        <img src="/hero_logo.svg" />
        <span id="logo-title">Co-Cart</span>
      </Link>
      <nav id="center-banner-part" aria-label="Dashboard navigation">
        <Link className="banner-button" to="/dashboard" aria-current="page">Browse Carts</Link>
        <Link className="banner-button" to="/create" aria-current="page">Start a Cart</Link>
        <Link className="banner-button" to="/messages" aria-current="page">Messages</Link>
      </nav>
      <div id="right-banner-part">
        <button className="account-pill" type="button">
          <span className="account-initials">ML</span>
          <span className="name">Maya (Building 4)</span>
        </button>
      </div>
    </header>
  );
}