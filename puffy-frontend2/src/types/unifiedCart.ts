/**
 * Unified cart: tracks both device and pods in one cart.
 */

import type { DeviceProductVariant, DeviceColorwayId } from "./deviceEligibility";
import type { PodsFlavorId, PodsNicotineId, PodsProductVariant } from "./podsCheckout";
import type { DeviceQuoteRequest, DeviceQuoteResponse } from "@/lib/puffyPurchaseApi";

/** Device line item in unified cart. */
export interface UnifiedDeviceItem {
  type: "device";
  variant: DeviceProductVariant;
  colorway: DeviceColorwayId;
  quantity: number;
}

/** Pods line item in unified cart. */
export type UnifiedPodsItem =
  | {
      type: "pods";
      variant: "vape";
      flavor: PodsFlavorId;
      nicotine: PodsNicotineId;
      quantity: number; // boxes
    }
  | {
      type: "pods";
      variant: "fresh";
      flavor: PodsFlavorId;
      quantity: number; // boxes
    };

/** Single item in the unified cart. */
export type UnifiedCartItem = UnifiedDeviceItem | UnifiedPodsItem;

export type UnifiedCartState = UnifiedCartItem[];

/** SessionStorage key for unified checkout. */
export const UNIFIED_CHECKOUT_SESSION_KEY = "puffy_unified_checkout_session";

/** Payload stored when navigating to unified checkout. */
export interface UnifiedCheckoutSessionPayload {
  cart: UnifiedCartItem[];
  /** Required when cart has device items. */
  deviceQuote?: DeviceQuoteResponse;
  deviceQuoteReq?: DeviceQuoteRequest;
}

/** localStorage key for persisting cart. */
export const CART_STORAGE_KEY = "puffy_cart";

/** SessionStorage key for order confirmation shown after place order (pending on-chain). */
export const ORDER_CONFIRMATION_KEY = "puffy_order_confirmation";

/** Payload stored after placing order, for the success/pending confirmation page. */
export interface OrderConfirmationPayload {
  orderIds: string[];
  status: "created" | "payment_pending" | "paid" | "failed";
  email: string;
  shippingAddress: {
    name: string;
    phone?: string;
    line1: string;
    line2?: string;
    city: string;
    state?: string;
    postal_code: string;
    country: string;
  };
  /** Snapshot of cart items for display (name, qty, price). */
  orderSummary: {
    items: { label: string; quantity: number; price: number }[];
    subtotal: number;
    shipping: number;
    total: number;
  };
  referralCode?: string;
  /** Wallet address if available for display. */
  walletAddress?: string;
}

/** Total number of "units" in cart (device count + pod boxes). */
export function getUnifiedCartItemCount(items: UnifiedCartItem[]): number {
  return items.reduce((sum, item) => sum + item.quantity, 0);
}

export function getDeviceItems(items: UnifiedCartItem[]): UnifiedDeviceItem[] {
  return items.filter((i): i is UnifiedDeviceItem => i.type === "device");
}

export function getPodsItems(items: UnifiedCartItem[]): UnifiedPodsItem[] {
  return items.filter((i): i is UnifiedPodsItem => i.type === "pods");
}
