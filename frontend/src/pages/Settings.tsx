import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useApi } from "../lib/hooks";
import type { Category, Supplier } from "../lib/types";
import { ConfirmModal, Modal } from "../components/Modal";
import { useToast } from "../components/Toast";
import { Empty, ErrorNote, Field, Loading, PageHead } from "../components/ui";

export function SettingsPage() {
  return (
    <>
      <PageHead title="Categories & suppliers" sub="Every book belongs to one category and comes from one supplier." />
      <div className="grid-2">
        <CategoriesPanel />
        <SuppliersPanel />
      </div>
    </>
  );
}

const inUseMessage = (what: string) => `This ${what} still has books, so it can't be deleted. Move those books first.`;

function CategoriesPanel() {
  const list = useApi<Category[]>("/categories/");
  const toast = useToast();
  const [editing, setEditing] = useState<Category | "new" | null>(null);
  const [deleting, setDeleting] = useState<Category | null>(null);

  async function remove() {
    if (!deleting) return;
    try {
      await api.del(`/categories/${deleting.category_id}`);
      toast(`Deleted ${deleting.category_name}.`);
      list.reload();
    } catch (e) {
      toast(e instanceof Error && e.message.includes("still used") ? inUseMessage("category") : String(e), "error");
    }
    setDeleting(null);
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Categories</h2>
        <button className="btn btn-small" onClick={() => setEditing("new")}>Add category</button>
      </div>
      {list.error ? (
        <ErrorNote message={list.error} onRetry={list.reload} />
      ) : list.loading ? (
        <Loading />
      ) : !list.data?.length ? (
        <Empty>No categories yet.</Empty>
      ) : (
        <ul className="kv kv-actions">
          {list.data.map((c) => (
            <li key={c.category_id}>
              <span>
                <span className="strong">{c.category_name}</span>
                {c.description && <span className="muted small block">{c.description}</span>}
              </span>
              <span className="nowrap">
                <button className="btn btn-small" onClick={() => setEditing(c)}>Edit</button>{" "}
                <button className="btn btn-small btn-quiet" onClick={() => setDeleting(c)}>Delete</button>
              </span>
            </li>
          ))}
        </ul>
      )}
      {editing && (
        <SimpleForm
          title={editing === "new" ? "Add category" : "Edit category"}
          fields={[
            { key: "category_name", label: "Name", required: true },
            { key: "description", label: "Description" },
          ]}
          initial={editing === "new" ? {} : { category_name: editing.category_name, description: editing.description ?? "" }}
          onClose={() => setEditing(null)}
          onSubmit={async (v) => {
            const body = { category_name: v.category_name, description: v.description || null };
            if (editing === "new") await api.post("/categories/", body);
            else await api.put(`/categories/${editing.category_id}`, body);
            toast(`Saved ${v.category_name}.`);
            setEditing(null);
            list.reload();
          }}
        />
      )}
      {deleting && (
        <ConfirmModal title="Delete category?" message={`“${deleting.category_name}” will be removed.`} confirmLabel="Delete category" onConfirm={remove} onClose={() => setDeleting(null)} />
      )}
    </section>
  );
}

function SuppliersPanel() {
  const list = useApi<Supplier[]>("/suppliers/");
  const toast = useToast();
  const [editing, setEditing] = useState<Supplier | "new" | null>(null);
  const [deleting, setDeleting] = useState<Supplier | null>(null);

  async function remove() {
    if (!deleting) return;
    try {
      await api.del(`/suppliers/${deleting.supplier_id}`);
      toast(`Deleted ${deleting.company_name}.`);
      list.reload();
    } catch (e) {
      toast(e instanceof Error && e.message.includes("still used") ? inUseMessage("supplier") : String(e), "error");
    }
    setDeleting(null);
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Suppliers</h2>
        <button className="btn btn-small" onClick={() => setEditing("new")}>Add supplier</button>
      </div>
      {list.error ? (
        <ErrorNote message={list.error} onRetry={list.reload} />
      ) : list.loading ? (
        <Loading />
      ) : !list.data?.length ? (
        <Empty>No suppliers yet.</Empty>
      ) : (
        <ul className="kv kv-actions">
          {list.data.map((s) => (
            <li key={s.supplier_id}>
              <span>
                <span className="strong">{s.company_name}</span>
                <span className="muted small block num">{s.phone_number}</span>
              </span>
              <span className="nowrap">
                <button className="btn btn-small" onClick={() => setEditing(s)}>Edit</button>{" "}
                <button className="btn btn-small btn-quiet" onClick={() => setDeleting(s)}>Delete</button>
              </span>
            </li>
          ))}
        </ul>
      )}
      {editing && (
        <SimpleForm
          title={editing === "new" ? "Add supplier" : "Edit supplier"}
          fields={[
            { key: "company_name", label: "Company name", required: true },
            { key: "phone_number", label: "Phone", required: true, type: "tel" },
          ]}
          initial={editing === "new" ? {} : { company_name: editing.company_name, phone_number: editing.phone_number }}
          onClose={() => setEditing(null)}
          onSubmit={async (v) => {
            if (editing === "new") await api.post("/suppliers/", v);
            else await api.put(`/suppliers/${editing.supplier_id}`, v);
            toast(`Saved ${v.company_name}.`);
            setEditing(null);
            list.reload();
          }}
        />
      )}
      {deleting && (
        <ConfirmModal title="Delete supplier?" message={`“${deleting.company_name}” will be removed.`} confirmLabel="Delete supplier" onConfirm={remove} onClose={() => setDeleting(null)} />
      )}
    </section>
  );
}

function SimpleForm({
  title,
  fields,
  initial,
  onSubmit,
  onClose,
}: {
  title: string;
  fields: { key: string; label: string; required?: boolean; type?: string }[];
  initial: Record<string, string>;
  onSubmit: (values: Record<string, string>) => Promise<void>;
  onClose: () => void;
}) {
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(fields.map((f) => [f.key, initial[f.key] ?? ""])),
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await onSubmit(Object.fromEntries(Object.entries(values).map(([k, v]) => [k, v.trim()])));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      setBusy(false);
    }
  }

  return (
    <Modal title={title} onClose={onClose}>
      <form onSubmit={submit} className="stack">
        {fields.map((f, i) => (
          <Field key={f.key} label={f.label}>
            <input
              type={f.type ?? "text"}
              value={values[f.key]}
              onChange={(e) => setValues({ ...values, [f.key]: e.target.value })}
              required={f.required}
              autoFocus={i === 0}
            />
          </Field>
        ))}
        {error && <div className="error-note" role="alert">{error}</div>}
        <div className="form-actions">
          <button type="button" className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Save"}</button>
        </div>
      </form>
    </Modal>
  );
}
