"use client";

import { useMemo } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { Button } from "antd";
import { MinusOutlined, PlusOutlined, DeleteOutlined } from "@ant-design/icons";

import { useGetUserInfoUserInfoGet } from "@/types";
import { useCart } from "@/contexts/CartContext";
import {
  getDeviceItems,
  getPodsItems,
  UNIFIED_CHECKOUT_SESSION_KEY,
  type UnifiedCheckoutSessionPayload,
} from "@/types/unifiedCart";
import { DEVICE_PRICE_USD, DEFAULT_DEVICE_SHIPPING_USD, getFallbackQuote, MAX_CART_QUANTITY } from "@/types/cartCheckout";
import { PODS_PRICE_PER_BOX_USD, PODS_SHIPPING_USD, MAX_PODS_BOXES } from "@/types/podsCheckout";
import { getColorwayLabel, PODS_FLAVORS, PODS_NICOTINE_LEVELS } from "@/lib/puffyRules";
import type { PodsFlavorId, PodsNicotineId } from "@/types/podsCheckout";
import Header from "@/components/layout/Header";

function getFlavorLabel(flavorId: PodsFlavorId): string {
  return PODS_FLAVORS.find((f) => f.id === flavorId)?.label ?? flavorId;
}

function getNicotineLabel(nicotineId: PodsNicotineId): string {
  return PODS_NICOTINE_LEVELS.find((n) => n.id === nicotineId)?.label ?? nicotineId;
}

function isWlHolderFromUserInfo(userInfo: unknown): boolean {
  const u = userInfo as { nfts?: { status?: string }[] } | null | undefined;
  const nfts = u?.nfts?.filter((n) => n?.status !== "new");
  return Array.isArray(nfts) && nfts.length > 0;
}

export default function CartPage() {
  const router = useRouter();
  const { data: userInfo } = useGetUserInfoUserInfoGet({ query: { enabled: true } });
  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);
  const {
    items,
    updateItemAt,
    removeItemAt,
    deviceItemCount,
    podsBoxCount,
    itemCount,
    deviceQuote,
    deviceQuoteReq,
  } = useCart();

  const deviceItems = useMemo(() => getDeviceItems(items), [items]);
  const podsItems = useMemo(() => getPodsItems(items), [items]);

  const deviceSubtotal = useMemo(() => {
    if (deviceItemCount === 0) return 0;
    return wlHolder ? (deviceItemCount - 1) * DEVICE_PRICE_USD : deviceItemCount * DEVICE_PRICE_USD;
  }, [deviceItemCount, wlHolder]);
  const deviceShipping = deviceItemCount > 0 ? (deviceQuote?.shipping_usdt ?? DEFAULT_DEVICE_SHIPPING_USD) : 0;
  const podsSubtotal = podsItems.reduce((s, i) => s + PODS_PRICE_PER_BOX_USD * i.quantity, 0);
  const podsShipping = podsBoxCount > 0 ? PODS_SHIPPING_USD : 0;

  const subtotal = deviceSubtotal + podsSubtotal;
  const shipping = deviceShipping + podsShipping;
  const total = subtotal + shipping;

  // Enable whenever cart has items; use fallback quote if user came to cart without visiting device page
  const canProceedToCheckout = items.length > 0;

  const handleProceedToCheckout = () => {
    if (items.length === 0) return;
    const quote = deviceQuote ?? (deviceItemCount > 0 ? getFallbackQuote(wlHolder) : null);
    const req = deviceQuoteReq ?? (deviceItemCount > 0 ? { pay_device_with: "usdt" as const, pay_shipping_with: "usdt" as const } : null);
    const payload: UnifiedCheckoutSessionPayload = {
      cart: items,
      ...(deviceItemCount > 0 && quote && req ? { deviceQuote: quote, deviceQuoteReq: req } : {}),
    };
    try {
      sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(payload));
      router.push("/checkout");
    } catch {}
  };

  if (items.length === 0) {
    return (
      <div className="min-h-screen w-full flex flex-col bg-white">
        <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5 border-b border-black/5">
          <Header />
        </header>
        <div className="flex flex-1 flex-col items-center justify-center px-4 pb-8 md:px-6">
          <div className="text-center max-w-md">
            <h1 className="text-2xl font-semibold text-[#111111] mb-4">Your cart is empty</h1>
            <p className="text-black/60 mb-6">
              Looks like you haven't added anything to your cart yet.
            </p>
            <Link
              href="/device"
              className="inline-block rounded-full bg-black text-white px-8 py-3 text-sm font-medium hover:opacity-90"
            >
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full flex flex-col bg-white">
      <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5 border-b border-black/5">
        <Header />
      </header>

      <div className="flex flex-1 flex-col px-4 py-8 md:px-6 lg:px-10">
        <div className="mx-auto w-full max-w-6xl">
          {/* Header row */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-[#111111]">My Cart</h1>
          </div>

          <div className="grid lg:grid-cols-[1fr_380px] gap-8">
            {/* Left: Cart items */}
            <div className="flex flex-col gap-4">
              {items.map((item, index) => {
                if (item.type === "device") {
                  const canIncrease = deviceItemCount < MAX_CART_QUANTITY;
                  return (
                    <div
                      key={`device-${index}-${item.variant}-${item.colorway}`}
                      className="flex gap-4 p-4 rounded-2xl border border-black/10 bg-white"
                    >
                      {/* Image */}
                      <div className="w-24 h-24 md:w-32 md:h-32 rounded-xl bg-[#F5F5F5] flex items-center justify-center shrink-0 overflow-hidden">
                        <Image
                          src="/preorder/device_small.png"
                          alt="Puffy Device"
                          width={120}
                          height={120}
                          className="object-contain"
                        />
                      </div>

                      {/* Details */}
                      <div className="flex-1 min-w-0 flex flex-col">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <h3 className="text-base font-medium text-black">
                              Puffy 1 {item.variant === "vape" ? "Vape" : "Fresh"}
                            </h3>
                            <p className="text-sm text-black/60 mt-0.5">
                              {getColorwayLabel(item.colorway)}
                            </p>
                          </div>
                        </div>

                        <div className="mt-auto pt-3 flex items-end justify-between">
                          {/* Price */}
                          <div className="text-lg font-semibold text-black">
                            ${(DEVICE_PRICE_USD * item.quantity).toFixed(2)}
                          </div>

                          {/* Quantity controls */}
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => updateItemAt(index, -1)}
                              className="flex h-9 w-9 items-center justify-center rounded-full border border-black/20 text-black hover:bg-black/5 transition-colors"
                              aria-label="Decrease quantity"
                            >
                              <MinusOutlined className="text-xs" />
                            </button>
                            <span className="min-w-[2rem] text-center text-sm font-medium">
                              {item.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => updateItemAt(index, 1)}
                              disabled={!canIncrease}
                              className="flex h-9 w-9 items-center justify-center rounded-full border border-black/20 text-black hover:bg-black/5 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                              aria-label="Increase quantity"
                            >
                              <PlusOutlined className="text-xs" />
                            </button>
                            <button
                              type="button"
                              onClick={() => removeItemAt(index)}
                              className="ml-2 flex h-9 w-9 items-center justify-center rounded-full text-black/40 hover:text-red-600 hover:bg-red-50 transition-colors"
                              aria-label="Remove item"
                            >
                              <DeleteOutlined className="text-sm" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                }

                // Pods item
                const canIncrease = podsBoxCount < MAX_PODS_BOXES;
                return (
                  <div
                    key={`pods-${index}-${item.variant}-${item.flavor}-${item.variant === "vape" ? item.nicotine : "na"}`}
                    className="flex gap-4 p-4 rounded-2xl border border-black/10 bg-white"
                  >
                    {/* Image */}
                    <div className="w-24 h-24 md:w-32 md:h-32 rounded-xl bg-[#F5F5F5] flex items-center justify-center shrink-0 overflow-hidden">
                      <Image
                        src="/preorder/pod_small.png"
                        alt="Puffy Pods"
                        width={120}
                        height={120}
                        className="object-contain"
                      />
                    </div>

                    {/* Details */}
                    <div className="flex-1 min-w-0 flex flex-col">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h3 className="text-base font-medium text-black">
                            {item.variant === "fresh" ? "Puffy Fresh Pods" : "Puffy Vape Pods"}
                          </h3>
                          <p className="text-sm text-black/60 mt-0.5">
                            {getFlavorLabel(item.flavor)}
                            {item.variant === "vape" ? ` · ${getNicotineLabel(item.nicotine)}` : ""}
                          </p>
                        </div>
                      </div>

                      <div className="mt-auto pt-3 flex items-end justify-between">
                        {/* Price */}
                        <div>
                          <div className="text-lg font-semibold text-black">
                            ${(PODS_PRICE_PER_BOX_USD * item.quantity).toFixed(2)}
                          </div>
                          {item.quantity > 1 && (
                            <div className="text-xs text-black/50">
                              ${PODS_PRICE_PER_BOX_USD.toFixed(2)} each
                            </div>
                          )}
                        </div>

                        {/* Quantity controls */}
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => updateItemAt(index, -1)}
                            className="flex h-9 w-9 items-center justify-center rounded-full border border-black/20 text-black hover:bg-black/5 transition-colors"
                            aria-label="Decrease quantity"
                          >
                            <MinusOutlined className="text-xs" />
                          </button>
                          <span className="min-w-[2rem] text-center text-sm font-medium">
                            {item.quantity}
                          </span>
                          <button
                            type="button"
                            onClick={() => updateItemAt(index, 1)}
                            disabled={!canIncrease}
                            className="flex h-9 w-9 items-center justify-center rounded-full border border-black/20 text-black hover:bg-black/5 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                            aria-label="Increase quantity"
                          >
                            <PlusOutlined className="text-xs" />
                          </button>
                          <button
                            type="button"
                            onClick={() => removeItemAt(index)}
                            className="ml-2 flex h-9 w-9 items-center justify-center rounded-full text-black/40 hover:text-red-600 hover:bg-red-50 transition-colors"
                            aria-label="Remove item"
                          >
                            <DeleteOutlined className="text-sm" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Right: Order Summary */}
            <div className="lg:sticky lg:top-6 h-fit">
              <div className="rounded-2xl border border-black/10 bg-white p-5">
                <h2 className="text-lg font-semibold text-black mb-4">Order Summary</h2>

                <div className="space-y-3 text-sm">
                  <div className="flex justify-between text-black/70">
                    <span>Subtotal ({itemCount} {itemCount === 1 ? "item" : "items"})</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between text-black/70">
                    <span>Shipping</span>
                    <span>{shipping === 0 ? "Free" : `$${shipping.toFixed(2)}`}</span>
                  </div>
                </div>

                <div className="border-t border-black/10 mt-4 pt-4">
                  <div className="flex justify-between text-base font-semibold text-black">
                    <span>Total</span>
                    <span>${total.toFixed(2)}</span>
                  </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                  <Button
                    type="primary"
                    onClick={handleProceedToCheckout}
                    disabled={!canProceedToCheckout}
                    className="w-full rounded-full h-12 text-base font-medium"
                    style={{
                      background: canProceedToCheckout ? "black" : "rgba(0,0,0,0.25)",
                      borderColor: canProceedToCheckout ? "black" : "transparent",
                    }}
                  >
                    Continue to Checkout
                  </Button>
                  <Link
                    href="/device"
                    className="w-full text-center rounded-full h-12 flex items-center justify-center border border-black/20 text-black text-base font-medium hover:bg-black/5 transition-colors"
                  >
                    Continue Shopping
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
