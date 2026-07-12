const API_URL = import.meta.env.VITE_API_URL || "/api";

export function getToken() {
  return localStorage.getItem("rawabet_token");
}

export function setToken(token) {
  localStorage.setItem("rawabet_token", token);
  localStorage.setItem("rawabet_token_created_at", String(Date.now()));
}

export function clearToken() {
  localStorage.removeItem("rawabet_token");
  localStorage.removeItem("rawabet_token_created_at");
}

export function getTokenCreatedAt() {
  return Number(localStorage.getItem("rawabet_token_created_at") || 0);
}

export async function api(path, options = {}) {
  const token = getToken();
  const requestToken = token;
  const headers = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  };

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch (error) {
    throw new Error("Cannot reach Rawabet server. Please check your internet connection or try again in a moment.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = data.detail || data.message || "Request failed";
    const error = new Error(message);
    error.status = response.status;
    error.detail = message;
    error.isSessionError = response.status === 401;
    error.staleSession = response.status === 401 && requestToken && requestToken !== getToken();
    if (response.status === 401 && token && !error.staleSession) {
      window.dispatchEvent(new CustomEvent("rawabet:session-ended", { detail: data.detail || data.message || "Invalid session" }));
    }
    throw error;
  }
  return data;
}
