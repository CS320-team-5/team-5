import { getSession } from "./auth";

export type UserProfile = {
  userid: number;
  name: string | null;
  location: string | null;
};

export async function getCurrentUser(
  signal?: AbortSignal
): Promise<UserProfile | null> {
  const session = await getSession();
  // A guest has no current profile.
  if (!session?.access_token) {
    return null;
  }

  const response = await fetch("/api/user/me", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
    },
    signal,
  });

  if (!response.ok) {
    throw new Error("Could not load your profile.");
  }

  return response.json();
}