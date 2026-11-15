import { Link } from "react-router";
// @ts-ignore
import theme from "../styles/theme.module.css";
import { ShoppingBasket } from "lucide-react";
import AppHomeLink from "./AppHomeLink";

import { useEffect, useState } from "react";
import { getCurrentUser, type UserProfile } from "../services/user";
import { supabase } from "../lib/supabase";
/**
 * Banner appearing on the Active Carts, Cart Creation, Messaging, and Settings pages
 */
function Banner() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileStatus, setProfileStatus] = useState<
    "loading" | "ready" | "error"
  >("loading");
  useEffect(() => {
    let active = true;
    let controller: AbortController | undefined;
    let refreshTimer: ReturnType<typeof setTimeout> | undefined;
    async function loadProfile() {
      controller?.abort();
      const request = new AbortController();
      controller = request;
      setProfile(null);
      setProfileStatus("loading");
      try {
        const user = await getCurrentUser(request.signal);
        if (active && !request.signal.aborted) {
          setProfile(user);
          setProfileStatus("ready");
        }
      } catch {
        if (active && !request.signal.aborted) {
          setProfileStatus("error");
        }
      }
    }

    const { data: { subscription } } = supabase.auth.onAuthStateChange(() => {
      controller?.abort();
      clearTimeout(refreshTimer);
      refreshTimer = setTimeout(() => {
        if (active) void loadProfile();
      }, 0);
    });

    void loadProfile();

    return () => {
      active = false;
      clearTimeout(refreshTimer);
      controller?.abort();
      subscription.unsubscribe();
    };
  }, []);

  const displayName = profile?.name?.trim() || "Your Account";
  const nameParts = displayName.split(/\s+/);
  const initials = (
    nameParts[0][0] +
    (nameParts.length > 1 ? nameParts[nameParts.length - 1][0] : "")
  ).toUpperCase();
  return (
    <header className={theme["banner"]}>
      <Link className={theme["left-banner-part"]} to="/" aria-label="Co-Cart home">
        <ShoppingBasket color="var(--primary-green)"/>
        <span className={theme["logo-title"]}>Co-Cart</span>
      </Link>
      <nav className={theme["center-banner-part"]} aria-label="Dashboard navigation">
        <Link className={theme["banner-button"]} to="/dashboard" aria-current="page">Browse Carts</Link>
        <Link className={theme["banner-button"]} to="/create" aria-current="page">Start a Cart</Link>
        <Link className={theme["banner-button"]} to="/messages" aria-current="page">Messages</Link>
      </nav>
      {profileStatus === "loading" ? (
        <div className={`${theme["right-banner-part"]} ${theme["account-pill"]}`} role="status">
          Loading account...
        </div>
      ) : profileStatus === "error" ? (
        <Link
          className={`${theme["right-banner-part"]} ${theme["account-pill"]}`} to="/settings">
          Account
        </Link>
      ) : profile ? (
        <Link
          className={`${theme["right-banner-part"]} ${theme["account-pill"]}`} to="/settings" aria-label="Account Settings">
          <span className={theme["account-initials"]} aria-hidden="true">
            {initials}
          </span>
          <span className={theme["name"]}>{displayName}</span>
        </Link>
      ) : (
        <Link
          className={`${theme["right-banner-part"]} ${theme["account-pill"]}`} to="/login">
          Log In
        </Link>
      )}
    </header>
  );
}

export default Banner
