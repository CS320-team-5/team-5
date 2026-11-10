export const initialMessages = [
  { cartId: 4928, id: 1, sender: 'Alex', initials: 'AM', time: '1:12 PM', text: "Order placed on DoorDash! Will drop by the lobby when it's here." },
  { cartId: 4928, id: 2, sender: 'Maya', initials: 'ML', time: '1:15 PM', text: 'Awesome, just sent you $14.50 on Venmo.', own: true },
  { cartId: 4928, id: 3, sender: 'Carlos', initials: 'CR', time: '1:18 PM', text: 'Heading to the lobby now, will bring cash or Venmo.' },
  { cartId: 4928, id: 4, sender: 'Alex', initials: 'AM', time: 'Just now', text: '🚗 Driver just pulled up outside!', alert: true },
]

// Demo IDs until carts are loaded from the signed-in user's joined carts.
export const cartConversations = [
  { cartId: 4928, title: "Trader Joe's Cart", status: 'Order Placed', pickupLocation: 'Main Building Lobby', total: 52, target: 50, estimatedDelivery: '~1:30 PM', deliverySavings: 7.99,
    members: [{ id: 1, name: 'Alex', initials: 'AM', host: true }, { id: 2, name: 'Maya', initials: 'ML', own: true }, { id: 3, name: 'Carlos', initials: 'CR' }],
  },
  { cartId: 4929, title: 'Sweetgreen Order', status: 'Completed', pickupLocation: 'Building 4 Mailroom', total: 64, target: 40,
    members: [{ id: 4, name: 'Sarah', initials: 'ST', host: true }, { id: 2, name: 'Maya', initials: 'ML', own: true }, { id: 5, name: 'James', initials: 'JK' }, { id: 6, name: 'Nina', initials: 'NP' }],
  },
  { cartId: 4930, title: 'Chipotle Run', status: 'Ordering', pickupLocation: 'Central Park West Benches', total: 22, target: 40,
    members: [{ id: 3, name: 'Carlos', initials: 'CR', host: true }, { id: 2, name: 'Maya', initials: 'ML', own: true }],
  },
]
