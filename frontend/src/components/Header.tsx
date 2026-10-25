import { TurbineIcon } from "../icons";

export function Header() {
  return (
    <header className="bg-[#10283a] text-white border-b border-slate-800 shadow-sm sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 min-h-[64px] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-6 py-3.5 sm:py-0">
        <div className="flex items-center gap-3">
          <span
            className="w-9 h-9 rounded-xl flex items-center justify-center bg-white/10 text-emerald-300 ring-1 ring-white/15 shadow-inner flex-shrink-0"
            aria-hidden="true"
          >
            <TurbineIcon width={22} height={22} />
          </span>
          <div>
            <div className="text-lg font-bold tracking-tight text-white leading-none">WindWatch</div>
            <div className="text-xs text-slate-300 mt-1 font-normal">GB day-ahead wind forecast review</div>
          </div>
        </div>
        <p className="text-xs text-slate-400 font-medium sm:text-right m-0">
          Sources: Elexon BMRS Live API · FUELHH (actual) · WINDFOR (forecast)
        </p>
      </div>
    </header>
  );
}
