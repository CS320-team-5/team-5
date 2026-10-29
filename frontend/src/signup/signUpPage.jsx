import "./signup.css";
import { ArrowRight, MapPin } from "lucide-react";

export default function SignUpPage() {
  return (
    <main className="signup-page">

      <header className="signup-header">
        <h1>
          Co-Cart<span className="brand-dot">.</span>
        </h1>

        <button className="login-button">
          Log In
        </button>
      </header>

      <div className="signup-content">
        <div className="signup-card">

          <h2 className="signup-title">
            Create Account
          </h2>

          <p className="signup-subtitle">
            Combine online orders with local people to reduce/eliminate delivery fees.
          </p>

          <div className="social-buttons">
            <button>Google</button>
            <button>Apple</button>
          </div>

          <div className="divider">
            <div className="divider-line"></div>

            <span className="divider-text">
              OR EMAIL
            </span>

            <div className="divider-line"></div>
          </div>

          <div className="form-group">
            <label>Full Name</label>

            <input
              type="text"
              placeholder="e.g. Maya Lin"
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>

            <input
              type="email"
              placeholder="you@example.com"
            />
          </div>

          <div className="form-group">
            <label>Building Address / Zip</label>

            <div className="address-wrapper">
              <input
                type="text"
                placeholder="e.g. 75 Montague St or 11201"
              />

              <MapPin
                size={18}
                className="map-icon"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              placeholder="8+ characters"
            />
          </div>

          <label className="checkbox-row">
            <input type="checkbox" />

            <span>
              Alert me when neighbors start an order
            </span>
          </label>

          <button className="create-account-button">
            Create Account

            <ArrowRight size={20} />
          </button>

          <p className="login-link">
            Already have an account?
            {" "}
            <span>Log in</span>
          </p>

        </div>
      </div>

      <footer className="signup-footer">
        Co-Cart
      </footer>

    </main>
  );
}