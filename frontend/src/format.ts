const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function previousDayLabel(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  date.setUTCDate(date.getUTCDate() - 1);
  return `${date.getUTCDate()} ${MONTHS[date.getUTCMonth()]},`;
}

export function fetchedLabel(isoTimestamp: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/.exec(isoTimestamp);
  if (!match) return "date unknown";
  const [, year, month, day, hours, minutes] = match;
  const dateText = `${Number(day)} ${MONTHS[Number(month) - 1]} ${year}`;
  return hours && minutes ? `${dateText}, ${hours}:${minutes} UTC` : dateText;
}

export function gw(value: number | null, digits: number): string {
  if (value === null) return "—";
  return value.toFixed(digits);
}

export function signedGw(value: number | null): string {
  if (value === null) return "—";
  const text = Math.abs(value).toFixed(2);
  if (value < 0) return `−${text}`;
  if (value > 0) return `+${text}`;
  return "0.00";
}

export function percent(value: number | null): string {
  if (value === null) return "—";
  return `${(value * 100).toFixed(1)}%`;
}
