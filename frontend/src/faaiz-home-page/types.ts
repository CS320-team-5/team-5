export type CartDetails = { 
  id: React.Key,
  owner: string,
  timeLeft: number,
  store: string,
  pickupLocation: string,
  openSpots: number,
  threshold: number,
  curr: number
};