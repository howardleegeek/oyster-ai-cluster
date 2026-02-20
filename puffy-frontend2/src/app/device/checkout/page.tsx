"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  CHECKOUT_SESSION_KEY,
  type CheckoutSessionPayload,
} from "@/types/cartCheckout";
import {
  UNIFIED_CHECKOUT_SESSION_KEY,
  type UnifiedCartItem,
  type UnifiedCheckoutSessionPayload,
} from "@/types/unifiedCart";

export default function DeviceCheckoutRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(CHECKOUT_SESSION_KEY);
      if (raw) {
        const payload = JSON.parse(raw) as CheckoutSessionPayload;
        if (payload?.cart?.length && payload?.quote && payload?.quoteReq) {
          const cart: UnifiedCartItem[] = payload.cart.map((item) => ({
            type: "device",
            variant: item.variant,
            colorway: item.colorway,
            quantity: item.quantity,
          }));
          const unified: UnifiedCheckoutSessionPayload = {
            cart,
            deviceQuote: payload.quote,
            deviceQuoteReq: payload.quoteReq,
          };
          sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(unified));
          sessionStorage.removeItem(CHECKOUT_SESSION_KEY);
        }
      }
    } catch {}
    router.replace("/checkout");
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="text-black/60">Redirecting to checkout…</div>
    </div>
  );
}
