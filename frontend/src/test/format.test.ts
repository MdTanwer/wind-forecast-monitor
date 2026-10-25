import { describe, expect, it } from "vitest";
import { fetchedLabel, gw, percent, previousDayLabel, signedGw } from "../format";

describe("format utilities", () => {
  it("computes previousDayLabel correctly across month boundaries", () => {
    expect(previousDayLabel("2026-01-15")).toBe("14 Jan,");
    expect(previousDayLabel("2026-02-01")).toBe("31 Jan,");
    expect(previousDayLabel("2026-01-01")).toBe("31 Dec,");
  });

  it("formats fetched timestamp with date and time", () => {
    expect(fetchedLabel("2026-01-15T09:30:00Z")).toBe("15 Jan 2026, 09:30 UTC");
    expect(fetchedLabel("invalid")).toBe("date unknown");
  });

  it("formats gw values with specified digits", () => {
    expect(gw(14.5678, 1)).toBe("14.6");
    expect(gw(14.5678, 2)).toBe("14.57");
    expect(gw(null, 2)).toBe("—");
  });

  it("formats signedGw with unicode minus and plus", () => {
    expect(signedGw(2.45)).toBe("+2.45");
    expect(signedGw(-1.2)).toBe("−1.20");
    expect(signedGw(0)).toBe("0.00");
    expect(signedGw(null)).toBe("—");
  });

  it("formats percent values", () => {
    expect(percent(0.067)).toBe("6.7%");
    expect(percent(null)).toBe("—");
  });
});
