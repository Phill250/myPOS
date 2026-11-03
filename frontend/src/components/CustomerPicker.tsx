import { useMemo, useState } from "react";
import type { Customer } from "../lib/types";
import { CustomerForm } from "../pages/Customers";
import { Modal } from "./Modal";

interface Props {
  customers: Customer[];
  value: Customer | null;
  onChange: (c: Customer | null) => void;
  onCreated: (c: Customer) => void;
  membersOnly?: boolean;
  placeholder?: string;
}

/** Type a name or phone number, pick a customer, or add a new one inline. */
export function CustomerPicker({ customers, value, onChange, onCreated, membersOnly, placeholder }: Props) {
  const [query, setQuery] = useState("");
  const [focused, setFocused] = useState(false);
  const [adding, setAdding] = useState(false);

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    const pool = membersOnly ? customers.filter((c) => c.library_member) : customers;
    if (!q) return pool.slice(0, 6);
    const digits = q.replace(/\D/g, "");
    return pool
      .filter(
        (c) =>
          `${c.first_name} ${c.last_name}`.toLowerCase().includes(q) ||
          (digits.length >= 3 && c.phone_number.replace(/\D/g, "").includes(digits)),
      )
      .slice(0, 6);
  }, [customers, query, membersOnly]);

  if (value) {
    return (
      <div className="picked">
        <div>
          <div className="strong">
            {value.first_name} {value.last_name}
          </div>
          <div className="muted small">
            {value.phone_number}
            {value.library_member ? ", library member" : ""}
          </div>
        </div>
        <button className="btn btn-small" onClick={() => onChange(null)}>
          Change
        </button>
      </div>
    );
  }

  return (
    <div className="picker">
      <input
        type="search"
        value={query}
        placeholder={placeholder ?? "Name or phone number"}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 150)}
        aria-label="Find customer"
      />
      {focused && (
        <ul className="picker-list" role="listbox">
          {matches.map((c) => (
            <li key={c.customer_id}>
              <button
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => {
                  onChange(c);
                  setQuery("");
                }}
              >
                <span className="strong">
                  {c.first_name} {c.last_name}
                </span>
                <span className="muted small">{c.phone_number}</span>
              </button>
            </li>
          ))}
          {matches.length === 0 && (
            <li className="picker-empty muted small">
              No {membersOnly ? "library member" : "customer"} matches “{query}”.
            </li>
          )}
          <li>
            <button
              type="button"
              className="picker-add"
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => setAdding(true)}
            >
              Add a new {membersOnly ? "member" : "customer"}
            </button>
          </li>
        </ul>
      )}
      {adding && (
        <Modal title={membersOnly ? "New library member" : "New customer"} onClose={() => setAdding(false)}>
          <CustomerForm
            initial={{ first_name: guessFirst(query), last_name: guessLast(query), library_member: !!membersOnly }}
            onSaved={(c) => {
              setAdding(false);
              onCreated(c);
              onChange(c);
              setQuery("");
            }}
            onCancel={() => setAdding(false)}
          />
        </Modal>
      )}
    </div>
  );
}

const looksLikePhone = (q: string) => /\d{3}/.test(q);
const guessFirst = (q: string) => (looksLikePhone(q) ? "" : q.trim().split(/\s+/)[0] ?? "");
const guessLast = (q: string) => (looksLikePhone(q) ? "" : q.trim().split(/\s+/).slice(1).join(" "));
