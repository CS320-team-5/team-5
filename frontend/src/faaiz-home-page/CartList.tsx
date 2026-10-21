import { type CartDetails } from "./types";
// see types.ts for the structure of a CartDetails object

/**
 * Returns a div containing the formatted contents of the 
 * @param param0 
 * @returns 
 */
export function CartList({ cartList }: { cartList: CartDetails[] }) {
  return cartList.map(cartDetails => {
    // initials used in icon for owner account of each cart entry
    const initials = cartDetails.owner.split(' ').reduce((acc, e) => acc + e.charAt(0), '');
    // use this to make "spots" plural or singular in cart entry and also to make text red if true
    const oneSpotLeft = cartDetails.openSpots == 1;
    // use this to make text for time red if at most 15 m left
    const nearDeadline = cartDetails.timeLeft <= 15;
    // finally, use this to set the width of the progress bar
    const percentage = Math.min(Math.floor(cartDetails.curr / cartDetails.threshold * 100), 100);
    return <>
      <div className="cart-cell">
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
            <div style={{color: "#B5260B", fontWeight: 700}}>${cartDetails.threshold - cartDetails.curr} needed</div>
          </div>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
          </div>
        </div>
        <div className="join-button">Join Cart</div>
      </div>
    </>;
  });
}