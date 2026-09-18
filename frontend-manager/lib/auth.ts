export const STAFF_STORAGE_KEY = "aeroresolve.staff.v1";

export function readStaffToken(): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(STAFF_STORAGE_KEY);
}

export function writeStaffToken(token: string) {
  sessionStorage.setItem(STAFF_STORAGE_KEY, token);
}

export function clearStaffToken() {
  sessionStorage.removeItem(STAFF_STORAGE_KEY);
}

export function takeStaffTokenFromHash(): string | null {
  if (typeof window === "undefined") return null;
  const match = window.location.hash.match(/(?:^#|&)st=([^&]+)/);
  if (!match) return null;
  const token = decodeURIComponent(match[1]);
  writeStaffToken(token);
  window.history.replaceState(null, "", window.location.pathname + window.location.search);
  return token;
}

export async function staffLogin(email: string, password: string): Promise<string> {
  const response = await fetch("/api/auth/staff/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = (body as { detail?: unknown }).detail;
    throw new Error(typeof detail === "string" ? detail : "Email or password is incorrect.");
  }
  const token = (body as { token?: string }).token;
  if (!token) throw new Error("Email or password is incorrect.");
  writeStaffToken(token);
  return token;
}

export async function staffLogout(token: string | null) {
  if (token) {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    }).catch(() => undefined);
  }
  clearStaffToken();
}
