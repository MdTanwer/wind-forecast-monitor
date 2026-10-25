import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Review, SeriesPoint } from "../types";

const TICKS = ["00:00", "06:00", "12:00", "18:00", "23:30"];

type ChartRow = SeriesPoint & { band: [number, number] | null };

function rows(review: Review): ChartRow[] {
  return review.series.map((point) => ({
    ...point,
    band:
      point.bandLow === null || point.bandHigh === null ? null : [point.bandLow, point.bandHigh],
  }));
}

function niceMax(values: number[]): number {
  const peak = Math.max(1, ...values);
  const padded = peak * 1.12;
  const step = padded > 20 ? 5 : padded > 8 ? 2.5 : 1;
  return Math.ceil(padded / step) * step;
}

function Tip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ChartRow }>;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="bg-slate-900/95 text-white backdrop-blur-md px-3.5 py-2.5 rounded-xl shadow-xl border border-slate-700/60 text-xs flex flex-col gap-1 min-w-[150px]">
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-1 mb-0.5 gap-2">
        <strong className="font-bold text-slate-100 text-sm">{point.label}</strong>
        {point.settlementPeriod && (
          <span className="text-[10px] font-semibold text-teal-300 bg-teal-950/80 px-1.5 py-0.5 rounded">
            SP {point.settlementPeriod}
          </span>
        )}
      </div>
      <span className="flex items-center justify-between gap-3 text-slate-200 font-medium">
        <span className="text-slate-400">Actual:</span>
        <span className="tabular-nums font-semibold text-white">
          {point.actualGw === null ? "—" : `${point.actualGw.toFixed(2)} GW`}
        </span>
      </span>
      <span className="flex items-center justify-between gap-3 text-emerald-300 font-medium">
        <span className="text-emerald-400/80">Forecast:</span>
        <span className="tabular-nums font-semibold">
          {point.forecastGw === null ? "—" : `${point.forecastGw.toFixed(2)} GW`}
        </span>
      </span>
      <span className="flex items-center justify-between gap-3 text-amber-300 font-medium">
        <span className="text-amber-400/80">Plan-on:</span>
        <span className="tabular-nums font-semibold">
          {point.planningGw === null ? "—" : `${point.planningGw.toFixed(2)} GW`}
        </span>
      </span>
    </div>
  );
}

export function ForecastChart({ review }: { review: Review }) {
  const data = rows(review);
  const scale = data.flatMap((point) =>
    [point.actualGw, point.forecastGw, point.bandHigh].filter((value): value is number => value !== null),
  );
  const rule = review.publishLabel
    ? `Latest run ${review.publishLabel}, at least ${review.horizonHours} h before the gate.`
    : `No WINDFOR file was published by ${review.cutoffLabel}.`;
  const coverage =
    review.publishLabel && review.coveredHours < 24
      ? ` ${review.coveredHours} of 24 hours covered.`
      : "";

  return (
    <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-800 tracking-tight">
            Forecast vs actual wind generation – {review.deliveryLabel}
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            {rule}
            {coverage}
          </p>
        </div>
        <ul className="flex flex-wrap items-center gap-4 text-xs text-slate-600 font-medium m-0 p-0 list-none">
          <li className="flex items-center gap-2">
            <span className="w-4 h-0.5 bg-[#243038] rounded-full inline-block" /> Actual
          </li>
          <li className="flex items-center gap-2">
            <span className="w-4 h-0 border-t-2 border-dashed border-[#12806d] inline-block" /> Latest forecast
          </li>
          <li className="flex items-center gap-2">
            <span className="w-3.5 h-2.5 bg-[#d5eee6] rounded-xs inline-block" /> ±1 MAE band
          </li>
          <li className="flex items-center gap-2">
            <span className="w-4 h-0 border-t-2 border-dashed border-[#c2662d] inline-block" /> Plan-on wind (P90)
          </li>
        </ul>
      </div>
      <div className="w-full mt-2">
        <ResponsiveContainer width="100%" height={320}>
          <ComposedChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
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
              domain={[0, niceMax(scale)]}
              tick={{ fill: "#6d7d86", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              width={36}
            />
            <Tooltip content={<Tip />} />
            <Area
              type="monotone"
              dataKey="band"
              stroke="none"
              fill="#d5eee6"
              fillOpacity={1}
              isAnimationActive={false}
              activeDot={false}
            />
            <Line
              type="monotone"
              dataKey="forecastGw"
              stroke="#12806d"
              strokeWidth={2}
              strokeDasharray="5 4"
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="planningGw"
              stroke="#c2662d"
              strokeWidth={1.75}
              strokeDasharray="2 3"
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="actualGw"
              stroke="#243038"
              strokeWidth={2.25}
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
