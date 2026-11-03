import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useApi } from "../lib/hooks";
import type { RentalSummary, SaleSummary } from "../lib/types";
import { dateTime, money } from "../lib/format";
import { DueStamp, Empty, Loading, PageHead } from "../components/ui";
import { SaleModal } from "./Sales";

/** What a signed-in customer sees: their loans and their receipts. */
export function AccountPage() {
  const { user } = useAuth();
  const profile = user?.customer_profile;
  const loans = useApi<RentalSummary[]>(profile ? "/pos/rentals" : null);
  const sales = useApi<SaleSummary[]>(profile ? "/pos/sales" : null);
  const [openSale, setOpenSale] = useState<number | null>(null);

  if (!profile) {
    return (
      <>
        <PageHead title={`Welcome, ${user?.username}`} />
        <div className="note note-big">
          <p>
            Your account isn't linked to a library card yet. Next time you're at Charisma Library, give the front desk your
            username, <strong>{user?.username}</strong>, and they'll connect it. Your loans and receipts will then show up here.
          </p>
        </div>
      </>
    );
  }

  const out = (loans.data ?? []).filter((r) => r.status !== "returned");
  const past = (loans.data ?? []).filter((r) => r.status === "returned");

  return (
    <>
      <PageHead
        title={`Hello, ${profile.first_name}`}
        sub={profile.library_member ? "Library member" : "Become a library member at the front desk to borrow books."}
      />

      <section className="panel">
        <div className="panel-head">
          <h2>Books you have out</h2>
        </div>
        {loans.loading ? (
          <Loading />
        ) : out.length === 0 ? (
          <Empty>You have no books out right now.</Empty>
        ) : (
          <ul className="loan-list">
            {out.map((r) => (
              <li key={r.rental_id}>
                <div>
                  {r.books.map((b) => (
                    <div key={b.rental_item_id}>
                      <span className="book-title">{b.title}</span> <span className="muted small">{b.author}</span>
                    </div>
                  ))}
                  {r.status === "overdue" && (
                    <div className="small text-red">
                      {r.days_overdue} {r.days_overdue === 1 ? "day" : "days"} late. Late fees apply.
                    </div>
                  )}
                </div>
                <DueStamp date={r.expected_return} status={r.status} />
              </li>
            ))}
          </ul>
        )}
      </section>

      <div className="grid-2">
        <section className="panel">
          <div className="panel-head">
            <h2>Your receipts</h2>
          </div>
          {sales.loading ? (
            <Loading />
          ) : !sales.data?.length ? (
            <Empty>No purchases yet.</Empty>
          ) : (
            <ul className="kv">
              {sales.data.map((s) => (
                <li key={s.sale_id}>
                  <button className="link-row" onClick={() => setOpenSale(s.sale_id)}>
                    <span>
                      {dateTime(s.sale_timestamp)}{" "}
                      <span className="muted small">
                        ({s.item_count} {s.item_count === 1 ? "book" : "books"})
                      </span>
                    </span>
                    <span className="num">{money(s.total_amount)}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="panel">
          <div className="panel-head">
            <h2>Reading history</h2>
          </div>
          {loans.loading ? (
            <Loading />
          ) : past.length === 0 ? (
            <Empty>Books you return will be listed here.</Empty>
          ) : (
            <ul className="kv">
              {past.flatMap((r) =>
                r.books.map((b) => (
                  <li key={b.rental_item_id}>
                    <span className="book-title">{b.title}</span>
                    <span className="muted small nowrap">{r.actual_return && new Date(r.actual_return).toLocaleDateString("en-GB", { month: "short", year: "numeric" })}</span>
                  </li>
                )),
              )}
            </ul>
          )}
        </section>
      </div>

      {openSale !== null && <SaleModal saleId={openSale} onClose={() => setOpenSale(null)} />}
    </>
  );
}
