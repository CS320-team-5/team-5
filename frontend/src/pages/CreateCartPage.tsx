import { Link } from "react-router";
import '../styles/createcart.css';

export function CreateCartPage() {
  return (
    <main id="create-cart-page">
      <div>
        <header id="banner">
          <Link id="left-banner-part" to="/" aria-label="CoCart home">
            <img src="../../public/hero_logo.svg" />
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
      </div>
      <br /><br />
      <div id="form-section">
        <div id="form-container">
          <div id="start-cart-header">
            <div id="start-cart-title">Start a Cart</div>
            <div className="general-text">Set up a shared order so neighbors can add to your cart.</div>
          </div>
          <div>
            <form action="" method="get" className="form-example">
              <div className="form-text">
                <label htmlFor="store">1. Store or Restaurant</label><br />
                <input 
                  type="text" name="store" id="store-input" 
                  placeholder="Or type a place (e.g. Insomnia Cookies)" required
                />
              </div>
              <div className="form-text">
                2. Order Minimum & Your Share
                <div id="price-container">
                  <div className="small-text">
                    <label htmlFor="threshold">Target Minimum</label>
                    <div className="general-container">
                      <span className="price-text">$</span>
                      <input 
                        type="number" name="threshold" 
                        id="threshold" readOnly placeholder="50"
                        className="price-input"
                      />
                    </div>
                  </div>
                  <div className="small-text">
                    <label htmlFor="start_amount">What you're spending</label>
                    <div className="general-container">
                      <span className="price-text">$</span>
                      <input 
                        type="number" name="start_amount" 
                        id="start_amount" placeholder="0"
                        className="price-input" 
                      />
                    </div>
                  </div>
                </div>
                <div id="notice-section">
                  <span><img src="../../piggy_bank.svg" /></span>
                  <div className="general-text">
                    Future cart participants need to add $20 to unlock free delivery
                  </div>
                </div>
              </div>
              <div className="form-example">
                <label htmlFor="name">Enter your name: </label>
                <input type="text" name="name" id="name" required />
              </div>
              <div className="form-example">
                <label htmlFor="email">Enter your email: </label>
                <input type="email" name="email" id="email" required />
              </div>
              <div className="form-example">
                <input type="submit" value="Subscribe!" />
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}