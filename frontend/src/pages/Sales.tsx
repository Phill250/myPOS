import { useMemo, useState } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { SaleDetail, SaleSummary } from "../lib/types";
import { dateTime, methodLabel, money } from "../lib/format";
import { ConfirmModal, Modal } from "../components/Modal";
import { SaleReceipt } from "../components/Receipt";
import { useToast } from "../components/Toast";
import { Empty, ErrorNote, Loading, PageHead } from "../components/ui";

type Range = "today" | "week" | "all";

function since(range: Range): number {
  if (range === "all") return 0;
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  if (range === "week") d.setDate(d.getDate() - 6);
  return d.getTime();
}

const ts = (s: string) => new Date(/[zZ]|[+-]\d{2}:?\d{2}$/.test(s) ? s : `${s}Z`).getTime();

export function SalesPage() {
  const sales = useApi<SaleSummary[]>("/pos/sales?limit=1000");
  const [range, setRange] = useState<Range>("today");
  const [query, setQuery] = useState("");
  const [openId, setOpenId] = useState<number | null>(null);

  const shown = useMemo(() => {
    const from = since(range);
    const q = query.trim().toLowerCase();
    return (sales.data ?? [])
      .filter((s) => ts(s.sale_timestamp) >= from)
      .filter(
        (s) =>
          !q ||
          (s.receipt_number ?? "").toLowerCase().includes(q) ||
          (s.customer_name ?? "").toLowerCase().includes(q) ||
          (s.cashier ?? "").toLowerCase().includes(q),
      );
  }, [sales.data, range, query]);

  const total = shown.reduce((s, x) => s + x.total_amount, 0);

  return (
    <>
      <PageHead title="Sales history" sub={`${shown.length} ${shown.length === 1 ? "sale" : "sales"}, ${money(total)}`} />

      <div className="toolbar">
        <div className="tabs" role="tablist">
          {(
            [
              ["today", "Today"],
              ["week", "Last 7 days"],
              ["all", "All"],
            ] as [Range, string][]
          ).map(([v, label]) => (
            <button key={v} role="tab" aria-selected={range === v} className={range === v ? "tab tab-on" : "tab"} onClick={() => setRange(v)}>
              {label}
            </button>
          ))}
        </div>
        <input type="search" className="toolbar-search" placeholder="Receipt number, customer or cashier" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search sales" />
      </div>

      {sales.error ? (
        <ErrorNote message={sales.error} onRetry={sales.reload} />
      ) : sales.loading && !sales.data ? (
        <Loading />
      ) : shown.length === 0 ? (
        <Empty>{range === "today" ? "No sales yet today." : "No sales match."}</Empty>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>When</th>
                <th>Receipt</th>
                <th>Customer</th>
                <th>Served by</th>
                <th>Paid by</th>
                <th className="right">Books</th>
                <th className="right">Total</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((s) => (
                <tr key={s.sale_id} className="row-click" onClick={() => setOpenId(s.sale_id)}>
                  <td className="nowrap">{dateTime(s.sale_timestamp)}</td>
                  <td className="num small">{s.receipt_number}</td>
                  <td>{s.customer_name ?? <span className="muted">Walk-in</span>}</td>
                  <td className="muted">{s.cashier}</td>
                  <td>{methodLabel(s.payment_method)}</td>
                  <td className="right num">{s.item_count}</td>
                  <td className="right num strong">{money(s.total_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {openId !== null && (
        <SaleModal
          saleId={openId}
          onClose={() => setOpenId(null)}
          onVoided={() => {
            setOpenId(null);
            sales.reload();
          }}
        />
      )}
    </>
  );
}

export function SaleModal({ saleId, onClose, onVoided }: { saleId: number; onClose: () => void; onVoided?: () => void }) {
  const { data, error, loading } = useApi<SaleDetail>(`/pos/sales/${saleId}`);
  const toast = useToast();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  async function voidSale() {
    setBusy(true);
    try {
      await api.del(`/sales/${saleId}`);
      toast("Sale voided. The books are back in stock.");
      onVoided?.();
    } catch (e) {
      toast(e instanceof Error ? e.message : String(e), "error");
      setConfirming(false);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Modal
        title="Receipt"
        onClose={onClose}
        footer={
          <>
            {onVoided && (
              <button className="btn btn-quiet" onClick={() => setConfirming(true)}>
                Void sale
              </button>
            )}
            <button className="btn" onClick={() => window.print()} disabled={!data}>
              Print receipt
            </button>
            <button className="btn btn-primary" onClick={onClose}>
              Done
            </button>
          </>
        }
      >
        {loading ? <Loading /> : error || !data ? <ErrorNote message={error ?? "Not found"} /> : <SaleReceipt sale={data} />}
      </Modal>
      {confirming && data && (
        <ConfirmModal
          title="Void this sale?"
          message={
            <>
              Receipt {data.receipt_number} for {money(data.total_amount)} will be deleted and its {data.item_count}{" "}
              {data.item_count === 1 ? "book goes" : "books go"} back into stock. Refund the customer yourself.
            </>
          }
          confirmLabel="Void sale"
          busy={busy}
          onConfirm={voidSale}
          onClose={() => setConfirming(false)}
        />
      )}
    </>
  );
}
