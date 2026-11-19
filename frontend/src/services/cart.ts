import { getSession } from "./auth";
import type { CartDetails } from "../types/cart";

export type CreateCartInput = {
  storeid: number;
  location: string;
  deadline: string;
  minimumamount: string;
  owneramount: string;
  notes: string | null;
};

export type CreatedCart = Omit<CreateCartInput, "owneramount"> & {
  cartid: number;
  owneruserid: number;
  status: "Active" | "Inactive";
  currentamount: string;
};

export async function createCart(
  values: CreateCartInput
): Promise<CreatedCart> {
  const session = await getSession();
  if (!session?.access_token) {
    throw new Error("Please log in before creating a cart.");
  }
  const response = await fetch("/api/cart", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify(values),
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((error) => error.msg).join("; ")
          : "Could not create the cart.";
    throw new Error(message);
  }
  return data;
}


export type ApiCart = {
  cartid: number;
  storeid: number;
  owneruserid: number;
  location: string | null;
  deadline: string;
  minimumamount: string;
  currentamount: string;
}

export async function getActiveCart(signal?: AbortSignal): Promise<ApiCart[]> {
  const response = await fetch("/api/cart?status=Active", { signal });

  if(!response.ok){
    throw new Error(`Could not load carts (${response.status}).`);
  }
  return response.json();
}

export function toCard(cart: ApiCart): CartDetails{
  return {
  id: cart.cartid,
  owner: `User ${cart.owneruserid}`,
  store: `Store ${cart.storeid}`,
  pickupLocation: cart.location ?? "Pickup location pending",
  timeLeft: Math.max(
    0,
    Math.ceil((Date.parse(cart.deadline) - Date.now()) / 60_000),
  ),
  threshold: parseFloat(cart.minimumamount),
  curr: Number(cart.currentamount),
  openSpots: 0,
 };
}
