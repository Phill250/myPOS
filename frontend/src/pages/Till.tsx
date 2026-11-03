import { useMemo, useRef, useState, type KeyboardEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { Book, Category, Customer, PaymentMethod, SaleDetail } from "../lib/types";
import { PAYMENT_METHODS, money, num } from "../lib/format";
import { CustomerPicker } from "../components/CustomerPicker";
import { Modal } from "../components/Modal";
import { SaleReceipt } from "../components/Receipt";
import { useToast } from "../components/Toast";
import { ErrorNote, Loading } from "../components/ui";

interface Line {
  book: Book;
  qty: number;
}

export function TillPage() {
  const books = useApi<Book[]>("/books/");
  const categories = useApi<Category[]>("/categories/");
  const customers = useApi<Customer[]>("/customers/");
  const toast = useToast();

  const [query, setQuery] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [lines, setLines] = useState<Line[]>([]);
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [method, setMethod] = useState<PaymentMethod>("cash");
  const [tendered, setTendered] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [receipt, setReceipt] = useState<SaleDetail | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (books.data ?? [])
      .filter((b) => categoryId === null || b.category_id === categoryId)
      .filter(
        (b) =>
          !q ||
          b.title.toLowerCase().includes(q) ||
          b.author.toLowerCase().includes(q) ||
          (b.isbn ?? "").replace(/-/g, "").includes(q.replace(/-/g, "")),
      )
      .sort((a, b) => a.title.localeCompare(b.title));
  }, [books.data, query, categoryId]);

  const inCart = (bookId: number) => lines.find((l) => l.book.book_id === bookId)?.qty ?? 0;
  const total = lines.reduce((s, l) => s + Math.round(Number(l.book.sale_price) * l.qty), 0);
  const count = lines.reduce((s, l) => s + l.qty, 0);
  const tenderedNum = Number(tendered.replace(/[^\d]/g, "")) || 0;
  const change = tenderedNum - total;

  function add(book: Book) {
    if (inCart(book.book_id) >= book.retail_stock) {
      toast(`Only ${book.retail_stock} ${book.retail_stock === 1 ? "copy" : "copies"} of “${book.title}” in stock.`, "error");
      return;
    }
    setError(null);
    setLines((ls) => {
      const found = ls.find((l) => l.book.book_id === book.book_id);
      if (found) return ls.map((l) => (l === found ? { ...l, qty: l.qty + 1 } : l));
      return [...ls, { book, qty: 1 }];
    });
  }

  function setQty(bookId: number, qty: number) {
    setLines((ls) =>
      ls
        .map((l) => (l.book.book_id === bookId ? { ...l, qty: Math.min(qty, l.book.retail_stock) } : l))
        .filter((l) => l.qty > 0),
    );
  }

  // A barcode scanner types the ISBN and presses Enter.
  function onSearchKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key !== "Enter") return;
    const q = query.trim().replace(/-/g, "");
    const exact = (books.data ?? []).find((b) => b.isbn && b.isbn.replace(/-/g, "") === q);
    const target = exact ?? (results.length === 1 ? results[0] : null);
    if (target) {
      add(target);
      setQuery("");
    }
  }

  function reset() {
    setLines([]);
    setCustomer(null);
    setMethod("cash");
    setTendered("");
    setError(null);
    setReceipt(null);
    searchRef.current?.focus();
  }

  async function charge() {
    setBusy(true);
    setError(null);
    try {
      const sale = await api.post<SaleDetail>("/pos/sales", {
        customer_id: customer?.customer_id ?? null,
        items: lines.map((l) => ({ book_id: l.book.book_id, quantity: l.qty })),
        payment_method: method,
      });
      setReceipt(sale);
      books.reload(); // fresh stock numbers
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      books.reload();
    } finally {
      setBusy(false);
    }
  }

  if (books.loading && !books.data) return <Loading />;
  if (books.error) return <ErrorNote message={books.error} onRetry={books.reload} />;

  const cashShort = method === "cash" && tendered !== "" && change < 0;

  return (
    <div className="till">
      <section className="till-catalog" aria-label="Find books">
        <div className="till-search">
          <input
            ref={searchRef}
            type="search"
            placeholder="Search title, author or scan ISBN"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onSearchKey}
            autoFocus
            aria-label="Search books"
          />
        </div>
        <div className="chips" role="group" aria-label="Filter by category">
          <button className={categoryId === null ? "chip chip-on" : "chip"} onClick={() => setCategoryId(null)}>
            All
          </button>
          {(categories.data ?? []).map((c) => (
            <button
              key={c.category_id}
              className={categoryId === c.category_id ? "chip chip-on" : "chip"}
              onClick={() => setCategoryId(c.category_id)}
            >
              {c.category_name}
            </button>
          ))}
        </div>

        <ul className="shelf-list">
          {results.map((b) => {
            const left = b.retail_stock - inCart(b.book_id);
            return (
              <li key={b.book_id}>
                <button className="shelf-item" onClick={() => add(b)} disabled={left <= 0}>
                  <span className="shelf-text">
                    <span className="book-title">{b.title}</span>
                    <span className="muted small">{b.author}</span>
                  </span>
                  <span className="shelf-side">
                    <span className="price">{num(b.sale_price)}</span>
                    <span className={left <= 0 ? "small text-red" : left <= 3 ? "small text-brass" : "small muted"}>
                      {left <= 0 ? (b.retail_stock === 0 ? "Sold out" : "All in basket") : `${left} in stock`}
                    </span>
                  </span>
                </button>
              </li>
            );
          })}
          {results.length === 0 && <li className="muted pad">No book matches “{query}”.</li>}
        </ul>
      </section>

      <section className="ticket" aria-label="Current sale">
        <div className="ticket-paper">
          <div className="ticket-head">
            <h2>Current sale</h2>
            {lines.length > 0 && (
              <button className="link" onClick={reset}>
                Clear
              </button>
            )}
          </div>

          <div className="ticket-customer">
            {customers.data ? (
              <CustomerPicker
                customers={customers.data}
                value={customer}
                onChange={setCustomer}
                onCreated={(c) => customers.setData([...(customers.data ?? []), c])}
                placeholder="Customer (optional): name or phone"
              />
            ) : (
              <span className="muted small">Loading customers…</span>
            )}
          </div>

          {lines.length === 0 ? (
            <p className="ticket-empty">Tap a book to add it, or scan its barcode.</p>
          ) : (
            <ul className="ticket-lines">
              {lines.map((l) => (
                <li key={l.book.book_id}>
                  <div className="tl-main">
                    <span className="book-title">{l.book.title}</span>
                    <span className="muted small">{num(l.book.sale_price)} each</span>
                  </div>
                  <div className="qty">
                    <button aria-label={`One fewer ${l.book.title}`} onClick={() => setQty(l.book.book_id, l.qty - 1)}>
                      −
                    </button>
                    <span aria-live="polite">{l.qty}</span>
                    <button
                      aria-label={`One more ${l.book.title}`}
                      onClick={() => setQty(l.book.book_id, l.qty + 1)}
                      disabled={l.qty >= l.book.retail_stock}
                    >
                      +
                    </button>
                  </div>
                  <span className="tl-amt num">{num(Math.round(Number(l.book.sale_price) * l.qty))}</span>
                </li>
              ))}
            </ul>
          )}

          <div className="ticket-total">
            <span>
              Total <span className="muted small">({count} {count === 1 ? "book" : "books"})</span>
            </span>
            <span className="total-figure">{money(total)}</span>
          </div>

          <fieldset className="methods-pick">
            <legend>Payment</legend>
            {PAYMENT_METHODS.map((m) => (
              <label key={m.value} className={method === m.value ? "seg seg-on" : "seg"}>
                <input type="radio" name="method" value={m.value} checked={method === m.value} onChange={() => setMethod(m.value)} />
                {m.label}
              </label>
            ))}
          </fieldset>

          {method === "cash" && lines.length > 0 && (
            <div className="cash">
              <label className="field">
                <span className="field-label">Cash received</span>
                <input inputMode="numeric" placeholder={num(total)} value={tendered} onChange={(e) => setTendered(e.target.value)} />
              </label>
              <div className="cash-change">
                <span className="field-label">Change</span>
                <span className={cashShort ? "text-red num strong" : "num strong"}>
                  {tendered === "" ? "—" : cashShort ? `${num(-change)} short` : money(change)}
                </span>
              </div>
            </div>
          )}

          {error && <div className="error-note" role="alert">{error}</div>}

          <button className="btn btn-primary btn-big btn-block" disabled={lines.length === 0 || busy || cashShort} onClick={charge}>
            {busy ? "Recording sale…" : lines.length ? `Charge ${money(total)}` : "Add books to charge"}
          </button>
        </div>
      </section>

      {receipt && (
        <Modal
          title="Sale recorded"
          onClose={reset}
          footer={
            <>
              <button className="btn" onClick={() => window.print()}>
                Print receipt
              </button>
              <button className="btn btn-primary" onClick={reset} autoFocus>
                Start next sale
              </button>
            </>
          }
        >
          {method === "cash" && tenderedNum > 0 && change >= 0 && (
            <p className="change-callout">
              Give <strong>{money(change)}</strong> change
            </p>
          )}
          <SaleReceipt sale={receipt} />
        </Modal>
      )}
    </div>
  );
}
