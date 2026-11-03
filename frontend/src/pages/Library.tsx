import { useMemo, useState } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { Book, Customer, PaymentMethod, RentalDetail, RentalSummary } from "../lib/types";
import { PAYMENT_METHODS, addDays, dateTime, day, money } from "../lib/format";
import { CustomerPicker } from "../components/CustomerPicker";
import { Modal } from "../components/Modal";
import { LoanSlip } from "../components/Receipt";
import { useToast } from "../components/Toast";
import { DueStamp, Empty, ErrorNote, Field, Loading, PageHead } from "../components/ui";

type Filter = "open" | "overdue" | "returned" | "all";
const FILTERS: { value: Filter; label: string }[] = [
  { value: "open", label: "Out now" },
  { value: "overdue", label: "Overdue" },
  { value: "returned", label: "Returned" },
  { value: "all", label: "All" },
];

export function LibraryPage() {
  const [filter, setFilter] = useState<Filter>("open");
  const [search, setSearch] = useState("");
  const loans = useApi<RentalSummary[]>(`/pos/rentals?status=${filter}`);
  const [lending, setLending] = useState(false);
  const [openId, setOpenId] = useState<number | null>(null);

  const shown = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return loans.data ?? [];
    return (loans.data ?? []).filter(
      (r) =>
        (r.customer_name ?? "").toLowerCase().includes(q) ||
        (r.customer_phone ?? "").replace(/\s/g, "").includes(q.replace(/\s/g, "")) ||
        r.books.some((b) => b.title.toLowerCase().includes(q)),
    );
  }, [loans.data, search]);

  return (
    <>
      <PageHead
        title="Library loans"
        sub="Lend books to members and check them back in."
        actions={
          <button className="btn btn-primary" onClick={() => setLending(true)}>
            Lend books
          </button>
        }
      />

      <div className="toolbar">
        <div className="tabs" role="tablist">
          {FILTERS.map((f) => (
            <button key={f.value} role="tab" aria-selected={filter === f.value} className={filter === f.value ? "tab tab-on" : "tab"} onClick={() => setFilter(f.value)}>
              {f.label}
            </button>
          ))}
        </div>
        <input type="search" className="toolbar-search" placeholder="Borrower, phone or title" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Search loans" />
      </div>

      {loans.error ? (
        <ErrorNote message={loans.error} onRetry={loans.reload} />
      ) : loans.loading && !loans.data ? (
        <Loading />
      ) : shown.length === 0 ? (
        <Empty
          action={
            filter === "open" && !search ? (
              <button className="btn" onClick={() => setLending(true)}>
                Lend books
              </button>
            ) : undefined
          }
        >
          {search ? `No loan matches “${search}”.` : filter === "overdue" ? "Nothing overdue." : "No loans here yet."}
        </Empty>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Borrower</th>
                <th>Books</th>
                <th>Issued</th>
                <th>Due</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {shown.map((r) => (
                <tr key={r.rental_id} className="row-click" onClick={() => setOpenId(r.rental_id)}>
                  <td>
                    <div className="strong">{r.customer_name}</div>
                    <div className="muted small">{r.customer_phone}</div>
                  </td>
                  <td>
                    {r.books.map((b) => (
                      <div key={b.rental_item_id} className="book-title">
                        {b.title}
                      </div>
                    ))}
                  </td>
                  <td className="muted nowrap">{dateTime(r.rental_timestamp)}</td>
                  <td>
                    <DueStamp date={r.actual_return ?? r.expected_return} status={r.status} />
                    {r.status === "overdue" && (
                      <div className="small text-red">
                        {r.days_overdue} {r.days_overdue === 1 ? "day" : "days"} late
                      </div>
                    )}
                  </td>
                  <td className="right">
                    <button
                      className="btn btn-small"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenId(r.rental_id);
                      }}
                    >
                      {r.status === "returned" ? "View" : "Check in"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {lending && (
        <LendModal
          onClose={() => setLending(false)}
          onDone={(r) => {
            setLending(false);
            loans.reload();
            setOpenId(r.rental_id);
          }}
        />
      )}
      {openId !== null && (
        <LoanModal
          rentalId={openId}
          onClose={() => setOpenId(null)}
          onChanged={loans.reload}
        />
      )}
    </>
  );
}

function LendModal({ onClose, onDone }: { onClose: () => void; onDone: (r: RentalDetail) => void }) {
  const customers = useApi<Customer[]>("/customers/");
  const books = useApi<Book[]>("/books/");
  const toast = useToast();
  const [member, setMember] = useState<Customer | null>(null);
  const [picked, setPicked] = useState<Book[]>([]);
  const [query, setQuery] = useState("");
  const [due, setDue] = useState(addDays(14));
  const [fee, setFee] = useState("0");
  const [method, setMethod] = useState<PaymentMethod>("cash");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return (books.data ?? [])
      .filter((b) => !picked.some((p) => p.book_id === b.book_id))
      .filter((b) => b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q) || (b.isbn ?? "").includes(q))
      .slice(0, 6);
  }, [books.data, query, picked]);

  async function submit() {
    if (!member) return setError("Choose the borrower first.");
    if (!picked.length) return setError("Add at least one book.");
    setBusy(true);
    setError(null);
    try {
      const rental = await api.post<RentalDetail>("/pos/rentals", {
        customer_id: member.customer_id,
        book_ids: picked.map((b) => b.book_id),
        expected_return: due,
        fee: Number(fee) || 0,
        payment_method: method,
      });
      toast(`${picked.length === 1 ? "Book" : `${picked.length} books`} lent to ${rental.customer_name}.`);
      onDone(rental);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal
      title="Lend books"
      onClose={onClose}
      wide
      footer={
        <>
          <button className="btn" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={submit} disabled={busy}>
            {busy ? "Lending…" : `Lend ${picked.length || ""} ${picked.length === 1 ? "book" : "books"}`}
          </button>
        </>
      }
    >
      {customers.loading || books.loading ? (
        <Loading />
      ) : (
        <div className="stack">
          <Field label="Borrower" hint="Only library members can borrow.">
            <CustomerPicker
              customers={customers.data ?? []}
              value={member}
              onChange={setMember}
              onCreated={(c) => customers.setData([...(customers.data ?? []), c])}
              membersOnly
              placeholder="Member name or phone"
            />
          </Field>

          <div className="field">
            <span className="field-label">Books</span>
            <div className="picker">
              <input type="search" placeholder="Search title, author or ISBN" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Find a book to lend" />
              {matches.length > 0 && (
                <ul className="picker-list picker-inline">
                  {matches.map((b) => (
                    <li key={b.book_id}>
                      <button
                        type="button"
                        disabled={b.library_stock < 1}
                        onClick={() => {
                          setPicked((p) => [...p, b]);
                          setQuery("");
                        }}
                      >
                        <span className="book-title">{b.title}</span>
                        <span className={b.library_stock < 1 ? "small text-red" : "muted small"}>
                          {b.library_stock < 1 ? "All copies out" : `${b.library_stock} on the shelf`}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            {picked.length > 0 && (
              <ul className="picked-books">
                {picked.map((b) => (
                  <li key={b.book_id}>
                    <span>
                      <span className="book-title">{b.title}</span> <span className="muted small">{b.author}</span>
                    </span>
                    <button className="link" onClick={() => setPicked((p) => p.filter((x) => x.book_id !== b.book_id))}>
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="row-fields">
            <Field label="Return by">
              <input type="date" value={due} min={addDays(0)} onChange={(e) => setDue(e.target.value)} />
            </Field>
            <div className="quick-dates">
              {[7, 14, 21].map((d) => (
                <button key={d} type="button" className={due === addDays(d) ? "chip chip-on" : "chip"} onClick={() => setDue(addDays(d))}>
                  {d} days
                </button>
              ))}
            </div>
          </div>

          <div className="row-fields">
            <Field label="Loan fee (RWF)" hint="Leave at 0 if lending is free.">
              <input inputMode="numeric" value={fee} onChange={(e) => setFee(e.target.value.replace(/[^\d]/g, ""))} />
            </Field>
            {Number(fee) > 0 && (
              <Field label="Paid by">
                <select value={method} onChange={(e) => setMethod(e.target.value as PaymentMethod)}>
                  {PAYMENT_METHODS.map((m) => (
                    <option key={m.value} value={m.value}>
                      {m.label}
                    </option>
                  ))}
                </select>
              </Field>
            )}
          </div>

          {error && <div className="error-note" role="alert">{error}</div>}
        </div>
      )}
    </Modal>
  );
}

function LoanModal({ rentalId, onClose, onChanged }: { rentalId: number; onClose: () => void; onChanged: () => void }) {
  const { data: rental, error, loading, setData } = useApi<RentalDetail>(`/pos/rentals/${rentalId}`);
  const toast = useToast();
  const [lateFee, setLateFee] = useState<string | null>(null);
  const [method, setMethod] = useState<PaymentMethod>("cash");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const fee = lateFee ?? String(rental?.suggested_late_fee ?? 0);

  async function checkIn() {
    setBusy(true);
    setErr(null);
    try {
      const updated = await api.post<RentalDetail>(`/pos/rentals/${rentalId}/return`, {
        late_fee: Number(fee) || 0,
        payment_method: method,
      });
      setData(updated);
      toast(`Checked in. ${updated.books.length === 1 ? "The book is" : "The books are"} back on the shelf.`);
      onChanged();
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const open = rental && rental.status !== "returned";

  return (
    <Modal
      title={open ? "Check in loan" : "Loan slip"}
      onClose={onClose}
      footer={
        rental && (
          <>
            <button className="btn" onClick={() => window.print()}>
              Print slip
            </button>
            {open ? (
              <button className="btn btn-primary" onClick={checkIn} disabled={busy}>
                {busy ? "Checking in…" : Number(fee) > 0 ? `Check in and charge ${money(Number(fee))}` : "Check in"}
              </button>
            ) : (
              <button className="btn btn-primary" onClick={onClose}>
                Done
              </button>
            )}
          </>
        )
      }
    >
      {loading && !rental ? (
        <Loading />
      ) : error || !rental ? (
        <ErrorNote message={error ?? "Not found"} />
      ) : (
        <div className="stack">
          {open && rental.days_overdue > 0 && (
            <div className="late-box">
              <p>
                <strong>{rental.days_overdue} {rental.days_overdue === 1 ? "day" : "days"} late</strong> (due {day(rental.expected_return)}).
                At {money(rental.late_fee_per_day)} a day, the late fee is {money(rental.suggested_late_fee)}.
              </p>
              <div className="row-fields">
                <Field label="Late fee to charge (RWF)" hint="Set to 0 to waive it.">
                  <input inputMode="numeric" value={fee} onChange={(e) => setLateFee(e.target.value.replace(/[^\d]/g, ""))} />
                </Field>
                {Number(fee) > 0 && (
                  <Field label="Paid by">
                    <select value={method} onChange={(e) => setMethod(e.target.value as PaymentMethod)}>
                      {PAYMENT_METHODS.map((m) => (
                        <option key={m.value} value={m.value}>
                          {m.label}
                        </option>
                      ))}
                    </select>
                  </Field>
                )}
              </div>
            </div>
          )}
          {err && <div className="error-note" role="alert">{err}</div>}
          <LoanSlip rental={rental} />
        </div>
      )}
    </Modal>
  );
}
