import { Link } from "react-router";
import '../styles/createcart.css';
import { useState } from "react";

export function CreateCartPage() {
  const d = new Date();
  /** Simply accepts a number, turns it into a string, and pads the start with 0s */
  const format = (n: number): string => n.toString().padStart(2, '0');
  // getFullYear because getYear is deprecated
  // getMonth+1 because getMonth is 0-based
  // getDate because getDay gets you the DAY OF THE WEEK

  //const navigate = useNavigate();

  const [priceValues, setPriceValues] = useState({ targetMin: 0, initValue: 0 });
  const handleTargetChange: React.ChangeEventHandler<HTMLInputElement> =
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const result = e.currentTarget.value.replaceAll(/\D/g, '');
      const newValue = Number(result);
      if (!Number.isNaN(newValue))
        setPriceValues(priceValues => ({...priceValues, targetMin: newValue }));
    };
  const handleInitChange: React.ChangeEventHandler<HTMLInputElement> =
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const result = e.currentTarget.value.replaceAll(/\D/g, '');
      const newValue = Number(result);
      if (!Number.isNaN(newValue))
        setPriceValues(priceValues => ({...priceValues, initValue: newValue }));
    };

  const handleFormSubmit: React.SubmitEventHandler<HTMLFormElement> =
    (e: React.SubmitEvent<HTMLFormElement>) => {
      e.preventDefault();

      const form = e.currentTarget as HTMLFormElement;
      const formData = new FormData(form);

      const deadline_input = formData.get("deadline-input");
      if (deadline_input) {
        const deadline = new Date(deadline_input.toString());
        const currentDate = new Date();

        if (deadline <= currentDate)
          alert(`Please enter a date after the current time: ${currentDate.toDateString()}, ${currentDate.toTimeString()}`);
        else {
          console.log("received!");
        }
          // here, we are fine
          // some sort of post over here to send data to backend
        
      }
      
    };

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
                <label htmlFor="store">1. Store or Restaurant</label>
                <input 
                  type="text" name="store" id="store-input" 
                  placeholder="Or type a place (e.g. Insomnia Cookies)" required
                />
              </div>
              <div className="form-text" id="price-section">
                2. Order Minimum & Your Share
                <div id="price-container">
                  <div className="small-text">
                    <label htmlFor="threshold">Target Minimum</label>
                    <div className="general-container">
                      <span className="price-text">$</span>
                      <input 
                        type="text" inputMode="numeric" name="target_min"
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
                        type="text" inputMode="numeric" name="start_amount" 
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
                    Future cart participants need to add <span id="diff-text">${priceValues.targetMin - priceValues.initValue}</span> to unlock free delivery
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
                  type="text" id="notes-input" name="notes-input"
                  placeholder="e.g. Ordering one large pizza, will text when courier arrives"  
                />
              </div>
              <button id="submitBtn" type="submit">Create Cart</button>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}