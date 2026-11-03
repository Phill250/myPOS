import type { RentalDetail, SaleDetail } from "../lib/types";
import { dateTime, day, methodLabel, money, num } from "../lib/format";

const SHOP = {
  name: "Charisma Library",
  line1: "Kigali, Rwanda",
};

function Head() {
  return (
    <div className="rc-head">
      <div className="rc-shop">{SHOP.name}</div>
      <div className="rc-muted">{SHOP.line1}</div>
    </div>
  );
}

export function SaleReceipt({ sale }: { sale: SaleDetail }) {
  return (
    <div className="receipt" id="printable">
      <Head />
      <dl className="rc-meta">
        <dt>Receipt</dt>
        <dd>{sale.receipt_number ?? `#${sale.sale_id}`}</dd>
        <dt>Date</dt>
        <dd>{dateTime(sale.sale_timestamp)}</dd>
        <dt>Served by</dt>
        <dd>{sale.cashier ?? "—"}</dd>
        {sale.customer_name && (
          <>
            <dt>Customer</dt>
            <dd>{sale.customer_name}</dd>
          </>
        )}
      </dl>
      <table className="rc-lines">
        <tbody>
          {sale.items.map((i) => (
            <tr key={i.sale_item_id}>
              <td>
                <div className="rc-title">{i.title}</div>
                <div className="rc-muted">
                  {i.quantity} × {num(i.unit_price)}
                </div>
              </td>
              <td className="rc-amt">{num(i.line_total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="rc-total">
        <span>Total</span>
        <span>{money(sale.total_amount)}</span>
      </div>
      <div className="rc-muted rc-center">Paid by {methodLabel(sale.payment_method)}</div>
      <div className="rc-foot">Thank you for reading with us.</div>
    </div>
  );
}

export function LoanSlip({ rental }: { rental: RentalDetail }) {
  const paid = rental.payments.reduce((sum, p) => sum + p.amount, 0);
  return (
    <div className="receipt" id="printable">
      <Head />
      <div className="rc-center rc-kind">Library loan slip</div>
      <dl className="rc-meta">
        <dt>Slip</dt>
        <dd>{rental.receipt_number ?? `#${rental.rental_id}`}</dd>
        <dt>Borrower</dt>
        <dd>{rental.customer_name}</dd>
        <dt>Issued</dt>
        <dd>{dateTime(rental.rental_timestamp)}</dd>
        <dt>Issued by</dt>
        <dd>{rental.staff ?? "—"}</dd>
      </dl>
      <ol className="rc-books">
        {rental.books.map((b) => (
          <li key={b.rental_item_id}>
            <span className="rc-title">{b.title}</span>
            <span className="rc-muted"> — {b.author}</span>
          </li>
        ))}
      </ol>
      <div className="rc-due">
        <span>Please return by</span>
        <strong>{day(rental.expected_return)}</strong>
      </div>
      {rental.actual_return && (
        <div className="rc-muted rc-center">Returned {day(rental.actual_return)}</div>
      )}
      {rental.payments.map((p) => (
        <div className="rc-row" key={p.payment_id}>
          <span>{p.transaction_type === "late_fee" ? "Late fee" : "Loan fee"}</span>
          <span>{money(p.amount)}</span>
        </div>
      ))}
      {paid > 0 && (
        <div className="rc-total">
          <span>Paid</span>
          <span>{money(paid)}</span>
        </div>
      )}
      <div className="rc-foot">
        Late returns cost {money(rental.late_fee_per_day)} per day.
      </div>
    </div>
  );
}
