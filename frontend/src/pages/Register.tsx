import { useState, type FormEvent } from "react";
import { Link } from "react-router";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Field } from "../components/ui";
import { AuthFrame } from "./Login";

export function RegisterPage() {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      setError("The two passwords don't match.");
      return;
    }
    if (password.length < 6) {
      setError("Use at least 6 characters for your password.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await api.post("/users/register", { username: username.trim(), password });
      await login(username.trim(), password);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg === "username exists" ? "That username is taken. Try another." : msg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthFrame>
      <h1 className="auth-title">Create your account</h1>
      <p className="muted">
        After signing up, ask at the front desk to link the account to your library card.
      </p>
      <form onSubmit={submit} className="stack">
        <Field label="Username">
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required />
        </Field>
        <Field label="Password">
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="new-password" required />
        </Field>
        <Field label="Confirm password">
          <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" required />
        </Field>
        {error && <div className="error-note" role="alert">{error}</div>}
        <button className="btn btn-primary btn-big" disabled={busy}>
          {busy ? "Creating account…" : "Create account"}
        </button>
      </form>
      <p className="auth-alt">
        Already have an account? <Link to="/">Sign in</Link>
      </p>
    </AuthFrame>
  );
}
