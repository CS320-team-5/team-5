import '../styles/signup.css';
import { Link } from 'react-router'
import { useNavigate } from "react-router";
import { ArrowRight, MapPin } from "lucide-react";
import { useState } from 'react';
import { supabase } from '../lib/supabase';
import "../styles/theme.module.css";
import { ShoppingBasket } from "lucide-react";


export default function SignUpPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [location, setLocation] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();


  const handleSignUp = async (e) => {
    e.preventDefault();

    if (loading) {
      return;
    }

    try {
      setLoading(true);
      setError("");

      const {
        data,
        error: authError,
      } = await supabase.auth.signUp({
        email,
        password,
      });

      if (authError) {
        throw authError;
      }

      if (!data.user) {
        throw new Error("User creation failed");
      }

      /*const { error: userError } =
        await supabase
          .from("users")
          .insert({
            name,
            email,
            location,
            status: true,
            authid: data.user.id,
          });

      if (userError) {
        console.log("FULL USER ERROR:");
        console.log(JSON.stringify(userError, null, 2));
        throw userError;
      }*/

      navigate("/dashboard");

      alert(
        "Account created. Check your email for verification."
      );

    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <main className="signup-page">

      <header className="signup-header">
        <Link className={theme["left-banner-part"]} to="/" aria-label="Co-Cart home">
          <ShoppingBasket color="var(--primary-green)"/>
          <span className={theme["logo-title"]}>Co-Cart</span>
        </Link>

        <Link className="login-button" to="/login">
          Log In
        </Link>
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
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Maya Lin"
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>

          <div className="form-group">
            <label>Building Address / Zip</label>

            <div className="address-wrapper">
              <input
                type="text"
                value={location}
                onChange={(e) =>
                  setLocation(e.target.value)
                }
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
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="8+ characters"
            />
          </div>

          {
            error && (
              <p style={{ color: "red" }}>
                {error}
              </p>
            )
          }

          <button
            type="button"
            className="create-account-button"
            onClick={handleSignUp}
            disabled={loading}
          >
            {loading ? "Creating..." : "Create Account"}
            <ArrowRight size={20} />
          </button>

          <p className="login-link">
            Already have an account?
            {" "}
            <Link to="/login"><span>Log in</span></Link>
          </p>

        </div>
      </div>

      <footer className="signup-footer">
        Co-Cart
      </footer>

    </main>
  );
}
