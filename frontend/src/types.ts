export type DeliveryOption = {
  value: string;
  label: string;
};

export type Meta = {
  deliveryDays: DeliveryOption[];
  defaultDeliveryDay: string;
  defaultDecisionTime: string;
  defaultHorizonHours: number;
  horizonOptions: number[];
  timezone: string;
  fetchedAt: string;
  source: string;
  liveApi: boolean;
  actualHalfHours: number;
  forecastPublications: number;
  sources: {
    actuals: string;
    forecasts: string;
  };
};


export type SeriesPoint = {
  settlementPeriod?: number | null;
  time: string;
  label: string;
  actualGw: number | null;
  forecastGw: number | null;
  bandLow: number | null;
  bandHigh: number | null;
  planningGw: number | null;
};

export type HorizonRow = {
  label: string;
  maeGw: number | null;
  rmseGw?: number | null;
  p90Gw: number | null;
  mape: number | null;
  nmaePercent?: number | null;
  samples: number;
};

export type DailyError = {
  date: string;
  label: string;
  maeGw: number | null;
};

export type Review = {
  deliveryDay: string;
  deliveryLabel: string;
  deliveryLabelWithYear: string;
  decisionLabel: string;
  decisionTime: string;
  horizonHours: number;
  gateTime: string;
  cutoffTime: string;
  cutoffLabel: string;
  publishTime: string | null;
  publishLabel: string | null;
  coveredHours: number;
  kpis: {
    peakGw: number | null;
    averageGw: number | null;
    periodCount: number;
    maeGw: number | null;
    rmseGw?: number | null;
    nmaePercent?: number | null;
    biasGw: number | null;
    biasLabel: string;
    scoredDays: number;
  };
  planning: {
    marginGw: number | null;
    averageGw: number | null;
    forecastAverageGw: number | null;
    minimumGw: number | null;
  };
  ruleErrors: HorizonRow;
  series: SeriesPoint[];
  horizons: HorizonRow[];
  daily: DailyError[];
};

export type Draft = {
  deliveryDay: string;
  decisionTime: string;
  horizonHours: number;
};

export type VintageSummary = {
  publishTime: string;
  publishLabel: string;
  leadHoursToGate: number;
  averageGw: number | null;
  peakGw: number | null;
};

export type EvolutionPoint = {
  settlementPeriod: number;
  time: string;
  label: string;
  actualGw: number | null;
  latestGw: number | null;
  previousGw: number | null;
  deltaGw: number | null;
};

export type EvolutionResponse = {
  deliveryDay: string;
  deliveryLabel: string;
  decisionTime: string;
  gateTime: string;
  latestVintage: VintageSummary | null;
  previousVintage: VintageSummary | null;
  totalVintagesBeforeGate: number;
  series: EvolutionPoint[];
};

