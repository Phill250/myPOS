import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router";
import { useAuth } from "../lib/auth";
import { ROLE_LABELS } from "../lib/format";

// Simple stroke icons (24px grid) so we don't need an icon library.
const ICONS: Record<string, string> = {
  dashboard: "M4 13h6V4H4zM14 20h6v-9h-6zM4 20h6v-4H4zM14 4v4h6V4z",
  till: "M4 7h16v12H4zM8 7V4h8v3M8 12h3M8 15h5M15 12h1M15 15h1",
  library: "M5 4h4v16H5zM10 4h4v16h-4zM15.5 5l3.8-1 3 15.4-3.8.9z",
  books: "M5 4h10a4 4 0 0 1 4 4v12H9a4 4 0 0 1-4-4zM9 4v16",
  customers: "M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21a7 7 0 0 1 14 0M17 3.5a4 4 0 0 1 0 7.5M22 21a7 7 0 0 0-4-6.3",
  sales: "M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6M9 16h3",
  settings: "M4 7h10M18 7h2M4 17h4M12 17h8M14 5v4M8 15v4",
  users: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
  account: "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0",
};

export function Icon({ name }: { name: string }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" aria-hidden>
      <path d={ICONS[name]} />
    </svg>
  );
}

export function Layout() {
  const { user, logout, isStaff, isAdmin } = useAuth();
  const [open, setOpen] = useState(false);
  const location = useLocation();

  useEffect(() => setOpen(false), [location.pathname]);

  const links = isStaff
    ? [
        { to: "/", label: "Today", icon: "dashboard", end: true },
        { to: "/till", label: "Till", icon: "till" },
        { to: "/library", label: "Library loans", icon: "library" },
        { to: "/books", label: "Books", icon: "books" },
        { to: "/customers", label: "Customers", icon: "customers" },
        { to: "/sales", label: "Sales history", icon: "sales" },
        { to: "/settings", label: "Categories & suppliers", icon: "settings" },
        ...(isAdmin ? [{ to: "/users", label: "Staff accounts", icon: "users" }] : []),
      ]
    : [{ to: "/", label: "My account", icon: "account", end: true }];

  return (
    <div className="shell">
      <aside className={open ? "side side-open" : "side"}>
        <div className="brand">
          <svg viewBox="0 0 32 32" className="brand-mark" aria-hidden>
            <path d="M7 6h11a6 6 0 0 1 6 6v14H13a6 6 0 0 1-6-6z" />
            <path d="M12 6v20" className="brand-spine" />
          </svg>
          <div>
            <div className="brand-name">Charisma</div>
            <div className="brand-sub">Library &amp; bookshop</div>
          </div>
        </div>

        <nav className="nav" aria-label="Main">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className="nav-link">
              <Icon name={l.icon} />
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="side-user">
          <div>
            <div className="side-username">{user?.username}</div>
            <div className="side-role">{user && ROLE_LABELS[user.role]}</div>
          </div>
          <button className="btn btn-ghost-light btn-small" onClick={logout}>
            Log out
          </button>
        </div>
      </aside>

      <div className="main-wrap">
        <div className="topbar">
          <button className="icon-btn" onClick={() => setOpen((o) => !o)} aria-label="Menu" aria-expanded={open}>
            <svg viewBox="0 0 24 24" className="icon" aria-hidden>
              <path d="M4 7h16M4 12h16M4 17h16" />
            </svg>
          </button>
          <span className="brand-name">Charisma</span>
        </div>
        {open && <div className="scrim" onClick={() => setOpen(false)} />}
        <main className="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
