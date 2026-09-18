"use client";

import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";

import { type GraphEdge, type GraphNode, type KnowledgeGraph, humanise } from "@/lib/ops";

const TYPE_COLOR: Record<string, string> = {
  Customer: "#f472b6",
  Booking: "#60a5fa",
  Disruption: "#fbbf24",
  PolicyRule: "#34d399",
  FrustrationCategory: "#fb7185",
  Feedback: "#34d399",
  Session: "#a78bfa",
  Unknown: "#94a3b8",
};

type Point = { x: number; y: number };
type View = { x: number; y: number; k: number };
type SimNode = GraphNode & Point & { vx: number; vy: number };
type Drag =
  | { kind: "pan"; start: Point; origin: View; moved: boolean }
  | { kind: "node"; id: string; start: Point; origin: Point; moved: boolean };

function colorFor(type: string) {
  return TYPE_COLOR[type] || TYPE_COLOR.Unknown;
}

function shortLabel(label: string) {
  return label.length > 22 ? `${label.slice(0, 20)}…` : label;
}

function collisionRadius(node: GraphNode) {
  return node.type === "Customer" ? 34 : 28;
}

function fitView(positions: Record<string, Point>, width: number, height: number): View {
  const points = Object.values(positions);
  if (!points.length) return { x: 0, y: 0, k: 1 };
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const point of points) {
    minX = Math.min(minX, point.x);
    minY = Math.min(minY, point.y);
    maxX = Math.max(maxX, point.x);
    maxY = Math.max(maxY, point.y);
  }
  const pad = 72;
  const boxW = Math.max(maxX - minX, 80);
  const boxH = Math.max(maxY - minY, 80);
  const k = Math.min((width - pad * 2) / boxW, (height - pad * 2) / boxH, 1.35);
  return {
    k,
    x: (width - boxW * k) / 2 - minX * k,
    y: (height - boxH * k) / 2 - minY * k,
  };
}

export function KnowledgeGraphPanel({
  data,
  highlightCustomerId,
}: {
  data: KnowledgeGraph | null;
  highlightCustomerId?: string | null;
}) {
  const [query, setQuery] = useState("");
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const visibleNodes = useMemo(() => {
    if (!data) return [];
    const needle = query.trim().toLowerCase();
    return data.nodes.filter((node) => {
      if (hidden.has(node.type)) return false;
      if (!needle) return true;
      return (
        node.label.toLowerCase().includes(needle) ||
        node.type.toLowerCase().includes(needle) ||
        node.id.toLowerCase().includes(needle)
      );
    });
  }, [data, hidden, query]);

  const visibleIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes]);

  const visibleEdges = useMemo(() => {
    if (!data) return [];
    return data.edges.filter((edge) => visibleIds.has(edge.from_id) && visibleIds.has(edge.to_id));
  }, [data, visibleIds]);

  const selected = visibleNodes.find((node) => node.id === selectedId) || null;
  const neighbors = useMemo(() => {
    if (!selected || !data) return [];
    return data.edges.filter((edge) => edge.from_id === selected.id || edge.to_id === selected.id);
  }, [selected, data]);

  const types = Object.keys(data?.types || {});
  const allVisible = types.length > 0 && types.every((type) => !hidden.has(type));

  if (!data || !data.nodes.length) {
    return (
      <section className="grid h-full min-h-[420px] place-items-center rounded-2xl border border-line bg-surface text-sm text-ink-faint">
        No graph edges yet. Run a passenger turn to grow the knowledge base.
      </section>
    );
  }

  return (
    <section className="flex h-full min-h-0 overflow-hidden rounded-2xl border border-line bg-surface text-ink shadow-card">
      <div className="relative min-h-0 min-w-0 flex-1">
        <ForceCanvas
          nodes={visibleNodes}
          edges={visibleEdges}
          selectedId={selectedId}
          highlightCustomerId={highlightCustomerId}
          onSelect={setSelectedId}
        />
        <div className="pointer-events-none absolute bottom-3 left-4 text-[11px] text-ink-faint">
          Scroll to zoom · drag to pan · click a node for its edges · {visibleNodes.length} nodes · {visibleEdges.length}{" "}
          edges
        </div>
      </div>

      <aside className="flex w-[280px] shrink-0 flex-col border-l border-line bg-lift">
        <div className="border-b border-line p-3">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search nodes…"
            className="w-full rounded-lg border border-line bg-canvas px-3 py-2 text-xs text-ink outline-none placeholder:text-ink-faint focus:border-brand"
          />
        </div>

        <div className="scroll-slim border-b border-line px-4 py-3">
          <div className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-faint">Node info</div>
          {selected ? (
            <div className="mt-2 space-y-2">
              <div className="text-sm font-semibold">{selected.label}</div>
              <dl className="space-y-1 text-[11px] text-ink-muted">
                <div>
                  Type: <span className="text-ink-soft">{selected.type}</span>
                </div>
                <div>
                  Degree: <span className="text-ink-soft">{neighbors.length}</span>
                </div>
                {neighbors[0]?.source ? (
                  <div>
                    Source: <span className="text-ink-soft">{neighbors[0].source}</span>
                  </div>
                ) : null}
              </dl>
              <div className="pt-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-faint">
                Neighbors ({neighbors.length})
              </div>
              <ol className="max-h-48 space-y-2 overflow-y-auto">
                {neighbors.map((edge) => {
                  const otherId = edge.from_id === selected.id ? edge.to_id : edge.from_id;
                  const other = data.nodes.find((node) => node.id === otherId);
                  return (
                    <li key={`${edge.from_id}-${edge.rel}-${edge.to_id}`} className="text-[11px] leading-4 text-ink-soft">
                      <span className="font-semibold text-brand-accent">{humanise(edge.rel)}</span>
                      {" → "}
                      <button type="button" className="text-left hover:text-ink" onClick={() => setSelectedId(otherId)}>
                        {other?.label || otherId}
                      </button>
                      {edge.reason ? <span className="mt-0.5 block text-ink-faint">{edge.reason}</span> : null}
                    </li>
                  );
                })}
              </ol>
            </div>
          ) : (
            <p className="mt-2 text-xs text-ink-faint">Click a node to inspect its edges.</p>
          )}
        </div>

        <div className="scroll-slim flex-1 px-4 py-3">
          <div className="text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-faint">Types</div>
          <label className="mt-2 flex items-center gap-2 text-xs text-ink-soft">
            <input
              type="checkbox"
              checked={allVisible}
              onChange={() => {
                if (allVisible) setHidden(new Set(types));
                else setHidden(new Set());
              }}
            />
            Select All
          </label>
          <div className="mt-2 space-y-1">
            {types.map((type) => (
              <label key={type} className="flex items-center gap-2 text-xs text-ink-soft">
                <input
                  type="checkbox"
                  checked={!hidden.has(type)}
                  onChange={() => {
                    setHidden((current) => {
                      const next = new Set(current);
                      if (next.has(type)) next.delete(type);
                      else next.add(type);
                      return next;
                    });
                  }}
                />
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: colorFor(type) }} />
                <span className="flex-1">{type}</span>
                <span className="text-ink-faint">{data.types?.[type] ?? 0}</span>
              </label>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}

function ForceCanvas({
  nodes,
  edges,
  selectedId,
  highlightCustomerId,
  onSelect,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedId: string | null;
  highlightCustomerId?: string | null;
  onSelect: (id: string | null) => void;
}) {
  const wrap = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const viewRef = useRef<View>({ x: 0, y: 0, k: 1 });
  const posRef = useRef<Record<string, Point>>({});
  const dragRef = useRef<Drag | null>(null);
  const runningRef = useRef(false);
  const [size, setSize] = useState({ width: 720, height: 640 });
  const [positions, setPositions] = useState<Record<string, Point>>({});
  const [view, setView] = useState<View>({ x: 0, y: 0, k: 1 });
  const [cursor, setCursor] = useState<"grab" | "grabbing" | "pointer">("grab");

  useEffect(() => {
    viewRef.current = view;
  }, [view]);

  useEffect(() => {
    posRef.current = positions;
  }, [positions]);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const measure = () => setSize({ width: el.clientWidth || 720, height: el.clientHeight || 640 });
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      event.stopPropagation();
      const current = viewRef.current;
      const factor = event.deltaY > 0 ? 0.9 : 1.1;
      const nextK = Math.min(4, Math.max(0.2, current.k * factor));
      const rect = el.getBoundingClientRect();
      const cx = event.clientX - rect.left;
      const cy = event.clientY - rect.top;
      const wx = (cx - current.x) / current.k;
      const wy = (cy - current.y) / current.k;
      const next = { k: nextK, x: cx - wx * nextK, y: cy - wy * nextK };
      viewRef.current = next;
      setView(next);
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  useEffect(() => {
    const { width, height } = size;
    if (!width || !height || !nodes.length) return;

    const radii = Object.fromEntries(nodes.map((node) => [node.id, collisionRadius(node)]));
    const sims: SimNode[] = nodes.map((node, index) => {
      const angle = (index / Math.max(nodes.length, 1)) * Math.PI * 2;
      return {
        ...node,
        x: width / 2 + Math.cos(angle) * 90,
        y: height / 2 + Math.sin(angle) * 90,
        vx: 0,
        vy: 0,
      };
    });
    const ids = new Map(sims.map((node) => [node.id, node]));
    runningRef.current = true;
    let frame = 0;
    let raf = 0;

    const publish = (done: boolean) => {
      const next = Object.fromEntries(sims.map((node) => [node.id, { x: node.x, y: node.y }]));
      posRef.current = next;
      setPositions(next);
      if (done) {
        const framed = fitView(next, width, height);
        viewRef.current = framed;
        setView(framed);
      }
    };

    const tick = () => {
      if (!runningRef.current) return;
      for (let i = 0; i < sims.length; i += 1) {
        for (let j = i + 1; j < sims.length; j += 1) {
          const a = sims[i];
          const b = sims[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const dist = Math.hypot(dx, dy) || 0.01;
          const nx = dx / dist;
          const ny = dy / dist;
          const charge = 720 / dist;
          a.vx += nx * charge;
          a.vy += ny * charge;
          b.vx -= nx * charge;
          b.vy -= ny * charge;
          const minDist = (radii[a.id] || 28) + (radii[b.id] || 28);
          if (dist < minDist) {
            const overlap = (minDist - dist) * 0.45;
            a.x += nx * overlap;
            a.y += ny * overlap;
            b.x -= nx * overlap;
            b.y -= ny * overlap;
          }
        }
      }
      for (const edge of edges) {
        const a = ids.get(edge.from_id);
        const b = ids.get(edge.to_id);
        if (!a || !b) continue;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.hypot(dx, dy) || 0.01;
        const rest = 96;
        const pull = (dist - rest) * 0.06;
        a.vx += (dx / dist) * pull;
        a.vy += (dy / dist) * pull;
        b.vx -= (dx / dist) * pull;
        b.vy -= (dy / dist) * pull;
      }
      for (const node of sims) {
        node.vx += (width / 2 - node.x) * 0.02;
        node.vy += (height / 2 - node.y) * 0.02;
        node.vx *= 0.75;
        node.vy *= 0.75;
        node.x += node.vx;
        node.y += node.vy;
      }
      frame += 1;
      if (frame % 4 === 0) publish(false);
      if (frame < 180) raf = requestAnimationFrame(tick);
      else {
        runningRef.current = false;
        publish(true);
      }
    };
    raf = requestAnimationFrame(tick);
    return () => {
      runningRef.current = false;
      cancelAnimationFrame(raf);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nodes.map((node) => node.id).join("|"), edges.length, size.width, size.height]);

  function worldPoint(clientX: number, clientY: number): Point {
    const rect = wrap.current?.getBoundingClientRect();
    const current = viewRef.current;
    const x = clientX - (rect?.left || 0);
    const y = clientY - (rect?.top || 0);
    return { x: (x - current.x) / current.k, y: (y - current.y) / current.k };
  }

  function hitNode(point: Point): GraphNode | null {
    let best: { node: GraphNode; dist: number } | null = null;
    for (const node of nodes) {
      const pos = posRef.current[node.id];
      if (!pos) continue;
      const dist = Math.hypot(pos.x - point.x, pos.y - point.y);
      if (dist <= collisionRadius(node) && (!best || dist < best.dist)) best = { node, dist };
    }
    return best?.node || null;
  }

  function onPointerDown(event: ReactPointerEvent<SVGSVGElement>) {
    if (event.button !== 0) return;
    runningRef.current = false;
    const hit = hitNode(worldPoint(event.clientX, event.clientY));
    const current = viewRef.current;
    event.currentTarget.setPointerCapture(event.pointerId);
    if (hit) {
      const origin = posRef.current[hit.id] || { x: 0, y: 0 };
      dragRef.current = { kind: "node", id: hit.id, start: { x: event.clientX, y: event.clientY }, origin, moved: false };
      setCursor("grabbing");
    } else {
      dragRef.current = { kind: "pan", start: { x: event.clientX, y: event.clientY }, origin: current, moved: false };
      setCursor("grabbing");
    }
  }

  function onPointerMove(event: ReactPointerEvent<SVGSVGElement>) {
    const drag = dragRef.current;
    if (!drag) {
      const hit = hitNode(worldPoint(event.clientX, event.clientY));
      setCursor(hit ? "pointer" : "grab");
      return;
    }
    const dx = event.clientX - drag.start.x;
    const dy = event.clientY - drag.start.y;
    if (Math.hypot(dx, dy) > 3) drag.moved = true;
    if (drag.kind === "pan") {
      const next = { ...drag.origin, x: drag.origin.x + dx, y: drag.origin.y + dy };
      viewRef.current = next;
      setView(next);
      return;
    }
    const k = viewRef.current.k;
    const nextPos = { x: drag.origin.x + dx / k, y: drag.origin.y + dy / k };
    posRef.current = { ...posRef.current, [drag.id]: nextPos };
    setPositions(posRef.current);
  }

  function onPointerUp() {
    const drag = dragRef.current;
    dragRef.current = null;
    setCursor("grab");
    if (!drag) return;
    if (!drag.moved) {
      onSelect(drag.kind === "node" ? drag.id : null);
    }
  }

  return (
    <div ref={wrap} className="h-full min-h-[520px] w-full touch-none">
      <svg
        ref={svgRef}
        width={size.width}
        height={size.height}
        className="block"
        style={{ cursor }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
      >
        <defs>
          <marker id="edge-arrow" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
          </marker>
        </defs>
        <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
          {edges.map((edge) => {
            const from = positions[edge.from_id];
            const to = positions[edge.to_id];
            if (!from || !to) return null;
            const mx = (from.x + to.x) / 2;
            const my = (from.y + to.y) / 2;
            const active =
              selectedId === edge.from_id ||
              selectedId === edge.to_id ||
              (highlightCustomerId && edge.customer_id === highlightCustomerId);
            return (
              <g key={`${edge.from_id}-${edge.rel}-${edge.to_id}`} className="pointer-events-none">
                <line
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke={active ? "#f9a8d4" : "#3d4560"}
                  strokeWidth={active ? 1.8 : 1.1}
                  strokeDasharray={edge.low_confidence ? "4 3" : undefined}
                  markerEnd="url(#edge-arrow)"
                />
                {active ? (
                  <text
                    x={mx}
                    y={my - 10}
                    textAnchor="middle"
                    fill="#fda4af"
                    fontSize="10"
                    paintOrder="stroke"
                    stroke="#0b0d14"
                    strokeWidth="3"
                  >
                    {humanise(edge.rel)}
                  </text>
                ) : null}
              </g>
            );
          })}
          {nodes.map((node) => {
            const pos = positions[node.id];
            if (!pos) return null;
            const selected = selectedId === node.id;
            const related =
              Boolean(highlightCustomerId) &&
              (node.id === highlightCustomerId ||
                edges.some(
                  (edge) =>
                    edge.customer_id === highlightCustomerId &&
                    (edge.from_id === node.id || edge.to_id === node.id),
                ));
            const r = node.type === "Customer" ? 11 : 7;
            return (
              <g key={node.id} className="pointer-events-none">
                <circle cx={pos.x} cy={pos.y} r={18} fill="transparent" />
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={selected ? r + 3 : r}
                  fill={colorFor(node.type)}
                  opacity={selected || related ? 0.95 : highlightCustomerId ? 0.35 : 0.95}
                  stroke={selected || related ? "#fff" : "transparent"}
                  strokeWidth={selected ? 2 : related ? 1 : 0}
                />
                <text
                  x={pos.x}
                  y={pos.y + r + 16}
                  textAnchor="middle"
                  fill="#e2e8f0"
                  fontSize="11"
                  paintOrder="stroke"
                  stroke="#0b0d14"
                  strokeWidth="4"
                >
                  {shortLabel(node.label)}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}
