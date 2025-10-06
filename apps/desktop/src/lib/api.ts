/// <reference types="vite/client" />

export const API_BASE = import.meta.env?.VITE_API_BASE ?? ""; // empty to use Vite proxy

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Request failed ${res.status}: ${text}`);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return (await res.json()) as T;
  return (await res.text()) as unknown as T;
}

export async function ingest(): Promise<{ status: string }> {
  return await request<{ status: string }>("/api/ingest", { method: "POST" });
}

export async function query(question: string, topK = 3): Promise<{ answer: string }> {
  return await request<{ answer: string }>("/api/query", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

async function uploadForm<T>(path: string, file: File): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}${path}`, { method: "POST", body: form });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Upload failed ${res.status}: ${text}`);
  }
  return (await res.json()) as T;
}

export async function uploadAssignment(file: File): Promise<{ status: string; stored_as: string; sha256: string }> {
  return await uploadForm("/api/upload", file);
}

export async function uploadRubric(file: File): Promise<{ status: string; stored_as: string; sha256: string }> {
  return await uploadForm("/api/upload-rubric", file);
}
