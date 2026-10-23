import { type CartDetails } from "./types";

/** Render the current cart data as cards. */
export function CartList({ cartList }: { cartList: CartDetails[] }) {
  return cartList.map(cartDetails => {
    // initials used in icon for owner account of each cart entry
    const initials = cartDetails.owner.split(' ').reduce((acc, e) => acc + e.charAt(0), '');
    // use this to make "spots" plural or singular in cart entry and also to make text red if true
    const oneSpotLeft = cartDetails.openSpots === 1;
    // use this to make text for time red if at most 15 m left
    const nearDeadline = cartDetails.timeLeft <= 15;
    // finally, use this to set the width of the progress bar
    const percentage = Math.min(Math.floor(cartDetails.curr / cartDetails.threshold * 100), 100);
    const amountNeeded = Math.max(cartDetails.threshold - cartDetails.curr, 0);
    return (
      <div className="cart-cell" key={cartDetails.id}>
        <div className="details-row">
          <div className="other-account-pill">
            <div className="other-account-initials">{initials}</div>
              {cartDetails.owner}
          </div>
          <div className="timer-pill" style={nearDeadline ? {color: "#B5260B"} : undefined}>
            {cartDetails.timeLeft}m left
          </div>
        </div>
        <div className="details-row">
          <div>
            <div className="store-title">{cartDetails.store}</div>
            <div className="location-text">{cartDetails.pickupLocation}</div>
          </div>
          <div className="spots-left-text" style={oneSpotLeft ? {color: "#B5260B"} : undefined}>
            {cartDetails.openSpots} {!oneSpotLeft ? "spots open" : "spot open!"}
          </div>
        </div>
        <div className="status-cell">
          <div className="status-row">
            <div>${cartDetails.curr} of ${cartDetails.threshold} target</div>
            <div style={{color: "#B5260B", fontWeight: 700}}>${amountNeeded} needed</div>
          </div>
          <div
            className="progress-track"
            role="progressbar"
            aria-label={`${cartDetails.store} delivery minimum`}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={percentage}
          >
            <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
          </div>
        </div>
        <button className="join-button" type="button">Join Cart</button>
      </div>
    );
  });
}

/**
 * Returns a JSX list of filters to be displayed as the filter list above the carts
 * on the dashboard
 * @param param0 An object containing a single member (filterList), an array of strings
 */
export function FilterList({ filterList }: { filterList: string[] }) {
  return filterList.map(filter => (
    <button className="filter-button" type="button" key={filter}>
      <span className="filter-text">{filter}</span>
    </button>
  ));
}
