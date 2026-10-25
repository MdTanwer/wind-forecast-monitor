import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DailyError } from "../types";

const LABELLED = new Set(["2 Jan", "15 Jan", "1 Feb"]);

function Tip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: DailyError }>;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="bg-slate-900/95 text-white backdrop-blur-md px-3.5 py-2 rounded-xl shadow-xl border border-slate-700/60 text-xs flex flex-col gap-0.5">
      <strong className="font-bold text-slate-100 text-sm">{point.label}</strong>
      <span className="text-emerald-300 font-semibold tabular-nums">
        MAE: {point.maeGw === null ? "—" : `${point.maeGw.toFixed(2)} GW`}
      </span>
    </div>
  );
}

export function DailyChart({ daily, selected }: { daily: DailyError[]; selected: string }) {
  return (
    <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col justify-between">
      <div>
        <h2 className="text-base font-bold text-slate-800 tracking-tight">Daily error, January decisions</h2>
        <p className="text-xs text-slate-500 mt-1">Mean absolute error per delivery day, GW</p>
      </div>
      <div className="w-full mt-4">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={daily} margin={{ top: 8, right: 4, left: 0, bottom: 0 }} barCategoryGap={3}>
            <CartesianGrid stroke="#e6eef0" vertical={false} />
            <XAxis
              dataKey="label"
              interval={0}
              tick={{ fill: "#6d7d86", fontSize: 12 }}
              tickFormatter={(label: string) => (LABELLED.has(label) ? label : "")}
              axisLine={{ stroke: "#e1eaec" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#6d7d86", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={32}
            />
            <Tooltip content={<Tip />} cursor={{ fill: "rgba(18, 128, 109, 0.08)" }} />
            <Bar dataKey="maeGw" radius={[3, 3, 0, 0]} isAnimationActive={false} maxBarSize={18}>
              {daily.map((entry) => (
                <Cell key={entry.date} fill={entry.date === selected ? "#0c4f43" : "#12806d"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
