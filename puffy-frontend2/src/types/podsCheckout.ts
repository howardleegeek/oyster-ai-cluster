/**
 * Smart Pods cart and checkout types.
 * Separate flow from device; no leasing program.
 */

/** Smart Pods flavor option id. */
export type PodsFlavorId = "peach_oolong" | "mint_ice" | "watermelon_ice";

/** Smart Pods product variant. */
export type PodsProductVariant = "vape" | "fresh";

/** Smart Pods nicotine level id. */
export type PodsNicotineId = "0" | "2";

/** Single line item in the pods cart (variant + flavor + quantity in boxes; nicotine only for vape). */
export type PodsLineItem =
  | {
      variant: "vape";
      flavor: PodsFlavorId;
      nicotine: PodsNicotineId;
      quantity: number; // boxes
    }
  | {
      variant: "fresh";
      flavor: PodsFlavorId;
      quantity: number; // boxes
    };

export type PodsCartState = PodsLineItem[];

/** SessionStorage key for pods checkout. */
export const PODS_CHECKOUT_SESSION_KEY = "puffy_pods_checkout_session";

/** Payload stored when navigating from pods page to pods checkout. */
export interface PodsCheckoutSessionPayload {
  cart: PodsLineItem[];
}

/** Fixed price per box of Smart Pods (6 pods/box) in USD. */
export const PODS_PRICE_PER_BOX_USD = 15;

/** Default shipping for pods order (used until price-fetch API is available). */
export const PODS_SHIPPING_USD = 5;

/** Max total boxes allowed in pods cart. */
export const MAX_PODS_BOXES = 20;

/** Live price for pods (subtotal + shipping). */
export interface PodsLivePrice {
  subtotal: number;
  shipping: number;
  total: number;
  currency: string;
}

export function getPodsCartTotalBoxes(cart: PodsLineItem[]): number {
  return cart.reduce((sum, item) => sum + item.quantity, 0);
}

export function getPodsLivePrice(totalBoxes: number): PodsLivePrice {
  const subtotal = totalBoxes * PODS_PRICE_PER_BOX_USD;
  const shipping = totalBoxes > 0 ? PODS_SHIPPING_USD : 0;
  return {
    subtotal,
    shipping,
    total: subtotal + shipping,
    currency: "USD",
  };
}
