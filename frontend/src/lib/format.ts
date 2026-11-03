import type { PaymentMethod } from "./types";

const rwf = new Intl.NumberFormat("en-RW", { maximumFractionDigits: 0 });

/** 12500 -> "12,500 RWF" */
export function money(amount: number | string): string {
  return `${rwf.format(Math.round(Number(amount)))} RWF`;
}

/** 12500 -> "12,500" (when the unit is shown elsewhere) */
export function num(amount: number | string): string {
  return rwf.format(Math.round(Number(amount)));
}

// Backend sends UTC timestamps; SQLite drops the "Z", so add it back.
function parse(value: string): Date {
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return new Date(`${value}T00:00:00`);
  const hasZone = /[zZ]|[+-]\d{2}:?\d{2}$/.test(value);
  return new Date(hasZone ? value : `${value}Z`);
}

export function dateTime(value: string): string {
  return parse(value).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function day(value: string): string {
  return parse(value).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function shortDay(value: string): string {
  return parse(value).toLocaleDateString("en-GB", { weekday: "short" });
}

/** yyyy-mm-dd for <input type="date">, in local time */
export function isoDate(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

export function addDays(days: number, from = new Date()): string {
  const d = new Date(from);
  d.setDate(d.getDate() + days);
  return isoDate(d);
}

export const PAYMENT_METHODS: { value: PaymentMethod; label: string }[] = [
  { value: "cash", label: "Cash" },
  { value: "mtn_momo", label: "MTN MoMo" },
  { value: "airtel_money", label: "Airtel Money" },
  { value: "card", label: "Card" },
  { value: "bank_transfer", label: "Bank transfer" },
];

export function methodLabel(value: string | null | undefined): string {
  if (!value) return "—";
  return PAYMENT_METHODS.find((m) => m.value === value)?.label ?? value;
}

export const ROLE_LABELS = {
  customer: "Customer",
  staff: "Staff",
  super_admin: "Administrator",
} as const;
