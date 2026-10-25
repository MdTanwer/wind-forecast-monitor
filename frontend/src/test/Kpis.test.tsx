import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Kpis } from "../components/Kpis";
import type { Review } from "../types";

describe("Kpis component", () => {
  const mockReview: Review = {
    deliveryDay: "2026-01-15",
    deliveryLabel: "15 Jan",
    deliveryLabelWithYear: "15 Jan 2026",
    decisionLabel: "14 Jan, 09:00",
    decisionTime: "09:00",
    horizonHours: 4,
    gateTime: "2026-01-14T09:00:00+00:00",
    cutoffTime: "2026-01-14T05:00:00+00:00",
    cutoffLabel: "14 Jan 05:00",
    publishTime: "2026-01-14T04:30:00+00:00",
    publishLabel: "14 Jan 04:30",
    coveredHours: 24,
    kpis: {
      peakGw: 14.5,
      averageGw: 11.2,
      periodCount: 48,
      maeGw: 1.85,
      rmseGw: 2.15,
      nmaePercent: 10.4,
      biasGw: 0.35,
      biasLabel: "Slight over-forecast",
      scoredDays: 31,
    },
    planning: {
      marginGw: 2.4,
      averageGw: 8.8,
      forecastAverageGw: 11.2,
      minimumGw: 5.1,
    },
    ruleErrors: {
      label: "Your rule",
      maeGw: 1.85,
      rmseGw: 2.15,
      p90Gw: 2.4,
      mape: 0.12,
      nmaePercent: 10.4,
      samples: 48,
    },
    series: [],
    horizons: [],
    daily: [],
  };

  it("renders peak, average, MAE, RMSE and nMAE correctly", () => {
    render(<Kpis review={mockReview} />);
    expect(screen.getByText("14.5")).toBeInTheDocument();
    expect(screen.getByText("11.2")).toBeInTheDocument();
    expect(screen.getByText("1.85")).toBeInTheDocument();
    expect(screen.getByText(/2.15/)).toBeInTheDocument();
    expect(screen.getByText("10.4%")).toBeInTheDocument();
    expect(screen.getByText("+0.35")).toBeInTheDocument();
    expect(screen.getByText(/Slight over-forecast/)).toBeInTheDocument();
  });
});
