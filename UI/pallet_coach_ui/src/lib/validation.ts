export function parsePositiveInt(raw: string): number | null {
  if (!raw.trim()) {
    return null;
  }
  const value = Number(raw);
  if (!Number.isInteger(value) || value <= 0) {
    return null;
  }
  return value;
}

export function parseFiniteNumber(raw: string): number | null {
  if (!raw.trim()) {
    return null;
  }
  const value = Number(raw);
  if (!Number.isFinite(value) || value <= 0) {
    return null;
  }
  return value;
}
