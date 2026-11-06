import '../styles/signup.css';
import { ArrowRight } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { signIn } from "../services/auth";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(event) {
    event.preventDefault();

    if (isSubmitting) return;

    setError("");
    setIsSubmitting(true);

    try {
      const data = await signIn(email.trim(), password);

      if (!data.session) {
        throw new Error("Login did not create a session. Please try again.");
      }

      navigate("/create");
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Could not log in."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="signup-page">
      <header className="signup-header">
        <h1>
          Co-Cart<span className="brand-dot">.</span>
        </h1>

        <Link className="login-button" to="/signup">
          Sign Up
        </Link>
      </header>

      <div className="signup-content">
        <div className="signup-card">
          <h2 className="signup-title">Log In</h2>

          <div className="social-buttons">
            <button type="button" disabled>
              Google
            </button>
            <button type="button" disabled>
              Apple
            </button>
          </div>

          <div className="divider">
            <div className="divider-line"></div>
            <span className="divider-text">OR EMAIL</span>
            <div className="divider-line"></div>
          </div>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="login-email">Email Address</label>

              <input
                id="login-email"
                type="email"
                placeholder="you@example.com"
                autoComplete="username"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="login-password">Password</label>

              <input
                id="login-password"
                type="password"
                placeholder="Your password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>
            {error && <p role="alert">{error}</p>}
            <button
              className="create-account-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Logging in..." : "Log In"}
              <ArrowRight size={20} />
            </button>
          </form>

          <p className="login-link">
            Don't have an account?{" "}
            <Link to="/signup">Sign Up</Link>
          </p>
        </div>
      </div>
      <footer className="signup-footer">Co-Cart</footer>
    </main>
  );
}