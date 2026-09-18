"use client";

import { useEffect, useMemo, useState } from "react";

import { CaseBoard } from "@/components/case-board";
import { CaseDrawer } from "@/components/case-drawer";
import { OpsDashboard } from "@/components/dashboard";
import { KnowledgeGraphPanel } from "@/components/knowledge-graph";
import { StaffLogin } from "@/components/staff-login";
import { clearStaffToken, readStaffToken, staffLogout, takeStaffTokenFromHash } from "@/lib/auth";
import {
  type Analytics,
  type CaseDetail,
  type CaseSummary,
  type Frustration,
  type KnowledgeGraph,
  OpsAuthError,
  fetchJson,
} from "@/lib/ops";

type View = "dashboard" | "cases" | "graph";

export default function OperationsPage() {
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [view, setView] = useState<View>("dashboard");
  const [query, setQuery] = useState("");
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [frustration, setFrustration] = useState<Frustration | null>(null);
  const [graph, setGraph] = useState<KnowledgeGraph | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setToken(takeStaffTokenFromHash() || readStaffToken());
    setReady(true);
  }, []);

  useEffect(() => {
    if (!token) return;

    function expire() {
      clearStaffToken();
      setToken(null);
      setCases([]);
      setAnalytics(null);
      setFrustration(null);
      setGraph(null);
      setDetail(null);
      setSelectedId(null);
    }

    function load() {
      Promise.all([
        fetchJson<CaseSummary[]>("/api/cases", token as string),
        fetchJson<Analytics>("/api/analytics/summary", token as string),
        fetchJson<Frustration>("/api/analytics/frustration", token as string),
        fetchJson<KnowledgeGraph>("/api/graph", token as string),
      ])
        .then(([list, summary, distress, kb]) => {
          setError("");
          setCases(list);
          setAnalytics(summary);
          setFrustration(distress);
          setGraph((current) => {
            if (
              current &&
              current.writes === kb.writes &&
              current.unique_edges === kb.unique_edges &&
              current.nodes.length === kb.nodes.length
            ) {
              return current;
            }
            return kb;
          });
        })
        .catch((err) => {
          if (err instanceof OpsAuthError) expire();
          else setError("Operations service is offline. Start the API on port 8000.");
        })
        .finally(() => setLoaded(true));
    }
    load();
    window.addEventListener("focus", load);
    const timer = window.setInterval(load, 5000);
    return () => {
      window.removeEventListener("focus", load);
      window.clearInterval(timer);
    };
  }, [token]);

  useEffect(() => {
    if (!token || !selectedId) {
      setDetail(null);
      return;
    }
    fetchJson<CaseDetail>(`/api/cases/${selectedId}`, token)
      .then(setDetail)
      .catch((err) => {
        if (err instanceof OpsAuthError) {
          clearStaffToken();
          setToken(null);
        } else {
          setDetail(null);
        }
      });
  }, [selectedId, token]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return cases;
    return cases.filter((item) =>
      [item.customer, item.pnr, item.issue, item.flight, item.status]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    );
  }, [cases, query]);

  if (!ready) {
    return <div className="grid min-h-dvh place-items-center text-sm text-ink-muted">Loading…</div>;
  }

  if (!token) {
    return <StaffLogin onSignedIn={setToken} />;
  }

  return (
    <div className="flex min-h-dvh">
      <aside className="hidden w-60 shrink-0 flex-col border-r border-line bg-sidebar md:flex">
        <div className="px-5 py-6">
          <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-brand-accent">AeroResolve</div>
          <div className="mt-1 text-lg font-semibold">Operations</div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          <NavButton active={view === "dashboard"} onClick={() => setView("dashboard")}>
            Dashboard
          </NavButton>
          <NavButton active={view === "cases"} onClick={() => setView("cases")}>
            Cases
          </NavButton>
          <NavButton active={view === "graph"} onClick={() => setView("graph")}>
            Knowledge graph
          </NavButton>
        </nav>
        <div className="border-t border-line px-3 py-4">
          <button
            type="button"
            onClick={() => {
              void staffLogout(token).then(() => setToken(null));
            }}
            className="w-full rounded-xl px-3 py-2 text-left text-sm text-ink-muted hover:bg-white/5 hover:text-ink"
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center gap-3 border-b border-line bg-canvas/80 px-5 py-3 backdrop-blur">
          <div className="flex gap-1 md:hidden">
            {(["dashboard", "cases", "graph"] as View[]).map((item) => (
              <button
                key={item}
                type="button"
                onClick={() => setView(item)}
                className={`rounded-lg px-2.5 py-1.5 text-xs capitalize ${view === item ? "bg-brand text-white" : "text-ink-muted"}`}
              >
                {item === "graph" ? "Graph" : item}
              </button>
            ))}
          </div>
          <div className="relative min-w-[220px] flex-1">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search customer, PNR, flight…"
              className="h-10 w-full rounded-xl border border-line bg-surface px-4 text-sm outline-none placeholder:text-ink-faint focus:border-brand"
            />
          </div>
          <div className="flex items-center gap-2 text-xs text-ink-muted">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-good-fg" />
              Live
            </span>
            <span className="hidden sm:inline">{analytics?.kb_backend || "json"} store</span>
          </div>
        </header>

        <main className={view === "graph" ? "min-h-0 flex-1 overflow-hidden p-4" : "scroll-slim flex-1 overflow-y-auto px-5 py-5"}>
          {error && (
            <p className="mb-4 rounded-xl border border-stop/40 bg-stop-bg px-4 py-3 text-sm text-stop-fg">{error}</p>
          )}

          {view === "dashboard" && (
            <div className="space-y-5">
              <OpsDashboard analytics={analytics} cases={filtered} frustration={frustration} />
              <div>
                <div className="mb-3 flex items-end justify-between">
                  <div>
                    <h2 className="text-sm font-semibold">Case pipeline</h2>
                    <p className="mt-1 text-xs text-ink-muted">Open a card to read the transcript, policy, and audit trail.</p>
                  </div>
                  <span className="text-[11px] text-ink-faint">{filtered.length} shown</span>
                </div>
                <CaseBoard
                  cases={filtered}
                  selectedId={selectedId}
                  onSelect={(id) => setSelectedId(id)}
                />
                {loaded && !cases.length && !error && (
                  <p className="mt-4 text-center text-sm text-ink-muted">No cases yet. Run a passenger conversation first.</p>
                )}
              </div>
            </div>
          )}

          {view === "cases" && (
            <div>
              <div className="mb-3">
                <h2 className="text-sm font-semibold">Cases</h2>
                <p className="mt-1 text-xs text-ink-muted">Same pipeline as the dashboard, without the charts.</p>
              </div>
              <CaseBoard cases={filtered} selectedId={selectedId} onSelect={setSelectedId} />
            </div>
          )}

          {view === "graph" && (
            <KnowledgeGraphPanel data={graph} highlightCustomerId={detail?.customer_id} />
          )}
        </main>
      </div>

      <CaseDrawer caseData={selectedId ? detail : null} onClose={() => setSelectedId(null)} />
    </div>
  );
}

function NavButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-xl px-3 py-2 text-left text-sm ${
        active ? "bg-brand-tint font-medium text-ink" : "text-ink-muted hover:bg-white/5 hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}
