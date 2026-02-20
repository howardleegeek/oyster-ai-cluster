"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type {
  UnifiedCartItem,
  UnifiedDeviceItem,
  UnifiedPodsItem,
} from "@/types/unifiedCart";
import {
  CART_STORAGE_KEY,
  getDeviceItems,
  getPodsItems,
} from "@/types/unifiedCart";
import { MAX_CART_QUANTITY } from "@/types/cartCheckout";
import { MAX_PODS_BOXES } from "@/types/podsCheckout";
import type { DeviceQuoteRequest, DeviceQuoteResponse } from "@/lib/puffyPurchaseApi";

interface CartContextValue {
  items: UnifiedCartItem[];
  deviceQuote: DeviceQuoteResponse | null;
  deviceQuoteReq: DeviceQuoteRequest | null;
  setDeviceQuote: (quote: DeviceQuoteResponse | null, req: DeviceQuoteRequest | null) => void;
  addDeviceItem: (item: Omit<UnifiedDeviceItem, "type">) => void;
  addPodsItem: (item: Omit<UnifiedPodsItem, "type">) => void;
  updateItemAt: (index: number, delta: number) => void;
  removeItemAt: (index: number) => void;
  clearCart: () => void;
  deviceItemCount: number;
  podsBoxCount: number;
  itemCount: number;
}

const CartContext = createContext<CartContextValue | null>(null);

function loadCartFromStorage(): UnifiedCartItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as UnifiedCartItem[];
  } catch {
    return [];
  }
}

function saveCartToStorage(items: UnifiedCartItem[]) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  } catch {}
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<UnifiedCartItem[]>([]);
  const [deviceQuote, setDeviceQuoteState] = useState<DeviceQuoteResponse | null>(null);
  const [deviceQuoteReq, setDeviceQuoteReqState] = useState<DeviceQuoteRequest | null>(null);

  useLayoutEffect(() => {
    setItems(loadCartFromStorage());
  }, []);

  useEffect(() => {
    saveCartToStorage(items);
  }, [items]);

  const setDeviceQuote = useCallback(
    (quote: DeviceQuoteResponse | null, req: DeviceQuoteRequest | null) => {
      setDeviceQuoteState(quote);
      setDeviceQuoteReqState(req);
    },
    []
  );

  const deviceItems = useMemo(() => getDeviceItems(items), [items]);
  const podsItems = useMemo(() => getPodsItems(items), [items]);
  const deviceItemCount = useMemo(
    () => deviceItems.reduce((s, i) => s + i.quantity, 0),
    [deviceItems]
  );
  const podsBoxCount = useMemo(
    () => podsItems.reduce((s, i) => s + i.quantity, 0),
    [podsItems]
  );
  const itemCount = useMemo(
    () => items.reduce((s, i) => s + i.quantity, 0),
    [items]
  );

  const addDeviceItem = useCallback(
    (item: Omit<UnifiedDeviceItem, "type">) => {
      const full: UnifiedDeviceItem = { ...item, type: "device" };
      setItems((prev) => {
        const deviceOnly = getDeviceItems(prev);
        const totalDevice = deviceOnly.reduce((s, i) => s + i.quantity, 0);
        if (totalDevice >= MAX_CART_QUANTITY) return prev;
        const existing = prev.find(
          (i): i is UnifiedDeviceItem =>
            i.type === "device" &&
            i.variant === full.variant &&
            i.colorway === full.colorway
        );
        if (existing) {
          const newQty = Math.min(
            existing.quantity + full.quantity,
            MAX_CART_QUANTITY - totalDevice + existing.quantity
          );
          if (newQty <= existing.quantity) return prev;
          return prev.map((i) =>
            i.type === "device" &&
            i.variant === full.variant &&
            i.colorway === full.colorway
              ? { ...i, quantity: newQty }
              : i
          );
        }
        const toAdd = Math.min(full.quantity, MAX_CART_QUANTITY - totalDevice);
        return [...prev, { ...full, quantity: toAdd }];
      });
    },
    []
  );

  const addPodsItem = useCallback(
    (item: Omit<UnifiedPodsItem, "type">) => {
      const full: UnifiedPodsItem = { ...item, type: "pods" };
      setItems((prev) => {
        const podsOnly = getPodsItems(prev);
        const totalPods = podsOnly.reduce((s, i) => s + i.quantity, 0);
        if (totalPods >= MAX_PODS_BOXES) return prev;
        const existing = prev.find(
          (i): i is UnifiedPodsItem =>
            i.type === "pods" &&
            i.variant === full.variant &&
            i.flavor === full.flavor &&
            (full.variant === "fresh" ||
              (i.variant === "vape" &&
                full.variant === "vape" &&
                i.nicotine === full.nicotine))
        );
        if (existing) {
          const newQty = Math.min(
            existing.quantity + full.quantity,
            MAX_PODS_BOXES - totalPods + existing.quantity
          );
          if (newQty <= existing.quantity) return prev;
          return prev.map((i) =>
            i.type === "pods" &&
            i.variant === full.variant &&
            i.flavor === full.flavor &&
            (full.variant === "fresh" ||
              (i.variant === "vape" &&
                full.variant === "vape" &&
                i.nicotine === full.nicotine))
              ? { ...i, quantity: newQty }
              : i
          );
        }
        const toAdd = Math.min(full.quantity, MAX_PODS_BOXES - totalPods);
        return [...prev, { ...full, quantity: toAdd }];
      });
    },
    []
  );

  const updateItemAt = useCallback((index: number, delta: number) => {
    setItems((prev) => {
      const next = [...prev];
      const item = next[index];
      if (!item) return prev;
      const newQty = Math.max(0, item.quantity + delta);
      if (newQty === 0) {
        next.splice(index, 1);
        return next;
      }
      if (item.type === "device") {
        const deviceOnly = getDeviceItems(next);
        const totalOthers = deviceOnly.reduce((s, i) => s + i.quantity, 0) - item.quantity;
        item.quantity = Math.min(newQty, MAX_CART_QUANTITY - totalOthers);
      } else {
        const podsOnly = getPodsItems(next);
        const totalOthers = podsOnly.reduce((s, i) => s + i.quantity, 0) - item.quantity;
        item.quantity = Math.min(newQty, MAX_PODS_BOXES - totalOthers);
      }
      return next;
    });
  }, []);

  const removeItemAt = useCallback((index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const clearCart = useCallback(() => {
    setItems([]);
    setDeviceQuoteState(null);
    setDeviceQuoteReqState(null);
  }, []);

  const value = useMemo(
    () => ({
      items,
      deviceQuote,
      deviceQuoteReq,
      setDeviceQuote,
      addDeviceItem,
      addPodsItem,
      updateItemAt,
      removeItemAt,
      clearCart,
      deviceItemCount,
      podsBoxCount,
      itemCount,
    }),
    [
      items,
      deviceQuote,
      deviceQuoteReq,
      setDeviceQuote,
      addDeviceItem,
      addPodsItem,
      updateItemAt,
      removeItemAt,
      clearCart,
      deviceItemCount,
      podsBoxCount,
      itemCount,
    ]
  );

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
