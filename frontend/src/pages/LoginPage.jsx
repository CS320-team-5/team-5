import '../styles/signup.css';
import { ArrowRight, MapPin } from "lucide-react";

export default function LoginPage() {
  return (
    <main className="signup-page">

      <header className="signup-header">
        <h1>
          Co-Cart<span className="brand-dot">.</span>
        </h1>

        <button className="login-button">
          Sign Up
        </button>
      </header>

      <div className="signup-content">
        <div className="signup-card">

          <h2 className="signup-title">
            Log In
          </h2>

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
            <label>Email Address</label>

            <input
              type="email"
              placeholder="you@example.com"
            />
          </div>

          <div className="form-group">
            <label>Password</label>

            <input
              type="password"
              placeholder="8+ characters"
            />
          </div>


          <button className="create-account-button">
            Log In

            <ArrowRight size={20} />
          </button>

          <p className="password-reset-link">
            {" "}
            <span>Forgot Password?</span>
          </p>

          <p className="login-link">
            Don't have an account?
            {" "}
            <span>Sign Up</span>
          </p>

        </div>
      </div>

      <footer className="signup-footer">
        Co-Cart
      </footer>

    </main>
  );
}
