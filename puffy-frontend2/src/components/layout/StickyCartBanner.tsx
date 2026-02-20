"use client";

import { useMemo } from "react";
import { Button } from "antd";
import { useRouter } from "next/navigation";
import { useGetUserInfoUserInfoGet } from "@/types";
import { useCart } from "@/contexts/CartContext";
import { DEVICE_PRICE_USD, DEFAULT_DEVICE_SHIPPING_USD } from "@/types/cartCheckout";
import { PODS_PRICE_PER_BOX_USD, PODS_SHIPPING_USD } from "@/types/podsCheckout";

function isWlHolderFromUserInfo(userInfo: unknown): boolean {
  const u = userInfo as { nfts?: { status?: string }[] } | null | undefined;
  const nfts = u?.nfts?.filter((n) => n?.status !== "new");
  return Array.isArray(nfts) && nfts.length > 0;
}

export default function StickyCartBanner() {
  const router = useRouter();
  const { data: userInfo } = useGetUserInfoUserInfoGet({ query: { enabled: true } });
  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);
  const { items, itemCount, deviceItemCount, podsBoxCount, deviceQuote } = useCart();

  // WL: first Puffy-1 starter kit free, shipping still paid
  const deviceSubtotal = useMemo(() => {
    if (deviceItemCount === 0) return 0;
    return wlHolder ? (deviceItemCount - 1) * DEVICE_PRICE_USD : deviceItemCount * DEVICE_PRICE_USD;
  }, [deviceItemCount, wlHolder]);
  const deviceShipping = deviceItemCount > 0 ? (deviceQuote?.shipping_usdt ?? DEFAULT_DEVICE_SHIPPING_USD) : 0;
  const podsSubtotal = podsBoxCount * PODS_PRICE_PER_BOX_USD;
  const podsShipping = podsBoxCount > 0 ? PODS_SHIPPING_USD : 0;

  const total = deviceSubtotal + deviceShipping + podsSubtotal + podsShipping;

  const hasItems = items.length > 0;

  return (
    <>
      <div
        className="fixed bottom-0 left-0 right-0 z-20 border-t border-black/10 bg-white px-4 py-3 md:px-6 md:py-4 shadow-[0_-4px_12px_rgba(0,0,0,0.06)]"
        role="region"
        aria-label="Cart summary"
      >
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
          <div className="flex flex-col gap-0.5">
            <span className="text-sm text-black/60">
              {itemCount > 0
                ? `${itemCount} ${itemCount === 1 ? "item" : "items"} in cart · Total`
                : "Total"}
            </span>
            <span className="text-lg font-semibold text-black">
              ${total.toFixed(2)} USD
            </span>
          </div>
          <Button
            type="primary"
            onClick={() => router.push("/cart")}
            disabled={!hasItems}
            className="rounded-full px-6"
            style={{
              height: 44,
              background: hasItems ? "black" : "rgba(0,0,0,0.25)",
              borderColor: hasItems ? "black" : "transparent",
            }}
          >
            View cart
          </Button>
        </div>
        {items.length === 0 && (
          <p className="mt-2 text-[11px] text-black/50">
            Add items to your cart to continue.
          </p>
        )}
      </div>

      {/* Spacer so main content is not hidden behind sticky banner */}
      <div className="h-20 md:h-24" aria-hidden />
    </>
  );
}
