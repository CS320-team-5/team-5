import { type CartDetails } from "./types";

/*
{
  owner: "Alex M.",
  time_left: 15,
  store: "Local Grocery Mart",
  pickupLocation: "Building 4 Mailroom",
  openSpots: 2,
  threshold: 50,
  curr: 34,
}
*/

export function CartList({ cartList }: { cartList: CartDetails[] }) {
  return cartList.map(cartDetails => {
    const initials = cartDetails.owner.split(' ').reduce((acc, e) => acc + e.charAt(0), '');
    return <>
      <div className="cart-cell">
        <div className="details-row">
          <div className="other-account-pill">
            <div className="other-account-initials">{initials}</div>
              {cartDetails.owner}
          </div>
          <div className="timer-pill">
            {cartDetails.timeLeft}m left
          </div>
        </div>
        <div className="details-row">
          <div>
            <div className="store-title">{cartDetails.store}</div>
            <div className="location-text">{cartDetails.pickupLocation}</div>
          </div>
          <div className="spots-left-text">{cartDetails.openSpots} spot{cartDetails.openSpots != 1 ? "s" : ""} open</div>
        </div>
        <div className="status-cell">
          <div className="status-row">
            <div>${cartDetails.curr} of ${cartDetails.threshold} target</div>
            <div style={{color: "#B5260B", fontWeight: 700}}>${cartDetails.threshold - cartDetails.curr} needed</div>
          </div>
          <div className="progress-track">
            <div className="progress-fill"></div>
          </div>
        </div>
        <div className="join-button">Join Cart</div>
      </div>
    </>;
  });
}