/**
 * Frontend state logic for sticky bottom cart banner and checkout flow.
 *
 * STICKY BOTTOM CART BANNER
 * -------------------------
 * - Live price: derived from current quote (device + shipping) or cart line items.
 *   Display: subtotal, shipping (if available), total. Update whenever quote or cart changes.
 *
 * - Checkout button enabled when:
 *   - User is authenticated
 *   - Cart has at least one (eligible) item
 *   - Quote is loaded (so we have a valid total)
 *   - Selected product is eligible for the chosen delivery country
 *   (No shipping address or agreement required to *proceed* to checkout; those are required on the checkout page to place order.)
 *
 * - Checkout button disabled when:
 *   - Not authenticated, or
 *   - Cart is empty, or
 *   - Quote not yet loaded / loading, or
 *   - Selected variant is ineligible for current country
 *
 * CHECKOUT PAGE
 * -------------
 * - Owns: shipping address form, order summary (confirm), referral code, terms checkbox, Place order.
 * - Place order button enabled only when: canProceedToCheckout + full shipping + agreed.
 */

import type {
  DeviceProductVariant,
  DeviceColorwayId,
} from "./deviceEligibility";
import type {
  DeviceQuoteRequest,
  DeviceQuoteResponse,
} from "@/lib/puffyPurchaseApi";

/**
 * Fallback quote when the quote API fails or is not yet called.
 * When wlHolder is true: 1 Puffy-1 starter kit is waived (device_price_usdt: 0), shipping still paid.
 */
export function getFallbackQuote(wlHolder?: boolean): DeviceQuoteResponse {
  const devicePrice = wlHolder ? 0 : DEVICE_PRICE_USD;
  return {
    device_price_usdt: devicePrice,
    device_price_points: 0,
    shipping_usdt: DEFAULT_DEVICE_SHIPPING_USD,
    shipping_points: 0,
    total_usdt: devicePrice + DEFAULT_DEVICE_SHIPPING_USD,
    total_points: 0,
    currency: "USDT",
  };
}

/** SessionStorage key for passing cart + quote from device page to checkout page. */
export const CHECKOUT_SESSION_KEY = "puffy_device_checkout_session";

/** Payload stored when navigating from device page to checkout. */
export interface CheckoutSessionPayload {
  quoteReq: DeviceQuoteRequest;
  quote: DeviceQuoteResponse;
  cart: CartLineItem[];
  /** First item variant/colorway for backward compatibility. */
  variant: DeviceProductVariant;
  colorway: DeviceColorwayId;
}

/** Single line item in the cart (extensible for multiple products). */
export interface CartLineItem {
  variant: DeviceProductVariant;
  colorway: DeviceColorwayId;
  quantity: number;
}

/** Cart state (array allows multiple products later). */
export type CartState = CartLineItem[];

/** Max total quantity allowed in cart (Puffy Vape + Puffy Fresh). */
export const MAX_CART_QUANTITY = 10;

/** Fixed price per starter kit (Puffy Vape and Puffy Fresh) in USD. */
export const DEVICE_PRICE_USD = 99;

/** Default shipping per device order (used until price-fetch API is available). */
export const DEFAULT_DEVICE_SHIPPING_USD = 8;

/** Live price display for the sticky banner (from quote + cart quantity). */
export interface LivePrice {
  /** Device/subtotal in display currency (device price × total quantity). */
  subtotal: number;
  /** Shipping (and customs if any) in display currency (one shipping per order). */
  shipping: number;
  /** Total in display currency. */
  total: number;
  /** Currency code for display (e.g. "USDT"). */
  currency: string;
  /** True when price is still loading (e.g. quote fetching). */
  isLoading: boolean;
}

/**
 * Total quantity across all cart line items.
 */
export function getCartTotalQuantity(cart: CartLineItem[]): number {
  return cart.reduce((sum, item) => sum + item.quantity, 0);
}

/**
 * Derives live price from the current quote and cart total quantity.
 * When isWlHolder: first Puffy-1 starter kit is free, additional devices at DEVICE_PRICE_USD; shipping always paid.
 */
export function getLivePriceFromQuote(
  quote: DeviceQuoteResponse | null | undefined,
  isQuoteLoading: boolean,
  totalQuantity: number = 1,
  isWlHolder?: boolean
): LivePrice {
  if (!quote) {
    return {
      subtotal: 0,
      shipping: 0,
      total: 0,
      currency: "USDT",
      isLoading: isQuoteLoading,
    };
  }
  const qty = Math.max(0, totalQuantity);
  const deviceSubtotal =
    qty === 0
      ? 0
      : isWlHolder
        ? (qty - 1) * DEVICE_PRICE_USD
        : qty * (quote.device_price_usdt ?? DEVICE_PRICE_USD);
  const shipping = qty === 0 ? 0 : quote.shipping_usdt;
  const total = deviceSubtotal + shipping;
  return {
    subtotal: deviceSubtotal,
    shipping,
    total,
    currency: quote.currency,
    isLoading: isQuoteLoading,
  };
}

/**
 * True when the user can proceed to checkout (sticky banner button enabled).
 * Does NOT require wallet connection; shipping address and terms are required on the checkout page.
 */
export function canProceedToCheckout(flags: {
  hasQuote: boolean;
  isQuoteLoading: boolean;
  cartNotEmpty: boolean;
  selectedVariantEligible: boolean;
}): boolean {
  return (
    flags.cartNotEmpty &&
    flags.selectedVariantEligible &&
    flags.hasQuote &&
    !flags.isQuoteLoading
  );
}

/**
 * True when the user can place the order on the checkout page.
 * Requires everything from canProceedToCheckout plus wallet connection,
 * full shipping, and agreement.
 */
export function canPlaceOrder(flags: {
  canProceedToCheckout: boolean;
  walletConnected: boolean;
  shippingComplete: boolean;
  agreedToTerms: boolean;
}): boolean {
  return (
    flags.canProceedToCheckout &&
    flags.walletConnected &&
    flags.shippingComplete &&
    flags.agreedToTerms
  );
}
