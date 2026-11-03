import { useState, type FormEvent } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useApi } from "../lib/hooks";
import type { Role, User } from "../lib/types";
import { ROLE_LABELS } from "../lib/format";
import { ConfirmModal, Modal } from "../components/Modal";
import { useToast } from "../components/Toast";
import { ErrorNote, Field, Loading, PageHead } from "../components/ui";

export function UsersPage() {
  const users = useApi<User[]>("/users/");
  const { user: me } = useAuth();
  const toast = useToast();
  const [editing, setEditing] = useState<User | "new" | null>(null);
  const [deleting, setDeleting] = useState<User | null>(null);
  const [showCustomers, setShowCustomers] = useState(false);

  const shown = (users.data ?? [])
    .filter((u) => showCustomers || u.role !== "customer")
    .sort((a, b) => a.username.localeCompare(b.username));

  async function remove() {
    if (!deleting) return;
    try {
      await api.del(`/users/${deleting.user_id}`);
      toast(`Deleted ${deleting.username}.`);
      users.reload();
    } catch (e) {
      toast(
        e instanceof Error && e.message.includes("still used")
          ? `${deleting.username} has recorded sales or loans. Deactivate the account instead.`
          : String(e instanceof Error ? e.message : e),
        "error",
      );
    }
    setDeleting(null);
  }

  return (
    <>
      <PageHead
        title="Staff accounts"
        sub="Who can sign in to the till. Deactivate an account to stop someone signing in."
        actions={<button className="btn btn-primary" onClick={() => setEditing("new")}>Add account</button>}
      />
      <div className="toolbar">
        <label className="check">
          <input type="checkbox" checked={showCustomers} onChange={(e) => setShowCustomers(e.target.checked)} /> Show customer accounts too
        </label>
      </div>

      {users.error ? (
        <ErrorNote message={users.error} onRetry={users.reload} />
      ) : users.loading && !users.data ? (
        <Loading />
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Status</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {shown.map((u) => (
                <tr key={u.user_id}>
                  <td className="strong">
                    {u.username}
                    {u.user_id === me?.user_id && <span className="tag">You</span>}
                  </td>
                  <td>{ROLE_LABELS[u.role]}</td>
                  <td>{u.is_active ? <span className="tag tag-green">Active</span> : <span className="tag tag-red">Deactivated</span>}</td>
                  <td className="right nowrap">
                    <button className="btn btn-small" onClick={() => setEditing(u)}>Edit</button>{" "}
                    {u.user_id !== me?.user_id && (
                      <button className="btn btn-small btn-quiet" onClick={() => setDeleting(u)}>Delete</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editing && (
        <UserModal
          user={editing === "new" ? null : editing}
          isSelf={editing !== "new" && editing.user_id === me?.user_id}
          onClose={() => setEditing(null)}
          onSaved={(u) => {
            setEditing(null);
            users.reload();
            toast(`Saved ${u.username}.`);
          }}
        />
      )}
      {deleting && (
        <ConfirmModal
          title="Delete account?"
          message={<>{deleting.username} will no longer be able to sign in. This can't be undone.</>}
          confirmLabel="Delete account"
          onConfirm={remove}
          onClose={() => setDeleting(null)}
        />
      )}
    </>
  );
}

function UserModal({ user, isSelf, onClose, onSaved }: { user: User | null; isSelf: boolean; onClose: () => void; onSaved: (u: User) => void }) {
  const [username, setUsername] = useState(user?.username ?? "");
  const [role, setRole] = useState<Role>(user?.role ?? "staff");
  const [active, setActive] = useState(user?.is_active ?? true);
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!user && password.length < 6) return setError("Use at least 6 characters for the password.");
    if (user && password && password.length < 6) return setError("Use at least 6 characters for the new password.");
    setBusy(true);
    setError(null);
    try {
      const saved = user
        ? await api.put<User>(`/users/${user.user_id}`, {
            username: username.trim(),
            role,
            is_active: active,
            ...(password ? { password } : {}),
          })
        : await api.post<User>("/users/", { username: username.trim(), password, role, is_active: active });
      onSaved(saved);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal title={user ? `Edit ${user.username}` : "Add account"} onClose={onClose}>
      <form onSubmit={submit} className="stack">
        <Field label="Username">
          <input value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
        </Field>
        <Field label="Role">
          <select value={role} onChange={(e) => setRole(e.target.value as Role)} disabled={isSelf}>
            <option value="staff">Staff: till, library and catalogue</option>
            <option value="super_admin">Administrator: everything, plus staff accounts</option>
            <option value="customer">Customer: own receipts and loans only</option>
          </select>
        </Field>
        <Field label={user ? "New password" : "Password"} hint={user ? "Leave empty to keep the current password." : undefined}>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" required={!user} />
        </Field>
        {!isSelf && (
          <label className="check">
            <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} /> Account is active (can sign in)
          </label>
        )}
        {error && <div className="error-note" role="alert">{error}</div>}
        <div className="form-actions">
          <button type="button" className="btn" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : user ? "Save changes" : "Add account"}</button>
        </div>
      </form>
    </Modal>
  );
}
