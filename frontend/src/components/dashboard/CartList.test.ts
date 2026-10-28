import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { test, expect } from 'vitest';
import { CartList } from './CartList';
import { FilterList } from './FilterList';
import { type CartDetails } from '../../types/cart';

const carts: CartDetails[] = [
  {
    id: 'alex-cart',
    owner: "Alex M.",
    timeLeft: 15,
    store: "Local Grocery Mart",
    pickupLocation: "Building 4 Mailroom",
    openSpots: 2,
    threshold: 50,
    curr: 34
  },
  {
    id: 'kevin-cart',
    owner: "Kevin C.",
    timeLeft: 8,
    store: "Campus Boba House",
    pickupLocation: "Building Lobby Rack",
    openSpots: 1,
    threshold: 30,
    curr: 28
  }
];

test('renders each cart owner, store, pickup location, and available spots', () => {
  const html = renderToStaticMarkup(createElement(CartList, { cartList: carts }));

  for (const cart of carts) {
    expect(html).toContain(cart.owner);
    expect(html).toContain(cart.store);
    expect(html).toContain(cart.pickupLocation);
  }
  expect(html).toContain('2 spots open');
  expect(html).toContain('1 spot open!');
});

test('shows different progress for carts with different totals', () => {
  const html = renderToStaticMarkup(createElement(CartList, { cartList: carts }));

  expect([...html.matchAll(/aria-valuenow="(\d+)"/g)].map(match => match[1])).toEqual(['68', '93']);
  expect(html).toContain('width:68%');
  expect(html).toContain('width:93%');
  expect(html).toContain('$16 needed');
  expect(html).toContain('$2 needed');
});

test('caps fully funded carts at 100 percent and shows no negative amount needed', () => {
  const html = renderToStaticMarkup(createElement(CartList, {
    cartList: [{ ...carts[0], curr: 60 }],
  }));

  expect(html).toContain('aria-valuenow="100"');
  expect(html).toContain('width:100%');
  expect(html).toContain('$0 needed');
});

test('renders no cart cards when the cart list is empty', () => {
  expect(renderToStaticMarkup(createElement(CartList, { cartList: [] }))).toBe('');
});

test('renders the supplied filter labels as buttons', () => {
  const filters = ['All Carts', 'Groceries', 'Takeout'];
  const html = renderToStaticMarkup(createElement(FilterList, { filterList: filters }));

  expect(html.match(/<button\b/g)).toHaveLength(filters.length);
  for (const filter of filters) expect(html).toContain(filter);
});

test('renders no filter buttons when the filter list is empty', () => {
  expect(renderToStaticMarkup(createElement(FilterList, { filterList: [] }))).toBe('');
});
