const API_BASE = "http://localhost:8000";

export type SearchItem = {
  listing: {
    id: number;
    year: number;
    make: string;
    model: string;
    trim?: string | null;
    mileage: number;
    price: number;
    city?: string | null;
    state?: string | null;
    zip?: string | null;
  };
  predicted_price: number;
  diff: number;
  diff_pct: number;
  deal_score: number;
  badge: string;
};

export async function searchListings(params: Record<string, string>) {
  const qs = new URLSearchParams(params);
  const res = await fetch(`${API_BASE}/search?${qs.toString()}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Search failed");
  return (await res.json()) as { results: SearchItem[] };
}

export async function getListing(id: number) {
  const res = await fetch(`${API_BASE}/listing/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Listing fetch failed");
  return await res.json();
}
