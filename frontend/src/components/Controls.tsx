import type { FormEvent } from "react";
import { getExportReviewCsvUrl } from "../api";
import { fetchedLabel, previousDayLabel } from "../format";
import type { Draft, Meta } from "../types";

const DECISION_TIMES = Array.from({ length: 48 }, (_, index) => {
  const hour = String(Math.floor(index / 2)).padStart(2, "0");
  const minute = index % 2 === 0 ? "00" : "30";
  return `${hour}:${minute}`;
});
DECISION_TIMES.push("09:20");
DECISION_TIMES.sort();

type Props = {
  meta: Meta;
  draft: Draft;
  busy: boolean;
  onChange: (draft: Draft) => void;
  onSubmit: () => void;
};

export function Controls({ meta, draft, busy, onChange, onSubmit }: Props) {
  function submit(event: FormEvent) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form
      className="bg-white border border-slate-200/90 rounded-2xl shadow-sm p-4 sm:p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[200px_230px_200px_auto_1fr] gap-4 items-end"
      onSubmit={submit}
    >
      <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-500">
        <span>Delivery day (Jan 2026)</span>
        <select
          className="w-full h-11 px-3 text-sm font-medium text-slate-800 bg-white border border-slate-200 rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all"
          value={draft.deliveryDay}
          onChange={(event) => onChange({ ...draft, deliveryDay: event.target.value })}
        >
          {meta.deliveryDays.map((day) => (
            <option key={day.value} value={day.value}>
              {day.label}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-500">
        <span>Decision time (day-ahead)</span>
        <span className="flex items-center h-11 px-3 text-sm bg-white border border-slate-200 rounded-xl shadow-xs focus-within:ring-2 focus-within:ring-teal-500 focus-within:border-teal-500 transition-all gap-2">
          <span className="text-xs font-medium text-slate-500 whitespace-nowrap">
            {previousDayLabel(draft.deliveryDay)}
          </span>
          <select
            className="w-full h-full text-sm font-semibold text-slate-800 bg-transparent border-0 focus:outline-none cursor-pointer"
            aria-label="Decision time"
            value={draft.decisionTime}
            onChange={(event) => onChange({ ...draft, decisionTime: event.target.value })}
          >
            {DECISION_TIMES.map((clock) => (
              <option key={clock} value={clock}>
                {clock}
              </option>
            ))}
          </select>
        </span>
      </label>

      <label className="flex flex-col gap-1.5 text-xs font-semibold text-slate-500">
        <span>Min. forecast horizon</span>
        <select
          className="w-full h-11 px-3 text-sm font-medium text-slate-800 bg-white border border-slate-200 rounded-xl shadow-xs focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all"
          value={draft.horizonHours}
          onChange={(event) => onChange({ ...draft, horizonHours: Number(event.target.value) })}
        >
          {meta.horizonOptions.map((hours) => (
            <option key={hours} value={hours}>
              {hours} h before gate
            </option>
          ))}
        </select>
      </label>

      <div className="flex items-center gap-2">
        <button
          className="h-11 px-5 rounded-xl font-semibold text-sm text-white bg-teal-600 hover:bg-teal-700 active:scale-[0.98] transition-all shadow-sm disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer whitespace-nowrap"
          type="submit"
          disabled={busy}
        >
          {busy ? "Updating…" : "Update view"}
        </button>

        <a
          href={getExportReviewCsvUrl(draft)}
          download={`windwatch_review_${draft.deliveryDay}.csv`}
          className="h-11 px-3.5 rounded-xl font-semibold text-xs sm:text-sm text-slate-700 bg-slate-100 hover:bg-slate-200 active:scale-[0.98] transition-all border border-slate-200 shadow-xs flex items-center justify-center cursor-pointer whitespace-nowrap gap-1.5"
          title="Download 48-settlement period intraday review to CSV"
        >
          <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span>Export CSV</span>
        </a>
      </div>

      <div className="flex items-center gap-2 text-xs text-slate-500 self-end justify-self-start lg:justify-self-end pb-2">
        <span className="relative flex h-2 w-2" aria-hidden="true">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
        </span>
        <span>Elexon BMRS Live Stream · Updated {fetchedLabel(meta.fetchedAt)}</span>
      </div>
    </form>
  );
}
