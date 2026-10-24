import { apiClient } from "./client";
import type { Draft, EvolutionResponse, Meta, Review } from "../types";

export async function fetchMeta(): Promise<Meta> {
  const response = await apiClient.get<Meta>("/meta");
  return response.data;
}

export async function fetchReview(draft: Draft): Promise<Review> {
  const response = await apiClient.get<Review>("/review", {
    params: {
      deliveryDay: draft.deliveryDay,
      decisionTime: draft.decisionTime,
      horizonHours: draft.horizonHours,
    },
  });
  return response.data;
}

export async function fetchEvolution(draft: Draft): Promise<EvolutionResponse> {
  const response = await apiClient.get<EvolutionResponse>("/forecasts/evolution", {
    params: {
      deliveryDay: draft.deliveryDay,
      decisionTime: draft.decisionTime,
      horizonHours: draft.horizonHours,
    },
  });
  return response.data;
}

export function getExportReviewCsvUrl(draft: Draft): string {
  const params = new URLSearchParams({
    deliveryDay: draft.deliveryDay,
    decisionTime: draft.decisionTime,
    horizonHours: draft.horizonHours.toString(),
  });
  return `/api/export/review.csv?${params.toString()}`;
}


