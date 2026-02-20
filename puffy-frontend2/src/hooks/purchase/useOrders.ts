"use client";

import { useEffect, useState } from "react";
import {
  getOrders,
  getOrderById,
  generateMockOrders,
  ORDERS_STORAGE_KEY,
  MOCK_DATA_VERSION,
  type Order,
} from "@/types/order";

const MOCK_VERSION_KEY = "puffy_orders_mock_version";

/** Re-seed mock data when the version changes (dev convenience). */
function ensureMockData(): Order[] {
  const currentVersion = localStorage.getItem(MOCK_VERSION_KEY);
  if (currentVersion !== MOCK_DATA_VERSION) {
    localStorage.removeItem(ORDERS_STORAGE_KEY);
    localStorage.setItem(MOCK_VERSION_KEY, MOCK_DATA_VERSION);
    return generateMockOrders();
  }
  let orders = getOrders();
  if (orders.length === 0) {
    orders = generateMockOrders();
  }
  return orders;
}

/**
 * Hook that returns all orders from localStorage, sorted by date descending.
 * Seeds mock orders on first visit or when mock data version changes.
 */
export function useOrders() {
  const [data, setData] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let orders = ensureMockData();
    // Sort by created_at descending (newest first)
    orders.sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    setData(orders);
    setIsLoading(false);

    // Listen for storage changes from other tabs / checkout
    const handleStorage = (e: StorageEvent) => {
      if (e.key === ORDERS_STORAGE_KEY) {
        let updated = getOrders();
        updated.sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setData(updated);
      }
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  return { data, isLoading };
}

/**
 * Hook that returns a single order by ID from localStorage.
 */
export function useOrderById(orderId: string) {
  const [data, setData] = useState<Order | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    ensureMockData();
    const order = getOrderById(orderId);
    setData(order);
    setIsLoading(false);
  }, [orderId]);

  return { data, isLoading };
}
