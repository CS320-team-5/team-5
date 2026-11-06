import { getSession } from "./auth";

export type StoreInput = {
  enterprisename: string;
  storetype: "restaurant" | "groceries" | "electronics" | "etc";
  address: string | null;
  minimumorderamount: string;
};

export type Store = StoreInput & {
  storeid: number;
};

export async function createStore(values: StoreInput): Promise<Store> {
  const session = await getSession();
  if (!session?.access_token) {
    throw new Error("Please log in before adding a store.");
  }
  const response = await fetch("/api/store", {
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
    const message = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((error) => error.msg).join("; ")
          : "Could not add the store.";
    throw new Error(message);
  }
  return data;
}