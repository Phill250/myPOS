import type { ReactNode } from "react";
import type { RentalStatus } from "../lib/types";
import { day } from "../lib/format";

export function PageHead({ title, sub, actions }: { title: string; sub?: ReactNode; actions?: ReactNode }) {
  return (
    <header className="page-head">
      <div>
        <h1>{title}</h1>
        {sub && <p className="page-sub">{sub}</p>}
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="loading" role="status">
      <span className="spinner" aria-hidden /> {label}
    </div>
  );
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="error-note" role="alert">
      <span>{message}</span>
      {onRetry && (
        <button className="btn btn-small" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

export function Empty({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="empty">
      <p>{children}</p>
      {action}
    </div>
  );
}

/** Library due-date stamp — the visual signature for loans. */
export function DueStamp({ date, status }: { date: string; status: RentalStatus }) {
  const label = status === "returned" ? "Returned" : status === "overdue" ? "Overdue" : "Due";
  return (
    <span className={`stamp stamp-${status}`}>
      <span className="stamp-label">{label}</span>
      <span className="stamp-date">{day(date)}</span>
    </span>
  );
}

export function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: ReactNode;
  children: ReactNode;
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  );
}

export function StockBadge({ count, kind }: { count: number; kind: "shop" | "library" }) {
  const tone = count === 0 ? "none" : count <= 3 ? "low" : "ok";
  return (
    <span className={`stock stock-${tone}`} title={kind === "shop" ? "Copies for sale" : "Copies to lend"}>
      {count} {kind === "shop" ? "for sale" : "to lend"}
    </span>
  );
}
