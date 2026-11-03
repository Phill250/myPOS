import { Link } from "react-router";
import { useApi } from "../lib/hooks";
import type { Dashboard, RentalSummary } from "../lib/types";
import { day, methodLabel, money, num, shortDay } from "../lib/format";
import { DueStamp, Empty, ErrorNote, Loading, PageHead } from "../components/ui";

export function DashboardPage() {
  const { data, error, loading, reload } = useApi<Dashboard>("/pos/dashboard");
  const overdue = useApi<RentalSummary[]>("/pos/rentals?status=overdue&limit=6");

  const todayLabel = new Date().toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  if (loading && !data) return <Loading />;
  if (error || !data) return <ErrorNote message={error ?? "No data"} onRetry={reload} />;

  const t = data.today;
  const maxRevenue = Math.max(1, ...data.last_7_days.map((d) => d.revenue));
  const weekTotal = data.last_7_days.reduce((s, d) => s + d.revenue, 0);

  return (
    <>
      <PageHead
        title={todayLabel}
        actions={
          <>
            <Link to="/library" className="btn">Lend books</Link>
            <Link to="/till" className="btn btn-primary">New sale</Link>
          </>
        }
      />

      <section className="daysheet" aria-label="Today so far">
        <div className="daysheet-main">
          <span className="daysheet-label">Taken at the till today</span>
          <span className="daysheet-figure">{num(t.sales_revenue)}<small> RWF</small></span>
          <span className="muted">
            {t.sales_count} {t.sales_count === 1 ? "sale" : "sales"}, {t.items_sold}{" "}
            {t.items_sold === 1 ? "book" : "books"} sold
          </span>
        </div>
        <dl className="daysheet-facts">
          <div>
            <dt>Library income</dt>
            <dd>{money(t.library_income)}</dd>
          </div>
          <div>
            <dt>Loans issued</dt>
            <dd>{t.loans_out}</dd>
          </div>
          <div>
            <dt>Books returned</dt>
            <dd>{t.returns}</dd>
          </div>
          <div>
            <dt>Out on loan</dt>
            <dd>
              {data.active_loans + data.overdue_loans}
              {data.overdue_loans > 0 && <span className="text-red"> ({data.overdue_loans} late)</span>}
            </dd>
          </div>
        </dl>
      </section>

      <div className="grid-2">
        <section className="panel">
          <div className="panel-head">
            <h2>Last 7 days</h2>
            <span className="muted">{money(weekTotal)}</span>
          </div>
          <div className="bars" role="img" aria-label="Sales revenue for each of the last seven days">
            {data.last_7_days.map((d, i) => {
              const isToday = i === data.last_7_days.length - 1;
              return (
                <div className="bar-col" key={d.date} title={`${day(d.date)}: ${money(d.revenue)}`}>
                  <span className="bar-val">{d.revenue ? num(d.revenue / 1000) + "k" : ""}</span>
                  <span
                    className={isToday ? "bar bar-today" : "bar"}
                    style={{ height: `${Math.max(2, (d.revenue / maxRevenue) * 100)}%` }}
                  />
                  <span className="bar-day">{isToday ? "Today" : shortDay(d.date)}</span>
                </div>
              );
            })}
          </div>
          {data.payment_methods_today.length > 0 && (
            <div className="methods">
              <h3>Paid today by</h3>
              <ul className="kv">
                {data.payment_methods_today.map((m) => (
                  <li key={m.method}>
                    <span>{methodLabel(m.method)}</span>
                    <span className="num">{money(m.amount)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Overdue loans</h2>
            <Link to="/library" className="link">All loans</Link>
          </div>
          {overdue.loading && !overdue.data ? (
            <Loading />
          ) : !overdue.data?.length ? (
            <Empty>Nothing overdue. Every borrowed book is within its due date.</Empty>
          ) : (
            <ul className="loan-list">
              {overdue.data.map((r) => (
                <li key={r.rental_id}>
                  <div>
                    <div className="strong">{r.customer_name}</div>
                    <div className="muted small">
                      {r.books.map((b) => b.title).join(", ")}, {r.customer_phone}
                    </div>
                  </div>
                  <DueStamp date={r.expected_return} status={r.status} />
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Running low</h2>
            <Link to="/books" className="link">Books</Link>
          </div>
          {data.low_stock.length === 0 ? (
            <Empty>Every title has enough copies for sale.</Empty>
          ) : (
            <ul className="kv">
              {data.low_stock.map((b) => (
                <li key={b.book_id}>
                  <span>
                    <span className="book-title">{b.title}</span>
                    <span className="muted small"> {b.author}</span>
                  </span>
                  <span className={b.retail_stock === 0 ? "text-red num" : "num"}>
                    {b.retail_stock === 0 ? "Sold out" : `${b.retail_stock} left`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel">
          <div className="panel-head">
            <h2>Best sellers, 30 days</h2>
          </div>
          {data.top_books_30_days.length === 0 ? (
            <Empty>No sales in the last 30 days yet.</Empty>
          ) : (
            <ol className="ranked">
              {data.top_books_30_days.map((b) => (
                <li key={b.book_id}>
                  <span className="book-title">{b.title}</span>
                  <span className="muted num">
                    {b.quantity} sold, {money(b.revenue)}
                  </span>
                </li>
              ))}
            </ol>
          )}
          <p className="muted small catalog-note">
            {data.total_titles} titles in the catalogue, {data.total_customers} customers, {data.library_members} of them library members.
          </p>
        </section>
      </div>
    </>
  );
}
