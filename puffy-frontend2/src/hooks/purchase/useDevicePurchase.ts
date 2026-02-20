"use client";

import {
  createDeviceOrder,
  createDevicePass,
  createPodsOrder,
  getDevicePassSummary,
  getDeviceQuote,
  validateDevicePass,
  type CreateDeviceOrderRequest,
  type CreatePodsOrderRequest,
  type DeviceQuoteRequest,
} from "@/lib/puffyPurchaseApi";
import { useMutation, useQuery } from "@tanstack/react-query";

export function useDevicePassSummary(enabled: boolean) {
  return useQuery({
    queryKey: ["device-pass", "summary"],
    queryFn: getDevicePassSummary,
    enabled,
    staleTime: 10_000,
  });
}

export function useCreateDevicePass() {
  return useMutation({
    mutationFn: createDevicePass,
  });
}

export function useValidateDevicePass() {
  return useMutation({
    mutationFn: (code: string) => validateDevicePass(code),
  });
}

export function useDeviceQuote(req: DeviceQuoteRequest, enabled: boolean) {
  return useQuery({
    queryKey: ["device", "quote", req],
    queryFn: () => getDeviceQuote(req),
    enabled,
    staleTime: 30_000, // Cache quote for 30 seconds before refetching
    gcTime: 5 * 60_000, // Keep in cache for 5 minutes
  });
}

export function useCreateDeviceOrder() {
  return useMutation({
    mutationFn: (req: CreateDeviceOrderRequest) => createDeviceOrder(req),
  });
}

export function useCreatePodsOrder() {
  return useMutation({
    mutationFn: (req: CreatePodsOrderRequest) => createPodsOrder(req),
  });
}

