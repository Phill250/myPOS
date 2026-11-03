import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { Customer, RentalSummary, SaleSummary, User } from "../lib/types";
import { dateTime, money } from "../lib/format";
import { ConfirmModal, Modal } from "../components/Modal";
import { useToast } from "../components/Toast";
import { DueStamp, Empty, ErrorNote, Field, Loading, PageHead } from "../components/ui";

export function CustomersPage() {
  const customers = useApi<Customer[]>("/customers/");
  const toast = useToast();
  const [query, setQuery] = useState("");
  const [membersOnly, setMembersOnly] = useState(false);
  const [editing, setEditing] = useState<Customer | "new" | null>(null);
  const [viewing, setViewing] = useState<Customer | null>(null);
  const [deleting, setDeleting] = useState<Customer | null>(null);
  const [busy, setBusy] = useState(false);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    const digits = q.replace(/\D/g, "");
    return (customers.data ?? [])
      .filter((c) => !membersOnly || c.library_member)
      .filter(
        (c) =>
          !q ||
          `${c.first_name} ${c.last_name}`.toLowerCase().includes(q) ||
          (c.email ?? "").toLowerCase().includes(q) ||
          (digits.length >= 3 && c.phone_number.replace(/\D/g, "").includes(digits)),
      )
      .sort((a, b) => `${a.first_name} ${a.last_name}`.localeCompare(`${b.first_name} ${b.last_name}`));
  }, [customers.data, query, membersOnly]);

  async function remove() {
    if (!deleting) return;
    setBusy(true);
    try {
      await api.del(`/customers/${deleting.customer_id}`);
      toast(`Deleted ${deleting.first_name} ${deleting.last_name}.`);
      customers.reload();
    } catch (e) {
      toast(
        e instanceof Error && e.message.includes("still used")
          ? "This customer has sales or loans on record, so they can't be deleted."
          : String(e instanceof Error ? e.message : e),
        "error",
      );
    } finally {
      setDeleting(null);
      setBusy(false);
    }
  }

  return (
    <>
      <PageHead
        title="Customers"
        sub={customers.data ? `${customers.data.length} customers, ${customers.data.filter((c) => c.library_member).length} library members` : undefined}
        actions={<button className="btn btn-primary" onClick={() => setEditing("new")}>Add customer</button>}
      />

      <div className="toolbar">
        <input type="search" className="toolbar-search" placeholder="Name, phone or email" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search customers" />
        <label className="check">
          <input type="checkbox" checked={membersOnly} onChange={(e) => setMembersOnly(e.target.checked)} /> Library members only
        </label>
      </div>

      {customers.error ? (
        <ErrorNote message={customers.error} onRetry={customers.reload} />
      ) : customers.loading && !customers.data ? (
        <Loading />
      ) : shown.length === 0 ? (
        <Empty>{customers.data?.length ? "No customer matches." : "No customers yet."}</Empty>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Library</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {shown.map((c) => (
                <tr key={c.customer_id} className="row-click" onClick={() => setViewing(c)}>
                  <td className="strong">
                    {c.first_name} {c.last_name}
                    {c.user_id && <span className="tag">Online account</span>}
                  </td>
                  <td className="num nowrap">{c.phone_number}</td>
                  <td className="muted">{c.email ?? "—"}</td>
                  <td>{c.library_member ? <span className="tag tag-green">Member</span> : <span className="muted">—</span>}</td>
                  <td className="right nowrap" onClick={(e) => e.stopPropagation()}>
                    <button className="btn btn-small" onClick={() => setEditing(c)}>Edit</button>{" "}
                    <button className="btn btn-small btn-quiet" onClick={() => setDeleting(c)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <Modal title={editing === "new" ? "Add customer" : "Edit customer"} onClose={() => setEditing(null)}>
          <CustomerForm
            customer={editing === "new" ? undefined : editing}
            onSaved={(c) => {
              setEditing(null);
              customers.reload();
              toast(`Saved ${c.first_name} ${c.last_name}.`);
            }}
            onCancel={() => setEditing(null)}
          />
        </Modal>
      )}
      {viewing && <CustomerHistory customer={viewing} onClose={() => setViewing(null)} />}
      {deleting && (
        <ConfirmModal
          title="Delete customer?"
          message={<>{deleting.first_name} {deleting.last_name} will be removed. This can't be undone.</>}
          confirmLabel="Delete customer"
          busy={busy}
          onConfirm={remove}
          onClose={() => setDeleting(null)}
        />
      )}
    </>
  );
}

export function CustomerForm({
  customer,
  initial,
  onSaved,
  onCancel,
}: {
  customer?: Customer;
  initial?: Partial<Customer>;
  onSaved: (c: Customer) => void;
  onCancel: () => void;
}) {
  const base = customer ?? initial ?? {};
  const [form, setForm] = useState({
    first_name: base.first_name ?? "",
    last_name: base.last_name ?? "",
    phone_number: base.phone_number ?? "",
    email: base.email ?? "",
    library_member: base.library_member ?? false,
  });
  const [username, setUsername] = useState("");
  const [linkLoaded, setLinkLoaded] = useState(!customer?.user_id);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // show which online account is linked, if any
  useEffect(() => {
    if (customer?.user_id) {
      api
        .get<User>(`/users/${customer.user_id}`)
        .then((u) => setUsername(u.username))
        .catch(() => {})
        .finally(() => setLinkLoaded(true));
    }
  }, [customer?.user_id]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      // until we know the linked username, keep whatever link exists
      let user_id: number | null = linkLoaded ? null : customer?.user_id ?? null;
      if (username.trim()) {
        const u = await api.get<User>(`/users/lookup?username=${encodeURIComponent(username.trim())}`);
        if (u.role !== "customer") throw new Error(`“${u.username}” is a staff account, not a customer account.`);
        user_id = u.user_id;
      }
      const body = {
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        phone_number: form.phone_number.trim(),
        email: form.email.trim() || null,
        library_member: form.library_member,
        user_id,
      };
      const saved = customer
        ? await api.put<Customer>(`/customers/${customer.customer_id}`, body)
        : await api.post<Customer>("/customers/", body);
      onSaved(saved);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg.includes("still used") ? "That online account is already linked to another customer." : msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="stack">
      <div className="row-fields">
        <Field label="First name">
          <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required autoFocus />
        </Field>
        <Field label="Last name">
          <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
        </Field>
      </div>
      <div className="row-fields">
        <Field label="Phone">
          <input type="tel" value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} placeholder="078…" required />
        </Field>
        <Field label="Email" hint="Optional">
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </Field>
      </div>
      <label className="check">
        <input type="checkbox" checked={form.library_member} onChange={(e) => setForm({ ...form, library_member: e.target.checked })} />
        Library member (can borrow books)
      </label>
      <Field label="Online account username" hint="Optional. Links the account they signed up with, so they can see their own receipts and loans.">
        <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="off" />
      </Field>
      {error && <div className="error-note" role="alert">{error}</div>}
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
        <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : customer ? "Save changes" : "Add customer"}</button>
      </div>
    </form>
  );
}

function CustomerHistory({ customer, onClose }: { customer: Customer; onClose: () => void }) {
  const sales = useApi<SaleSummary[]>(`/pos/sales?customer_id=${customer.customer_id}&limit=50`);
  const loans = useApi<RentalSummary[]>(`/pos/rentals?customer_id=${customer.customer_id}&limit=50`);
  const spent = (sales.data ?? []).reduce((s, x) => s + x.total_amount, 0);

  return (
    <Modal title={`${customer.first_name} ${customer.last_name}`} onClose={onClose} wide>
      <p className="muted">
        {customer.phone_number}
        {customer.email ? `, ${customer.email}` : ""}
        {customer.library_member ? ". Library member." : "."}
      </p>
      <div className="grid-2 grid-tight">
        <section>
          <h3>Purchases {sales.data && <span className="muted">({money(spent)} in total)</span>}</h3>
          {sales.loading ? (
            <Loading />
          ) : !sales.data?.length ? (
            <p className="muted">No purchases yet.</p>
          ) : (
            <ul className="kv">
              {sales.data.map((s) => (
                <li key={s.sale_id}>
                  <span>
                    {dateTime(s.sale_timestamp)} <span className="muted small">({s.item_count} {s.item_count === 1 ? "book" : "books"})</span>
                  </span>
                  <span className="num">{money(s.total_amount)}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section>
          <h3>Loans</h3>
          {loans.loading ? (
            <Loading />
          ) : !loans.data?.length ? (
            <p className="muted">No loans yet.</p>
          ) : (
            <ul className="loan-list">
              {loans.data.map((r) => (
                <li key={r.rental_id}>
                  <span className="small">{r.books.map((b) => b.title).join(", ")}</span>
                  <DueStamp date={r.actual_return ?? r.expected_return} status={r.status} />
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </Modal>
  );
}
