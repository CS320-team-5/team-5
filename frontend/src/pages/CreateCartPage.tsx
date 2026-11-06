import { Link } from "react-router";
import '../styles/createcart.css';
import { useEffect, useState } from "react";
import { createCart } from "../services/cart";

type StoreOption = {
  storeid: number;
  enterprisename: string;
};

export function CreateCartPage() {
  const d = new Date();
  /** Simply accepts a number, turns it into a string, and pads the start with 0s */
  const format = (n: number): string => n.toString().padStart(2, '0');
  // getFullYear because getYear is deprecated
  // getMonth+1 because getMonth is 0-based
  // getDate because getDay gets you the DAY OF THE WEEK

  //const navigate = useNavigate();

  const [priceValues, setPriceValues] = useState({
    targetMin: "",
    initValue: "",
  });
  const handleTargetChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const value = e.currentTarget.value;
    if (/^\d*(\.\d{0,2})?$/.test(value)) {
      setPriceValues((previous) => ({ ...previous, targetMin: value }));
    }
  };
  const handleInitChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const value = e.currentTarget.value;
    if (/^\d*(\.\d{0,2})?$/.test(value)) {
      setPriceValues((previous) => ({ ...previous, initValue: value }));
    }
  };
  const handleFormSubmit: React.SubmitEventHandler<HTMLFormElement> =
    async (e) => {
      e.preventDefault();
      if (isSubmitting) return;
      setSubmitError("");
      setSubmitSuccess("");
      const formData = new FormData(e.currentTarget);
      const storeid = Number(formData.get("store"));
      const location = String(formData.get("location-input") ?? "").trim();
      const deadline = new Date(
        String(formData.get("deadline-input") ?? "")
      );
      const minimumamount = String(formData.get("target_min") ?? "");
      const startingAmount = String(formData.get("start_amount") ?? "");
      const notes = String(formData.get("notes-input") ?? "").trim();

      if (!Number.isInteger(storeid) || storeid <= 0) {
        setSubmitError("Please select a store.");
        return;
      }
      if (!location || location.length > 30) {
        setSubmitError("Enter a location between 1 and 30 characters.");
        return;
      }
      if (
        Number.isNaN(deadline.getTime()) ||
        deadline <= new Date()
      ) {
        setSubmitError("Please choose a future deadline.");
        return;
      }
      if (!Number.isFinite(Number(minimumamount)) ||
          Number(minimumamount) <= 0) {
        setSubmitError("The minimum amount must be greater than zero.");
        return;
      }
      // These fields need additional backend support.
      if (
        !startingAmount.trim() ||
        !Number.isFinite(Number(startingAmount)) ||
        Number(startingAmount) < 0
      ) {
        setSubmitError("Your planned amount must be zero or greater.");
        return;
      }

      setIsSubmitting(true);
      try {
        const cart = await createCart({
          storeid,
          location,
          deadline: deadline.toISOString(),
          minimumamount,
          owneramount: startingAmount,
          notes: notes || null,
        });
        setSubmitSuccess(`Cart ${cart.cartid} created successfully.`);
      } catch (error) {
        setSubmitError(
          error instanceof Error
            ? error.message
            : "Could not create the cart."
        );
      } finally {
        setIsSubmitting(false);
      }
    };
  const [stores, setStores] = useState<StoreOption[]>([]);
  const [storesLoading, setStoresLoading] = useState(true);
  const [storeError, setStoreError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [submitSuccess, setSubmitSuccess] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadStores() {
      try {
        const response = await fetch("/api/store", {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Could not load stores.");
        }

        const data: StoreOption[] = await response.json();
        setStores(data);
      } catch (error) {
        if (!controller.signal.aborted) {
          setStoreError(
            error instanceof Error ? error.message : "Could not load stores."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setStoresLoading(false);
        }
      }
    }

    loadStores();
    return () => controller.abort();
  }, []);
  return (
    <main id="create-cart-page">
      <header id="banner">
        <Link id="left-banner-part" to="/" aria-label="CoCart home">
          <img src="/hero_logo.svg" />
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
      <div id="form-section">
        <div id="form-container">
          <div id="start-cart-header">
            <div id="start-cart-title">Start a Cart</div>
            <div className="general-text">Set up a shared order so neighbors can add to your cart.</div>
          </div>
          <div>
            <form action="" method="get" id="cart-form" onSubmit={handleFormSubmit}>
              <div className="form-text">
                <label htmlFor="store-input">1. Store or Restaurant</label>
                <select
                  name="store"
                  id="store-input"
                  defaultValue=""
                  required
                  disabled={storesLoading || stores.length === 0}
                >
                  <option value="" disabled>
                    {storesLoading
                      ? "Loading stores..."
                      : stores.length === 0
                        ? "No stores available"
                        : "Select a store"}
                  </option>

                  {stores.map((store) => (
                    <option key={store.storeid} value={store.storeid}>
                      {store.enterprisename}
                    </option>
                  ))}
                </select>
                {storeError && <p role="alert">{storeError}</p>}
              </div>
              <div className="form-text" id="price-section">
                2. Order Minimum & Your Share
                <div id="price-container">
                  <div className="small-text">
                    <label htmlFor="threshold">Target Minimum</label>
                    <div className="general-container">
                      <span className="price-text">$</span>
                      <input
                        type="text" inputMode="decimal" name="target_min"
                        value={priceValues.targetMin} placeholder="0.00"
                        id="threshold" pattern="[0-9]+(\.[0-9][0-9]?)?"
                        className="price-input" required onChange={handleTargetChange}
                      />
                    </div>
                  </div>
                  <div className="small-text" style={{"gap": 4}}>
                    <label htmlFor="start_amount">What you're spending</label>
                    <div className="general-container">
                      <span className="price-text">$</span>
                      <input
                        type="text" inputMode="decimal" name="start_amount"
                        value={priceValues.initValue} placeholder="0.00"
                        id="start_amount" pattern="[0-9]+(\.[0-9][0-9]?)?"
                        className="price-input" required onChange={handleInitChange}
                      />
                    </div>
                  </div>
                </div>
                <div id="notice-section">
                  <span><img src="/piggy_bank.svg" /></span>
                  <div className="general-text">
                    Future cart participants need to add <span id="diff-text">${Math.max(0,Number(priceValues.targetMin) - Number(priceValues.initValue)).toFixed(2)}</span> to reach the delivery minimum
                  </div>
                </div>
              </div>
              <div id="location-section">
                <label htmlFor="location-input" className="form-text">
                  3. Pickup Location (Common Spot)
                </label>
                <input
                  type="text" id="location-input" name="location-input"
                  list="prev-locations" placeholder="Type or select..." required
                  className="general-text"
                />

                <datalist id="prev-locations">
                  <option value="Maritown butterbeer"></option>
                  <option value="Instant fun bust"></option>
                  <option value="Marry's butter green"></option>
                  <option value="Monsoon friend"></option>
                  <option value="Mastodon"></option>
                  <option value="Manstand"></option>
                </datalist>
                <div id="safety-container">
                  <span><img src="/lock.svg" /></span>
                  <div className="small-text">Safety consideration: choose a public location to keep private addresses private.</div>
                  </div>
              </div>
              <div id="deadline-section">
                <label htmlFor="deadline-input" className="form-text">4. Deadline</label>
                <input
                  type="datetime-local" id="deadline-input" name="deadline-input"
                  required
                />
              </div>
              <div id="notes-section">
                <label htmlFor="notes-input" className="form-text">5. Notes (Optional)</label>
                <input
                  type="text" id="notes-input" name="notes-input" maxLength={500}
                  placeholder="e.g. Ordering one large pizza, will text when courier arrives"
                />
              </div>{submitError && <p role="alert">{submitError}</p>}{submitSuccess && <p role="status">{submitSuccess}</p>}
              <button id="submitBtn" type="submit" disabled={isSubmitting || storesLoading || stores.length === 0}>
                {isSubmitting ? "Creating cart..." : "Create Cart"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}