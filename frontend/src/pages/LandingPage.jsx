import '../styles/landing.css'

function LandingPage() {
  return (
    <div className="landing-page">
      <header>
        <a className="logo" href="#">CoCart</a>
        <nav aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="/dashboard">Browse carts</a>
          <button className="button button-outline" type="button">Log in</button>
          <button className="button" type="button">Sign up</button>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div>
            <h1>Meet the delivery minimum, together.</h1>
            <p>
              Create or join a cart at your favorite store and find another
              shopper to combine orders with. Get in touch, confirm payment
              details, and coordinate pickup together.
            </p>
            <a className="button" href="#get-started">Get started</a>
          </div>
          <img className="delivery-picture" src="/delivery.svg" alt="Two delivery bags and a takeout box" width="320" height="280" />
        </section>

        <section id="how-it-works">
          <h2>How it works</h2>
          <div className="steps">
            <article>
              <h3>1. Create or join a cart</h3>
              <p>Start a shopping cart at your favorite store or join an existing one.</p>
            </article>
            <article>
              <h3>2. Find another shopper</h3>
              <p>Connect with someone who wants to combine their order with yours.</p>
            </article>
            <article>
              <h3>3. Get in touch and confirm payments</h3>
              <p>Discuss payment details with the other shopper and agree on a pickup plan.</p>
            </article>
            <article>
              <h3>4. Enjoy the benefits</h3>
              <p>Meet the delivery minimum and enjoy the benefits of your combined purchase.</p>
            </article>
          </div>
        </section>

        <section className="get-started" id="get-started">
          <h2>Ready to order together?</h2>
          <p>Create or join a cart and find someone to shop with.</p>
          <button className="button" type="button">Sign up</button>
        </section>
      </main>

      <footer>CoCart — Shared orders, easier pickups.</footer>
    </div>
  )
}

export default LandingPage
