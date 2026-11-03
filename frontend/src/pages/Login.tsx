import { useState, type FormEvent } from "react";
import { Link } from "react-router";
import { useAuth } from "../lib/auth";
import { Field } from "../components/ui";

export function AuthFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="auth">
      <div className="auth-panel">
        <div className="auth-brand">
          <svg viewBox="0 0 32 32" className="brand-mark" aria-hidden>
            <path d="M7 6h11a6 6 0 0 1 6 6v14H13a6 6 0 0 1-6-6z" />
            <path d="M12 6v20" className="brand-spine" />
          </svg>
          <span>Charisma Library</span>
        </div>
        {children}
      </div>
      <div className="auth-art" aria-hidden>
        <div className="shelf">
          {Array.from({ length: 22 }).map((_, i) => (
            <span key={i} className={`spine spine-${i % 6}`} style={{ height: `${62 + ((i * 37) % 34)}%` }} />
          ))}
        </div>
        <p className="auth-quote">Books for sale, books to borrow — one counter.</p>
      </div>
    </div>
  );
}

export function LoginPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(username.trim(), password);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg === "incorrect" ? "Wrong username or password." : msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthFrame>
      <h1 className="auth-title">Sign in</h1>
      <form onSubmit={submit} className="stack">
        <Field label="Username">
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" autoFocus required />
        </Field>
        <Field label="Password">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </Field>
        {error && <div className="error-note" role="alert">{error}</div>}
        <button className="btn btn-primary btn-big" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="auth-alt">
        Library member? <Link to="/register">Create an account</Link> to see your loans and receipts.
      </p>
    </AuthFrame>
  );
}
