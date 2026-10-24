import { gw, signedGw } from "../format";
import type { Review } from "../types";

export function Kpis({ review }: { review: Review }) {
  const { kpis } = review;
  const periods =
    kpis.periodCount === 1 ? "1 half-hour period" : `${kpis.periodCount} half-hour periods`;

  return (
    <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Summary">
      <article className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Latest forecast, peak
        </h2>
        <p className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-2.5 mb-1 flex items-baseline gap-1.5">
          {gw(kpis.peakGw, 1)} <span className="text-base font-semibold text-slate-500">GW</span>
        </p>
        <p className="text-xs text-slate-500 mt-auto pt-2">
          {review.publishLabel ? `Published ${review.publishLabel}` : "No run before the gate"}
        </p>
      </article>

      <article className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Forecast average
        </h2>
        <p className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-2.5 mb-1 flex items-baseline gap-1.5">
          {gw(kpis.averageGw, 1)} <span className="text-base font-semibold text-slate-500">GW</span>
        </p>
        <p className="text-xs text-slate-500 mt-auto pt-2">{periods}</p>
      </article>

      <article className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Mean absolute error
        </h2>
        <p className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-2.5 mb-1 flex items-baseline gap-1.5">
          {gw(kpis.maeGw, 2)} <span className="text-base font-semibold text-slate-500">GW</span>
        </p>
        <p className="text-xs text-slate-500 mt-auto pt-2 flex items-center justify-between">
          <span>RMSE: <strong className="font-semibold text-slate-700">{gw(kpis.rmseGw ?? null, 2)} GW</strong></span>
          <span>nMAE: <strong className="font-semibold text-teal-700">{kpis.nmaePercent ? `${kpis.nmaePercent}%` : "—"}</strong></span>
        </p>
      </article>

      <article className="bg-white border border-slate-200/90 rounded-2xl p-4 sm:p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          Bias (forecast − actual)
        </h2>
        <p className="text-3xl sm:text-4xl font-bold tracking-tight text-slate-900 mt-2.5 mb-1 flex items-baseline gap-1.5">
          {signedGw(kpis.biasGw)} <span className="text-base font-semibold text-slate-500">GW</span>
        </p>
        <p className="text-xs text-slate-500 mt-auto pt-2">{kpis.biasLabel}</p>
      </article>
    </section>
  );
}
