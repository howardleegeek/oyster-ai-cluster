"use client";

import { useCallback, useEffect, useRef, useMemo, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { message, Button } from "antd";
import { CheckCircleFilled, CloseCircleFilled } from "@ant-design/icons";

import { useGetUserInfoUserInfoGet } from "@/types";
import { REFERRAL_CODE_KEY } from "@/hooks/reward-center/useCampaign";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { fluidSize } from "@/lib/utils";
import {
  getProductEligibility,
  getColorwaysForVariant,
  getDefaultColorway,
  getColorwayLabel,
  DELIVERY_COUNTRY_OPTIONS,
} from "@/lib/puffyRules";
import { useDeviceQuote } from "@/hooks/purchase/useDevicePurchase";
import {
  getLivePriceFromQuote,
  getFallbackQuote,
  MAX_CART_QUANTITY,
} from "@/types/cartCheckout";
import type { DeviceColorwayId } from "@/types/deviceEligibility";
import {
  useCart,
} from "@/contexts/CartContext";
import {
  getDeviceItems,
  UNIFIED_CHECKOUT_SESSION_KEY,
  type UnifiedCheckoutSessionPayload,
} from "@/types/unifiedCart";
import {
  PODS_PRICE_PER_BOX_USD,
  PODS_SHIPPING_USD,
} from "@/types/podsCheckout";
import { getDeviceImages } from "@/lib/productImages";
import ProductImageGallery from "@/components/product/ProductImageGallery";
import Header from "@/components/layout/Header";
import StickyCartBanner from "@/components/layout/StickyCartBanner";

function isWlHolderFromUserInfo(userInfo: any) {
  const nfts = userInfo?.nfts?.filter((n: any) => n?.status !== "new");
  return Array.isArray(nfts) && nfts.length > 0;
}

export default function DevicePurchasePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [api, contextHolder] = message.useMessage();
  const navigatingRef = useRef(false);

  const { data: userInfo } = useGetUserInfoUserInfoGet({
    query: { enabled: true },
  });

  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);
  const referralFromUrl = useMemo(() => {
    const v = searchParams.get(REFERRAL_CODE_KEY);
    return v ? decodeURIComponent(v) : "";
  }, [searchParams]);

  const [selectedVariant, setSelectedVariant] = useState<"vape" | "fresh">("vape");
  const [selectedColorway, setSelectedColorway] = useState<DeviceColorwayId>("black");
  const {
    items,
    setDeviceQuote,
    deviceQuote,
    deviceQuoteReq,
    addDeviceItem,
    updateItemAt,
    removeItemAt,
    deviceItemCount,
    podsBoxCount,
    itemCount,
  } = useCart();

  const [shipping, setShipping] = useState({
    name: "",
    email: userInfo?.email ?? "",
    phone: "",
    line1: "",
    line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "US",
  });

  // Keep email in sync once user info loads
  useEffect(() => {
    if (userInfo?.email) {
      setShipping((s) => ({ ...s, email: userInfo.email as string }));
    }
  }, [userInfo?.email]);

  const eligibility = useMemo(
    () => getProductEligibility({ countryCode: shipping.country }),
    [shipping.country]
  );

  // When country changes, if current selection is ineligible, switch to an eligible default
  useEffect(() => {
    if (!eligibility[selectedVariant].eligible) {
      setSelectedVariant("fresh");
    }
  }, [shipping.country, eligibility, selectedVariant]);

  // When variant or WL status changes, reset colorway to valid default
  useEffect(() => {
    setSelectedColorway((prev) => {
      const def = getDefaultColorway(selectedVariant, wlHolder);
      const options = getColorwaysForVariant(selectedVariant, wlHolder);
      const valid = options.some((o) => o.id === prev);
      return valid ? prev : def;
    });
  }, [selectedVariant, wlHolder]);

  const quoteReq = useMemo(
    () => ({
      device_pass_code: undefined,
      pay_device_with: wlHolder ? ("waived" as const) : ("usdt" as const),
      pay_shipping_with: "usdt" as const,
      referral_code: referralFromUrl.trim() || undefined,
    }),
    [wlHolder, referralFromUrl]
  );

  const quoteEnabled = true;

  const { data: quote, isFetching: isQuoteLoading, error: quoteError } =
    useDeviceQuote(quoteReq, quoteEnabled);

  const fallbackQuoteStable = useMemo(() => getFallbackQuote(wlHolder), [wlHolder]);
  const effectiveQuote = quote ?? (quoteError ? fallbackQuoteStable : (items.length >= 1 && deviceItemCount >= 1 && !isQuoteLoading ? fallbackQuoteStable : null));

  useEffect(() => {
    if (!effectiveQuote || !quoteReq) return;
    if (deviceQuote === effectiveQuote && deviceQuoteReq === quoteReq) return;
    setDeviceQuote(effectiveQuote, quoteReq);
  }, [effectiveQuote, quoteReq, setDeviceQuote, deviceQuote, deviceQuoteReq]);

  const cartTotalQty = deviceItemCount;
  // Use fallback quote for immediate price display while loading
  const livePriceQuote = effectiveQuote ?? fallbackQuoteStable;
  const livePrice = useMemo(
    () => getLivePriceFromQuote(livePriceQuote, false, cartTotalQty, wlHolder),
    [livePriceQuote, cartTotalQty, wlHolder]
  );
  const podsTotal =
    podsBoxCount > 0
      ? podsBoxCount * PODS_PRICE_PER_BOX_USD + PODS_SHIPPING_USD
      : 0;
  const combinedTotal = livePrice.total + podsTotal;
  const canAddMore = deviceItemCount < MAX_CART_QUANTITY;

  const canGoToCheckout = useMemo(
    () =>
      items.length >= 1 &&
      (deviceItemCount === 0 || !!(deviceQuote ?? effectiveQuote)),
    [items.length, deviceItemCount, deviceQuote, effectiveQuote]
  );

  const handleAddToCart = () => {
    if (!eligibility[selectedVariant].eligible || !canAddMore) return;
    addDeviceItem({
      variant: selectedVariant,
      colorway: selectedColorway,
      quantity: 1,
    });
    api.success({
      content: "Added to cart",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
  };

  const handleProceedToCheckout = useCallback(() => {
    if (navigatingRef.current) return;
    if (!canGoToCheckout || items.length === 0) return;
    const quote = deviceQuote ?? effectiveQuote;
    const req = deviceQuoteReq ?? quoteReq;
    if (deviceItemCount > 0 && (!quote || !req)) return;
    const payload: UnifiedCheckoutSessionPayload = {
      cart: items,
      ...(deviceItemCount > 0 && quote && req
        ? { deviceQuote: quote, deviceQuoteReq: req }
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
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  }, [
    canGoToCheckout,
    items,
    deviceItemCount,
    deviceQuote,
    deviceQuoteReq,
    effectiveQuote,
    quoteReq,
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
              images={getDeviceImages(selectedVariant)}
              alt={`Puffy-1 ${selectedVariant === "fresh" ? "Fresh" : "Vape"} Starter Kit`}
            />
          </div>
        </div>

        {/* Right: configuration + checkout */}
        <div className="flex flex-col gap-5 md:gap-6">
          {/* Title + price */}
          <div className="flex items-baseline justify-between gap-4">
            <div>
              <div
                className="text-[#111111] font-semibold"
                style={{ fontSize: fluidSize(22, 26) }}
              >
                Puffy-1 Starter Kit
              </div>
              <div
                className="text-black/50 mt-1"
                style={{ fontSize: fluidSize(11, 13) }}
              >
                Select your Puffy-1 Device, 3 Free Pods, 1 Puffy-1 NFT, plus exclusive
                rewards.
              </div>
            </div>
            <div
              className="text-[#111111] font-semibold"
              style={{ fontSize: fluidSize(18, 22) }}
            >
              $99
            </div>
          </div>

          {/* Delivery country — product eligibility updates based on this */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
            <div className="text-black font-medium mb-2 text-sm">Delivery country</div>
            <select
              value={shipping.country}
              onChange={(e) =>
                setShipping((s) => ({ ...s, country: e.target.value.trim() || "US" }))
              }
              className="w-full rounded-xl border border-black/10 bg-white px-3 py-2.5 text-sm text-[#111111] focus:outline-none focus:ring-2 focus:ring-black/10"
              aria-label="Delivery country"
            >
              {DELIVERY_COUNTRY_OPTIONS.map(({ code, name }) => (
                <option key={code} value={code}>
                  {name}
                </option>
              ))}
            </select>
          </div>

          {/* Select your Puffy-1 — eligibility and reason update when delivery country changes */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
            <div className="text-black font-medium mb-3">Select your Puffy-1</div>
            <div className="grid gap-3">
              <div>
                <button
                  type="button"
                  disabled={!eligibility.vape.eligible}
                  onClick={() => eligibility.vape.eligible && setSelectedVariant("vape")}
                  className={`w-full text-left rounded-2xl border-2 px-4 py-3 md:px-5 md:py-4 transition-colors ${
                    !eligibility.vape.eligible
                      ? "cursor-not-allowed border-black/10 bg-black/[0.03] opacity-80"
                      : selectedVariant === "vape"
                        ? "border-[#ED00ED] bg-pink-50/50"
                        : "border-black/10 bg-white"
                  }`}
                  aria-disabled={!eligibility.vape.eligible}
                >
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <div className="text-black font-medium" style={{ fontSize: 14 }}>
                        Puffy Vape
                      </div>
                      <div className="text-black/50 mt-1 text-xs">
                        For current Vaper who is looking for cessation, choose between 2%,
                        1%, no-nicotine.
                      </div>
                    </div>
                  </div>
                </button>
                {!eligibility.vape.eligible && (
                  <p className="mt-2 text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
                    Puffy Vape is only eligible for delivery in selected countries (e.g. US, UK, Canada, Australia). Choose Puffy Fresh or a different delivery country for this order.
                  </p>
                )}
              </div>
              <button
                type="button"
                disabled={!eligibility.fresh.eligible}
                onClick={() => eligibility.fresh.eligible && setSelectedVariant("fresh")}
                className={`w-full text-left rounded-2xl border-2 px-4 py-3 md:px-5 md:py-4 transition-colors ${
                  !eligibility.fresh.eligible
                    ? "cursor-not-allowed border-black/10 bg-black/[0.03] opacity-80"
                    : selectedVariant === "fresh"
                      ? "border-[#ED00ED] bg-pink-50/50"
                      : "border-black/10 bg-white"
                }`}
                aria-disabled={!eligibility.fresh.eligible}
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <div className="text-black font-medium" style={{ fontSize: 14 }}>
                      Puffy Fresh
                    </div>
                    <div className="text-black/50 mt-1 text-xs">
                      For everyone who wants to keep their oral health.
                    </div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Colorway — after product selection; WL gets community, non-WL gets default per variant */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
            <div className="text-black font-medium mb-3">Colorway</div>
            <div className="grid gap-2">
              {getColorwaysForVariant(selectedVariant, wlHolder).map((opt) => (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setSelectedColorway(opt.id)}
                  className={`w-full text-left rounded-2xl border-2 px-4 py-3 transition-colors ${
                    selectedColorway === opt.id
                      ? "border-[#ED00ED] bg-pink-50/50"
                      : "border-black/10 bg-white hover:border-black/20"
                  }`}
                >
                  <span className="text-black font-medium" style={{ fontSize: 14 }}>
                    {opt.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Add to cart */}
          <Button
            type="primary"
            onClick={handleAddToCart}
            disabled={!eligibility[selectedVariant].eligible || !canAddMore}
            className="w-full rounded-full"
            style={{
              height: 44,
              background:
                eligibility[selectedVariant].eligible && canAddMore
                  ? "black"
                  : "rgba(0,0,0,0.25)",
              borderColor:
                eligibility[selectedVariant].eligible && canAddMore
                  ? "black"
                  : "transparent",
            }}
          >
            Add to cart {!canAddMore && "(max 10)"}
          </Button>

        </div>
      </div>
      </div>

      <StickyCartBanner />
    </div>
  );
}

