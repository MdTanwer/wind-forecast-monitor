import { gw, percent } from "../format";
import type { Review } from "../types";

export function HorizonTable({ review }: { review: Review }) {
  return (
    <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col justify-between">
      <div>
        <h2 className="text-base font-bold text-slate-800 tracking-tight">Error by forecast horizon</h2>
        <p className="text-xs text-slate-500 mt-1">
          Lead-time rows score every January run. The top row scores only your gate rule.
        </p>
      </div>
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-slate-200">
              <th scope="col" className="pb-2.5 pt-1 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Horizon
              </th>
              <th scope="col" className="pb-2.5 pt-1 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                MAE (GW)
              </th>
              <th scope="col" className="pb-2.5 pt-1 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                RMSE (GW)
              </th>
              <th scope="col" className="pb-2.5 pt-1 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                nMAE
              </th>
              <th scope="col" className="pb-2.5 pt-1 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                P90 error (GW)
              </th>
              <th scope="col" className="pb-2.5 pt-1 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">
                MAPE
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            <tr className="bg-teal-50/70 hover:bg-teal-50 transition-colors">
              <th scope="row" className="py-2.5 px-1 text-left font-semibold text-teal-900">
                Your rule{" "}
                <span className="text-[11px] font-normal text-teal-700 bg-teal-100/80 px-1.5 py-0.5 rounded-md ml-1">
                  {review.decisionTime}, ≥{review.horizonHours} h
                </span>
              </th>
              <td className="py-2.5 px-1 text-right tabular-nums font-semibold text-teal-950">
                {gw(review.ruleErrors.maeGw, 2)}
              </td>
              <td className="py-2.5 px-1 text-right tabular-nums font-semibold text-teal-950">
                {gw(review.ruleErrors.rmseGw ?? null, 2)}
              </td>
              <td className="py-2.5 px-1 text-right tabular-nums font-semibold text-teal-950">
                {review.ruleErrors.nmaePercent ? `${review.ruleErrors.nmaePercent}%` : "—"}
              </td>
              <td className="py-2.5 px-1 text-right tabular-nums font-semibold text-teal-950">
                {gw(review.ruleErrors.p90Gw, 2)}
              </td>
              <td className="py-2.5 px-1 text-right tabular-nums font-semibold text-teal-950">
                {percent(review.ruleErrors.mape)}
              </td>
            </tr>
            {review.horizons.map((row) => (
              <tr key={row.label} className="hover:bg-slate-50/80 transition-colors">
                <th scope="row" className="py-2.5 px-1 text-left font-medium text-slate-700">
                  {row.label}
                </th>
                <td className="py-2.5 px-1 text-right tabular-nums text-slate-800">{gw(row.maeGw, 2)}</td>
                <td className="py-2.5 px-1 text-right tabular-nums text-slate-800">{gw(row.rmseGw ?? null, 2)}</td>
                <td className="py-2.5 px-1 text-right tabular-nums text-slate-800">
                  {row.nmaePercent ? `${row.nmaePercent}%` : "—"}
                </td>
                <td className="py-2.5 px-1 text-right tabular-nums text-slate-800">{gw(row.p90Gw, 2)}</td>
                <td className="py-2.5 px-1 text-right tabular-nums text-slate-800">{percent(row.mape)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
