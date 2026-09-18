export const IATA: Record<string, string> = {
  Delhi: "DEL",
  Goa: "GOI",
  Mumbai: "BOM",
  Bengaluru: "BLR",
  Hyderabad: "HYD",
};

export function toIata(city?: string | null): string {
  if (!city) return "—";
  return IATA[city] || city.slice(0, 3).toUpperCase();
}
