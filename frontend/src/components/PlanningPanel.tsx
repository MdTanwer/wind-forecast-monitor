import { gw } from "../format";
import type { Review } from "../types";

export function PlanningPanel({ review }: { review: Review }) {
  const { planning } = review;
  if (planning.averageGw === null || planning.marginGw === null) {
    return (
      <section className="bg-slate-100 border border-slate-200 rounded-2xl p-5 sm:p-6 text-slate-500 text-sm">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Planning figure</h2>
        <p>No forecast was available before the gate, so there is no planning figure for {review.deliveryLabel}.</p>
      </section>
    );
  }

  return (
    <section
      className="bg-gradient-to-br from-emerald-50/70 via-teal-50/40 to-slate-50 border border-teal-200/80 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-6"
      aria-label="Planning figure"
    >
      <div className="flex-shrink-0 min-w-[240px]">
        <h2 className="text-xs font-semibold text-teal-800 uppercase tracking-wide">
          Wind to plan on · {review.deliveryLabel}
        </h2>
        <p className="text-3xl sm:text-4xl font-bold tracking-tight text-teal-950 mt-2 mb-1 flex items-baseline gap-1.5">
          {gw(planning.averageGw, 1)}{" "}
          <span className="text-base font-semibold text-teal-700">GW average</span>
        </p>
        <p className="text-xs text-teal-800/80 font-medium">Lowest half-hour {gw(planning.minimumGw, 1)} GW</p>
      </div>
      <p className="text-sm text-slate-600 leading-relaxed max-w-2xl bg-white/70 p-4 rounded-xl border border-teal-100/80 shadow-xs m-0">
        The forecast averages <strong className="text-slate-900 font-semibold">{gw(planning.forecastAverageGw, 1)} GW</strong>. Under this gate rule, January
        forecasts were more than <strong className="text-slate-900 font-semibold">{gw(planning.marginGw, 2)} GW</strong> above actual wind in only 1 hour in
        10. Taking that margin off leaves the figure on the left. Cover demand beyond it from the day-ahead market.
      </p>
    </section>
  );
}
