import {
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EvolutionPoint, EvolutionResponse } from "../types";

const TICKS = ["00:00", "06:00", "12:00", "18:00", "23:30"];

function Tip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: EvolutionPoint }>;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  const deltaColor =
    point.deltaGw === null
      ? "text-slate-400"
      : point.deltaGw >= 0
      ? "text-emerald-400"
      : "text-rose-400";
  const deltaSign = point.deltaGw !== null && point.deltaGw > 0 ? "+" : "";

  return (
    <div className="bg-slate-900/95 text-white backdrop-blur-md px-3.5 py-2.5 rounded-xl shadow-xl border border-slate-700/60 text-xs flex flex-col gap-1 min-w-[170px]">
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-1 mb-0.5">
        <strong className="font-bold text-slate-100 text-sm">{point.label}</strong>
        <span className="text-[11px] font-semibold text-teal-400 bg-teal-950/80 px-1.5 py-0.5 rounded">
          SP {point.settlementPeriod}
        </span>
      </div>
      <span className="flex items-center justify-between gap-3 text-slate-200 font-medium">
        <span className="text-slate-400">Actual:</span>
        <span className="tabular-nums font-semibold text-white">
          {point.actualGw === null ? "—" : `${point.actualGw.toFixed(2)} GW`}
        </span>
      </span>
      <span className="flex items-center justify-between gap-3 text-teal-300 font-medium">
        <span className="text-teal-400/80">Latest Run:</span>
        <span className="tabular-nums font-semibold">
          {point.latestGw === null ? "—" : `${point.latestGw.toFixed(2)} GW`}
        </span>
      </span>
      <span className="flex items-center justify-between gap-3 text-indigo-300 font-medium">
        <span className="text-indigo-400/80">Previous Run:</span>
        <span className="tabular-nums font-semibold">
          {point.previousGw === null ? "—" : `${point.previousGw.toFixed(2)} GW`}
        </span>
      </span>
      <span className={`flex items-center justify-between gap-3 font-semibold pt-0.5 border-t border-slate-800 ${deltaColor}`}>
        <span>Revision Delta:</span>
        <span className="tabular-nums">
          {point.deltaGw === null ? "—" : `${deltaSign}${point.deltaGw.toFixed(2)} GW`}
        </span>
      </span>
    </div>
  );
}

export function ForecastEvolution({ evolution }: { evolution: EvolutionResponse }) {
  const latest = evolution.latestVintage;
  const previous = evolution.previousVintage;
  const avgDelta =
    latest?.averageGw !== null && previous?.averageGw !== null && latest?.averageGw !== undefined && previous?.averageGw !== undefined
      ? Number((latest.averageGw - previous.averageGw).toFixed(2))
      : null;

  return (
    <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-base font-bold text-slate-800 tracking-tight">
              Forecast Evolution & Run-to-Run Delta
            </h2>
            {avgDelta !== null && (
              <span
                className={`text-xs font-semibold px-2 py-0.5 rounded-full inline-flex items-center gap-1 ${
                  avgDelta >= 0
                    ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                    : "bg-rose-100 text-rose-800 border border-rose-200"
                }`}
              >
                {avgDelta >= 0 ? "▲ Upward revision" : "▼ Downward revision"} (
                {avgDelta >= 0 ? `+${avgDelta}` : avgDelta} GW avg)
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Tracking model adjustments between consecutive forecast publications leading to the{" "}
            {evolution.decisionTime} decision gate.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs text-slate-600 font-medium">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 bg-teal-600 rounded-xs inline-block" /> Latest (
            {latest?.publishLabel || "N/A"})
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 bg-indigo-500 rounded-xs inline-block" /> Previous (
            {previous?.publishLabel || "N/A"})
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 bg-emerald-500 rounded-xs inline-block" /> Upward (+Δ)
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 bg-rose-500 rounded-xs inline-block" /> Downward (-Δ)
          </span>
        </div>
      </div>

      <div className="w-full mt-2">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart data={evolution.series} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#e6eef0" vertical={false} />
            <XAxis
              dataKey="label"
              ticks={TICKS}
              tick={{ fill: "#6d7d86", fontSize: 12 }}
              axisLine={{ stroke: "#e1eaec" }}
              tickLine={false}
              dy={6}
            />
            <YAxis
              tick={{ fill: "#6d7d86", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={36}
            />
            <Tooltip content={<Tip />} />
            <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
            <Bar dataKey="deltaGw" isAnimationActive={false}>
              {evolution.series.map((entry) => (
                <Cell
                  key={`cell-${entry.settlementPeriod}`}
                  fill={
                    entry.deltaGw === null
                      ? "#cbd5e1"
                      : entry.deltaGw >= 0
                      ? "#10b981"
                      : "#f43f5e"
                  }
                  opacity={0.85}
                />
              ))}
            </Bar>
            <Line
              type="monotone"
              dataKey="latestGw"
              stroke="#0d9488"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="previousGw"
              stroke="#6366f1"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
