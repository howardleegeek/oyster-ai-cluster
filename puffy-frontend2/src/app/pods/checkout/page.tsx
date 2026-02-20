"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  PODS_CHECKOUT_SESSION_KEY,
  type PodsCheckoutSessionPayload,
} from "@/types/podsCheckout";
import {
  UNIFIED_CHECKOUT_SESSION_KEY,
  type UnifiedCartItem,
  type UnifiedCheckoutSessionPayload,
} from "@/types/unifiedCart";

export default function PodsCheckoutRedirectPage() {
  const router = useRouter();

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(PODS_CHECKOUT_SESSION_KEY);
      if (raw) {
        const payload = JSON.parse(raw) as PodsCheckoutSessionPayload;
        if (payload?.cart?.length) {
          const cart: UnifiedCartItem[] = payload.cart.map((item: any) => {
            const variant = item?.variant === "fresh" ? "fresh" : "vape";
            if (variant === "fresh") {
              return {
                type: "pods",
                variant: "fresh",
                flavor: item.flavor,
                quantity: item.quantity,
              } as UnifiedCartItem;
            }
            return {
              type: "pods",
              variant: "vape",
              flavor: item.flavor,
              nicotine: item.nicotine ?? "0",
              quantity: item.quantity,
            } as UnifiedCartItem;
          });
          const unified: UnifiedCheckoutSessionPayload = { cart };
          sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(unified));
          sessionStorage.removeItem(PODS_CHECKOUT_SESSION_KEY);
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
