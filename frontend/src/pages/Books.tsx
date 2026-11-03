import { useMemo, useState, type FormEvent } from "react";
import { Link } from "react-router";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { Book, Category, Supplier } from "../lib/types";
import { num } from "../lib/format";
import { ConfirmModal, Modal } from "../components/Modal";
import { useToast } from "../components/Toast";
import { Empty, ErrorNote, Field, Loading, PageHead, StockBadge } from "../components/ui";

export function BooksPage() {
  const books = useApi<Book[]>("/books/");
  const categories = useApi<Category[]>("/categories/");
  const suppliers = useApi<Supplier[]>("/suppliers/");
  const toast = useToast();

  const [query, setQuery] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [lowOnly, setLowOnly] = useState(false);
  const [editing, setEditing] = useState<Book | "new" | null>(null);
  const [deleting, setDeleting] = useState<Book | null>(null);
  const [busy, setBusy] = useState(false);

  const catName = (id: number) => categories.data?.find((c) => c.category_id === id)?.category_name ?? "—";

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (books.data ?? [])
      .filter((b) => !categoryId || b.category_id === Number(categoryId))
      .filter((b) => !lowOnly || b.retail_stock <= 3)
      .filter(
        (b) => !q || b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q) || (b.isbn ?? "").includes(q),
      )
      .sort((a, b) => a.title.localeCompare(b.title));
  }, [books.data, query, categoryId, lowOnly]);

  async function remove() {
    if (!deleting) return;
    setBusy(true);
    try {
      await api.del(`/books/${deleting.book_id}`);
      toast(`Deleted “${deleting.title}”.`);
      setDeleting(null);
      books.reload();
    } catch (e) {
      toast(
        e instanceof Error && e.message.includes("still used")
          ? `“${deleting.title}” has past sales or loans, so it can't be deleted. Set its stock to 0 instead.`
          : String(e instanceof Error ? e.message : e),
        "error",
      );
      setDeleting(null);
    } finally {
      setBusy(false);
    }
  }

  const noSetup = categories.data?.length === 0 || suppliers.data?.length === 0;

  return (
    <>
      <PageHead
        title="Books"
        sub={books.data ? `${books.data.length} titles` : undefined}
        actions={
          <button className="btn btn-primary" onClick={() => setEditing("new")} disabled={noSetup}>
            Add book
          </button>
        }
      />

      {noSetup && (
        <div className="note">
          Before adding books, create at least one category and one supplier in{" "}
          <Link to="/settings" className="link">Categories &amp; suppliers</Link>.
        </div>
      )}

      <div className="toolbar">
        <input type="search" className="toolbar-search" placeholder="Title, author or ISBN" value={query} onChange={(e) => setQuery(e.target.value)} aria-label="Search books" />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)} aria-label="Category">
          <option value="">All categories</option>
          {(categories.data ?? []).map((c) => (
            <option key={c.category_id} value={c.category_id}>
              {c.category_name}
            </option>
          ))}
        </select>
        <label className="check">
          <input type="checkbox" checked={lowOnly} onChange={(e) => setLowOnly(e.target.checked)} /> Low stock only
        </label>
      </div>

      {books.error ? (
        <ErrorNote message={books.error} onRetry={books.reload} />
      ) : books.loading && !books.data ? (
        <Loading />
      ) : shown.length === 0 ? (
        <Empty>{books.data?.length ? "No book matches these filters." : "No books yet. Add your first title."}</Empty>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Category</th>
                <th className="right">Price (RWF)</th>
                <th>Shop</th>
                <th>Library</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {shown.map((b) => (
                <tr key={b.book_id}>
                  <td>
                    <div className="book-title">{b.title}</div>
                    <div className="muted small">
                      {b.author}
                      {b.isbn ? `, ISBN ${b.isbn}` : ""}
                    </div>
                  </td>
                  <td className="muted">{catName(b.category_id)}</td>
                  <td className="right num">{num(b.sale_price)}</td>
                  <td><StockBadge count={b.retail_stock} kind="shop" /></td>
                  <td><StockBadge count={b.library_stock} kind="library" /></td>
                  <td className="right nowrap">
                    <button className="btn btn-small" onClick={() => setEditing(b)}>Edit</button>{" "}
                    <button className="btn btn-small btn-quiet" onClick={() => setDeleting(b)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <BookModal
          book={editing === "new" ? null : editing}
          categories={categories.data ?? []}
          suppliers={suppliers.data ?? []}
          onClose={() => setEditing(null)}
          onSaved={(b, isNew) => {
            setEditing(null);
            books.reload();
            toast(isNew ? `Added “${b.title}”.` : `Saved “${b.title}”.`);
          }}
        />
      )}
      {deleting && (
        <ConfirmModal
          title="Delete book?"
          message={<>“{deleting.title}” will be removed from the catalogue. This can't be undone.</>}
          confirmLabel="Delete book"
          busy={busy}
          onConfirm={remove}
          onClose={() => setDeleting(null)}
        />
      )}
    </>
  );
}

function BookModal({
  book,
  categories,
  suppliers,
  onClose,
  onSaved,
}: {
  book: Book | null;
  categories: Category[];
  suppliers: Supplier[];
  onClose: () => void;
  onSaved: (b: Book, isNew: boolean) => void;
}) {
  const [form, setForm] = useState({
    title: book?.title ?? "",
    author: book?.author ?? "",
    isbn: book?.isbn ?? "",
    sale_price: book ? String(Math.round(Number(book.sale_price))) : "",
    category_id: String(book?.category_id ?? categories[0]?.category_id ?? ""),
    supplier_id: String(book?.supplier_id ?? suppliers[0]?.supplier_id ?? ""),
    retail_stock: String(book?.retail_stock ?? 0),
    library_stock: String(book?.library_stock ?? 0),
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) => setForm((f) => ({ ...f, [k]: e.target.value }));

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const body = {
      title: form.title.trim(),
      author: form.author.trim(),
      isbn: form.isbn.trim() || null,
      sale_price: Number(form.sale_price),
      category_id: Number(form.category_id),
      supplier_id: Number(form.supplier_id),
      retail_stock: Number(form.retail_stock),
      library_stock: Number(form.library_stock),
    };
    try {
      const saved = book ? await api.put<Book>(`/books/${book.book_id}`, body) : await api.post<Book>("/books/", body);
      onSaved(saved, !book);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title={book ? "Edit book" : "Add book"} onClose={onClose} wide>
      <form onSubmit={submit} className="stack">
        <Field label="Title">
          <input value={form.title} onChange={set("title")} required autoFocus />
        </Field>
        <div className="row-fields">
          <Field label="Author">
            <input value={form.author} onChange={set("author")} required />
          </Field>
          <Field label="ISBN" hint="Optional. Lets you scan the barcode at the till.">
            <input value={form.isbn} onChange={set("isbn")} />
          </Field>
        </div>
        <div className="row-fields">
          <Field label="Category">
            <select value={form.category_id} onChange={set("category_id")} required>
              {categories.map((c) => (
                <option key={c.category_id} value={c.category_id}>{c.category_name}</option>
              ))}
            </select>
          </Field>
          <Field label="Supplier">
            <select value={form.supplier_id} onChange={set("supplier_id")} required>
              {suppliers.map((s) => (
                <option key={s.supplier_id} value={s.supplier_id}>{s.company_name}</option>
              ))}
            </select>
          </Field>
        </div>
        <div className="row-fields row-3">
          <Field label="Price (RWF)">
            <input type="number" min={0} step={1} value={form.sale_price} onChange={set("sale_price")} required />
          </Field>
          <Field label="Copies for sale">
            <input type="number" min={0} step={1} value={form.retail_stock} onChange={set("retail_stock")} required />
          </Field>
          <Field label="Copies to lend">
            <input type="number" min={0} step={1} value={form.library_stock} onChange={set("library_stock")} required />
          </Field>
        </div>
        {error && <div className="error-note" role="alert">{error}</div>}
        <div className="form-actions">
          <button type="button" className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : book ? "Save changes" : "Add book"}</button>
        </div>
      </form>
    </Modal>
  );
}
