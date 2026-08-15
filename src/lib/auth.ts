"use client";

/**
 * There's no login/register UI in this app (per BACKEND_INTEGRATION.md
 * §6, auth wasn't built on the frontend side). The backend requires an
 * email/password account though, so this bootstraps one silently the
 * first time a device needs to talk to the API: generate random
 * credentials, register, log in, and persist the token + credentials so
 * the same "account" is reused on every future visit from this device
 * and the session can be re-established if the JWT expires.
 *
 * This is a deliberate simplification for the MVP, not a real identity
 * system — there's no way to move this account to a new device/browser,
 * and anyone with access to this browser's storage has full access to
 * the account. Fine for a single-device demo; flag before shipping
 * multi-device support.
 */

const STORAGE_KEY = "acementor:session";

interface StoredSession {
  email: string;
  password: string;
  token: string | null;
  userId: string | null;
}

function readSession(): StoredSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as StoredSession;
  } catch {
    return null;
  }
}

function writeSession(session: StoredSession) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

function randomCredentials(): { email: string; password: string } {
  const id =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;

  return {
    email: `${id}@example.com`,
    password: `pw_${id}`.slice(0, 24),
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function registerAndLogin(email: string, password: string): Promise<string> {
  const registerRes = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  void registerRes; // registration may 409 if this device already has an account — that's fine, login below is what matters

  const loginRes = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!loginRes.ok) {
    throw new Error(`Login failed (${loginRes.status})`);
  }

  const body = (await loginRes.json()) as {
    access_token: string;
    user_id: string;
  };

  return body.access_token;
}
/** Returns a valid bearer token, creating and/or refreshing the device's
 * anonymous session as needed. Safe to call before every authenticated
 * request. */
export async function ensureToken(): Promise<string> {
  let session = readSession();

  if (!session) {
    const creds = randomCredentials();
    session = { ...creds, token: null, userId: null };
    writeSession(session);
  }

  if (session.token) {
    return session.token;
  }

  const token = await registerAndLogin(session.email, session.password);
  writeSession({ ...session, token });
  return token;
}

/** Called after a 401 from the API — the stored token is stale/expired,
 * so re-authenticate with the same stored credentials and get a fresh
 * one. */
export async function refreshToken(): Promise<string> {
  const session = readSession();
  if (!session) return ensureToken();
  const token = await registerAndLogin(session.email, session.password);
  writeSession({ ...session, token });
  return token;
}

export function clearSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}
