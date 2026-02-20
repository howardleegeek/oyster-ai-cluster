"use client";

import { useCallback, useEffect, useRef, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { Button, message } from "antd";
import { CheckCircleFilled } from "@ant-design/icons";

import { fluidSize } from "@/lib/utils";
import {
  PODS_FLAVORS,
  PODS_NICOTINE_LEVELS,
  PODS_QUANTITY_OPTIONS,
} from "@/lib/puffyRules";
import {
  getPodsLivePrice,
  PODS_PRICE_PER_BOX_USD,
  MAX_PODS_BOXES,
} from "@/types/podsCheckout";
import type { PodsFlavorId, PodsNicotineId, PodsProductVariant } from "@/types/podsCheckout";
import { useGetUserInfoUserInfoGet } from "@/types";
import { useCart } from "@/contexts/CartContext";
import {
  UNIFIED_CHECKOUT_SESSION_KEY,
  type UnifiedCheckoutSessionPayload,
  type UnifiedPodsItem,
} from "@/types/unifiedCart";
import { DEVICE_PRICE_USD, DEFAULT_DEVICE_SHIPPING_USD } from "@/types/cartCheckout";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { getPodsImages } from "@/lib/productImages";
import ProductImageGallery from "@/components/product/ProductImageGallery";
import Header from "@/components/layout/Header";
import StickyCartBanner from "@/components/layout/StickyCartBanner";

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

export default function PodsPage() {
  const router = useRouter();
  const [api, contextHolder] = message.useMessage();
  const navigatingRef = useRef(false);
  const { data: userInfo } = useGetUserInfoUserInfoGet({ query: { enabled: true } });
  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);
  const [selectedVariant, setSelectedVariant] = useState<PodsProductVariant>("vape");
  const [selectedFlavor, setSelectedFlavor] = useState<PodsFlavorId>("peach_oolong");
  const [selectedNicotine, setSelectedNicotine] = useState<PodsNicotineId>("0");
  const [selectedQuantity, setSelectedQuantity] = useState<number>(1);
  const {
    items,
    addPodsItem,
    deviceItemCount,
    deviceQuote,
    deviceQuoteReq,
    podsBoxCount,
    itemCount,
  } = useCart();

  const totalBoxes = podsBoxCount;
  const livePrice = useMemo(() => getPodsLivePrice(totalBoxes), [totalBoxes]);
  const canAddMore = totalBoxes < MAX_PODS_BOXES;

  const handleAddToCart = () => {
    if (!canAddMore) return;
    const room = MAX_PODS_BOXES - totalBoxes;
    const qtyToAdd = Math.min(selectedQuantity, room);
    if (qtyToAdd <= 0) return;
    addPodsItem(
      (selectedVariant === "fresh"
        ? {
            variant: "fresh" as const,
            flavor: selectedFlavor,
            quantity: qtyToAdd,
          }
        : {
            variant: "vape" as const,
            flavor: selectedFlavor,
            nicotine: selectedNicotine,
            quantity: qtyToAdd,
          }) as Omit<UnifiedPodsItem, "type">
    );
    api.success({
      content: "Added to cart",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
  };

  const deviceTotal =
    deviceItemCount > 0
      ? (wlHolder ? (deviceItemCount - 1) * DEVICE_PRICE_USD : DEVICE_PRICE_USD * deviceItemCount) +
        (deviceQuote?.shipping_usdt ?? DEFAULT_DEVICE_SHIPPING_USD)
      : 0;
  const combinedTotal = livePrice.total + deviceTotal;

  const handleProceedToCheckout = useCallback(() => {
    if (navigatingRef.current) return;
    if (items.length === 0) return;
    if (deviceItemCount > 0 && (!deviceQuote || !deviceQuoteReq)) {
      api.error({
        content: "Visit the device page to refresh pricing, then checkout.",
        ...NOTIFICATION_CONFIG,
      });
      return;
    }
    const payload: UnifiedCheckoutSessionPayload = {
      cart: items,
      ...(deviceItemCount > 0 && deviceQuote && deviceQuoteReq
        ? { deviceQuote, deviceQuoteReq }
        : {}),
    };
    try {
      sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(payload));
      navigatingRef.current = true;
      router.push("/checkout");
    } catch (e) {
      api.error({
        content: "Could not proceed to checkout. Please try again.",
        ...NOTIFICATION_CONFIG,
      });
    }
  }, [
    items,
    deviceItemCount,
    deviceQuote,
    deviceQuoteReq,
    api,
    router,
  ]);

  useEffect(() => {
    const onPageShow = () => {
      navigatingRef.current = false;
    };
    window.addEventListener("pageshow", onPageShow);
    return () => window.removeEventListener("pageshow", onPageShow);
  }, []);

  const canGoToCheckout =
    items.length >= 1 &&
    (deviceItemCount === 0 || (!!deviceQuote && !!deviceQuoteReq));

  return (
    <div className="w-full flex flex-col bg-white">
      <header
        className="w-full z-10"
        style={{ padding: fluidSize(16, 24) }}
      >
        <Header />
      </header>

      <div className="w-full flex justify-center flex-1">
        {contextHolder}
        <div className="w-full max-w-6xl px-4 md:px-8 lg:px-10 py-10 md:py-16 grid md:grid-cols-[minmax(0,1.05fr)_minmax(0,1.4fr)] gap-10">
          {/* Left: product visual */}
          <div className="flex items-start justify-center">
            <div className="w-full max-w-md">
              <ProductImageGallery
                images={getPodsImages(selectedVariant)}
                alt={`Puffy ${selectedVariant === "fresh" ? "Fresh" : "Vape"} Smart Pods`}
              />
            </div>
          </div>

          {/* Right: configuration */}
          <div className="flex flex-col gap-5 md:gap-6">
            <div className="flex items-baseline justify-between gap-4">
              <div>
                <div
                  className="text-[#111111] font-semibold"
                  style={{ fontSize: fluidSize(22, 26) }}
                >
                  Smart Pods
                </div>
                <div
                  className="text-black/50 mt-1"
                  style={{ fontSize: fluidSize(11, 13) }}
                >
                  6 pods per box · 5ml · 0.8 Ω · Food-grade materials
                </div>
              </div>
              <div
                className="text-[#111111] font-semibold"
                style={{ fontSize: fluidSize(18, 22) }}
              >
                ${PODS_PRICE_PER_BOX_USD}/box
              </div>
            </div>

            {/* Pods type */}
            <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
              <div className="text-black font-medium mb-3">Pods type</div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setSelectedVariant("vape")}
                  className={`rounded-2xl border-2 px-4 py-3 text-left transition-colors ${
                    selectedVariant === "vape"
                      ? "border-[#ED00ED] bg-pink-50/50"
                      : "border-black/10 bg-white hover:border-black/20"
                  }`}
                >
                  <div className="text-black font-medium text-sm">Puffy Vape Pods</div>
                  <div className="text-black/50 text-xs mt-0.5">Choose nicotine level</div>
                </button>
                <button
                  type="button"
                  onClick={() => setSelectedVariant("fresh")}
                  className={`rounded-2xl border-2 px-4 py-3 text-left transition-colors ${
                    selectedVariant === "fresh"
                      ? "border-[#ED00ED] bg-pink-50/50"
                      : "border-black/10 bg-white hover:border-black/20"
                  }`}
                >
                  <div className="text-black font-medium text-sm">Puffy Fresh Pods</div>
                  <div className="text-black/50 text-xs mt-0.5">No nicotine selection</div>
                </button>
              </div>
            </div>

            {/* Flavor */}
            <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
              <div className="text-black font-medium mb-3">Flavor</div>
              <div className="grid gap-2">
                {PODS_FLAVORS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setSelectedFlavor(opt.id)}
                    className={`w-full text-left rounded-2xl border-2 px-4 py-3 transition-colors ${
                      selectedFlavor === opt.id
                        ? "border-[#ED00ED] bg-pink-50/50"
                        : "border-black/10 bg-white hover:border-black/20"
                    }`}
                  >
                    <span className="text-black font-medium text-sm">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Nicotine level (Vape Pods only) */}
            {selectedVariant === "vape" && (
              <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
                <div className="text-black font-medium mb-3">Nicotine level</div>
                <div className="flex gap-2 flex-wrap">
                  {PODS_NICOTINE_LEVELS.map((opt) => (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setSelectedNicotine(opt.id)}
                      className={`rounded-2xl border-2 px-4 py-3 transition-colors ${
                        selectedNicotine === opt.id
                          ? "border-[#ED00ED] bg-pink-50/50"
                          : "border-black/10 bg-white hover:border-black/20"
                      }`}
                    >
                      <span className="text-black font-medium text-sm">{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Quantity (boxes) */}
            <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
              <div className="text-black font-medium mb-3">Quantity (boxes)</div>
              <div className="flex flex-wrap gap-2">
                {PODS_QUANTITY_OPTIONS.map((qty) => (
                  <button
                    key={qty}
                    type="button"
                    onClick={() => setSelectedQuantity(qty)}
                    className={`rounded-2xl border-2 px-4 py-3 transition-colors ${
                      selectedQuantity === qty
                        ? "border-[#ED00ED] bg-pink-50/50"
                        : "border-black/10 bg-white hover:border-black/20"
                    }`}
                  >
                    <span className="text-black font-medium text-sm">
                      {qty} {qty === 1 ? "box" : "boxes"}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <Button
              type="primary"
              onClick={handleAddToCart}
              disabled={!canAddMore}
              className="w-full rounded-full"
              style={{
                height: 44,
                background: canAddMore ? "black" : "rgba(0,0,0,0.25)",
                borderColor: canAddMore ? "black" : "transparent",
              }}
            >
              Add to cart {!canAddMore && "(max 20 boxes)"}
            </Button>
          </div>
        </div>
      </div>

      <StickyCartBanner />
    </div>
  );
}
