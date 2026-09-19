const API_BASE = import.meta.env.VITE_API_URL || '';

export async function getRiskSummary() {
  if (!API_BASE) return { score: 22, status: 'Low risk' };
  const response = await fetch(`${API_BASE}/risk/summary`);
  if (!response.ok) throw new Error('Unable to load risk summary');
  return response.json();
}