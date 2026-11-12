import "../styles/settings.css";
import "../styles/dashboard.css";
import Banner from "../components/Banner"

export default function SettingsPage() {
  return (
    <div className="dashboard-page">
    <Banner />
    
    <div className="settings-page">
      <div className="settings-header">
        <div>
          <p className="verified-label">✓ VERIFIED PROFILE</p>
          <h1>Account & Settings</h1>
          <p className="settings-subtitle">
            Manage your neighborhood identity, settlement handles, and cart
            alerts.
          </p>
        </div>

        <div className="status-pill">
          ● Cart Status: Active in 1 cart
        </div>
      </div>

      <div className="settings-layout">
        {/* LEFT COLUMN */}
        <div className="settings-column">
          <section className="settings-card">
            <div className="card-header">
              <h2>Personal Information</h2>
              <span className="badge">Public in Carts</span>
            </div>

            <div className="profile-section">
              <div className="profile-avatar">📷</div>

              <div>
                <h3>Maya Lin</h3>
                <p>Member since October 2023</p>

                <div className="address-pill">
                  Brooklyn, NY
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Full Name</label>
              <input type="text" value="Maya Lin" readOnly />
            </div>

            <div className="two-column">
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value="maya.lin@example.com"
                  readOnly
                />
              </div>

              <div className="form-group">
                <label>Mobile Phone</label>
                <input
                  type="text"
                  value="(555) 234-8901"
                  readOnly
                />
              </div>
            </div>

            <div className="form-group">
              <label>Default Pickup Location</label>

              <select defaultValue="75 Montague">
                <option>75 Montague St (Brooklyn Heights Lobby)</option>
                <option>Main Street Pickup Hub</option>
              </select>
            </div>
          </section>

          <section className="settings-card actions-card">
            <button className="save-button">
              Save Changes
            </button>

            <div className="bottom-actions">
              <button className="text-button">
                Sign Out
              </button>

              <button className="delete-button">
                Delete Account
              </button>
            </div>
          </section>

          
        </div>

        {/* RIGHT COLUMN */}
        <div className="settings-column right-column">
          <section className="settings-card">
            <div className="card-header">
              <h2>Stats and Record</h2>
            </div>

            <div className="stat-card">
              <span>Total Savings</span>
              <h3>$148.50</h3>
            </div>

            <div className="stat-card">
              <span>Completed Carts</span>
              <h3>18 carts</h3>
            </div>

            <div className="stat-card">
              <span>Average Rating</span>
              <h3>4.79 / 5</h3>
            </div>
          </section>

          <section className="settings-card">
            <h2>Cart Alerts</h2>

            <div className="toggle-row">
              <div>
                <strong>Courier arrival SMS</strong>
                <p>
                  Alert when Co-Cart order is marked as delivered
                </p>
              </div>

              <input type="checkbox" defaultChecked />
            </div>

            <div className="toggle-row">
              <div>
                <strong>Nearby carts opened</strong>
                <p>
                  Alert when users within 10mi initiate a Co-Cart
                </p>
              </div>

              <input type="checkbox" defaultChecked />
            </div>

            <div className="toggle-row">
              <div>
                <strong>Direct Messages</strong>
                <p>
                  Alerts when direct messages are recieved
                </p>
              </div>

              <input type="checkbox" defaultChecked />
            </div>
          </section>
        </div>
      </div>
    </div>
    </div>
  );
}