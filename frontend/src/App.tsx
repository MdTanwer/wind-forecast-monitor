import { useCallback, useEffect, useState } from "react";
import { fetchEvolution, fetchMeta, fetchReview } from "./api";
import { Controls } from "./components/Controls";
import { DailyChart } from "./components/DailyChart";
import { ForecastChart } from "./components/ForecastChart";
import { ForecastEvolution } from "./components/ForecastEvolution";
import { Header } from "./components/Header";
import { HorizonTable } from "./components/HorizonTable";
import { Kpis } from "./components/Kpis";
import { PlanningPanel } from "./components/PlanningPanel";
import { SpinnerIcon } from "./icons";
import type { Draft, EvolutionResponse, Meta, Review } from "./types";

export function App() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [review, setReview] = useState<Review | null>(null);
  const [evolution, setEvolution] = useState<EvolutionResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadInitial = useCallback(async () => {
    try {
      const next = await fetchMeta();
      const initial: Draft = {
        deliveryDay: next.defaultDeliveryDay,
        decisionTime: next.defaultDecisionTime,
        horizonHours: next.defaultHorizonHours,
      };
      setMeta(next);
      setDraft(initial);
      const [reviewData, evolutionData] = await Promise.all([
        fetchReview(initial),
        fetchEvolution(initial),
      ]);
      setReview(reviewData);
      setEvolution(evolutionData);
      setError(null);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The review could not be loaded.");
    }
  }, []);

  useEffect(() => {
    void loadInitial();
  }, [loadInitial]);

  async function apply() {
    if (!draft) return;
    setBusy(true);
    setError(null);
    try {
      const [reviewData, evolutionData] = await Promise.all([
        fetchReview(draft),
        fetchEvolution(draft),
      ]);
      setReview(reviewData);
      setEvolution(evolutionData);
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : "The review could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Header />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-5 sm:space-y-6">
        {meta && draft ? (
          <Controls
            meta={meta}
            draft={draft}
            busy={busy}
            onChange={setDraft}
            onSubmit={() => void apply()}
          />
        ) : error ? (
          <section className="bg-red-50/80 border border-red-200/80 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <p className="text-red-800 text-sm font-medium m-0">{error}</p>
            <button
              className="px-4 py-2 bg-red-600 hover:bg-red-700 active:scale-95 text-white rounded-xl text-sm font-semibold shadow-xs transition-all cursor-pointer"
              type="button"
              onClick={() => void loadInitial()}
            >
              Retry
            </button>
          </section>
        ) : (
          <section className="bg-white border border-slate-200/90 rounded-2xl p-8 shadow-sm flex items-center justify-center gap-3 text-slate-500 text-sm font-medium">
            <SpinnerIcon className="animate-spin h-5 w-5 text-teal-600" />
            <span>Loading the January review…</span>
          </section>
        )}
        {error ? (
          <section className="bg-red-50/80 border border-red-200/80 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <p className="text-red-800 text-sm font-medium m-0">{error}</p>
            <button
              className="px-4 py-2 bg-red-600 hover:bg-red-700 active:scale-95 text-white rounded-xl text-sm font-semibold shadow-xs transition-all cursor-pointer"
              type="button"
              onClick={() => void (review ? apply() : loadInitial())}
            >
              Retry
            </button>
          </section>
        ) : null}
        {review ? (
          <>
            <Kpis review={review} />
            <ForecastChart review={review} />
            {evolution ? <ForecastEvolution evolution={evolution} /> : null}
            <section className="grid grid-cols-1 lg:grid-cols-[1.05fr_1fr] gap-5 sm:gap-6">
              <HorizonTable review={review} />
              <DailyChart daily={review.daily} selected={review.deliveryDay} />
            </section>
            <PlanningPanel review={review} />
          </>
        ) : null}
      </main>
    </>
  );
}
