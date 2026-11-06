import { getSession } from "./auth";

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