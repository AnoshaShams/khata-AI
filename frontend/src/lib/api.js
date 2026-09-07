// Talks to the FastAPI backend. Shapes here must match docs/CONTRACTS.md exactly.
// If you change a request/response shape, update CONTRACTS.md in the same commit.

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Single demo business for the hackathon build — no auth/login flow in scope.
// Swap this for a real business_id once/if a login screen exists.
export const DEMO_BUSINESS_ID = "demo-business-1";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: options.body instanceof FormData ? undefined : { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      detail = data.detail || detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }

  if (res.status === 204) return null;
  return res.json();
}

// --- OCR path: photo -> Parsed Transaction[] (Qwen2-VL does extraction+structuring in one call) ---
export function uploadLedgerPhoto(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/ledger/upload", { method: "POST", body: formData });
}

// --- Voice path: audio -> single Parsed Transaction (STT + parse combined in one call) ---
export function processVoice(audioFile, languageMode = "urdu") {
  const formData = new FormData();
  formData.append("file", audioFile);
  formData.append("language_mode", languageMode);
  return request("/voice/process", { method: "POST", body: formData });
}

// --- Confirm a reviewed transaction -> writes to the ledger ---
export function confirmTransaction({ businessId, customerName, amount, type, item, source }) {
  return request("/ledger/confirm", {
    method: "POST",
    body: JSON.stringify({
      business_id: businessId,
      customer_name: customerName,
      amount,
      type,
      item: item || null,
      source,
    }),
  });
}

// --- Dashboard ---
export function getDashboard(businessId) {
  return request(`/ledger/${businessId}`);
}

// --- Trust score ---
export function getTrustScore(businessId) {
  return request(`/score/${businessId}`);
}

// --- Reminders ---
export function getReminders(businessId) {
  return request(`/reminders/${businessId}`);
}