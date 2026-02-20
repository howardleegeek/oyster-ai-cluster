"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useWallet } from "@solana/wallet-adapter-react";
import { Input, ConfigProvider, message, Button, Checkbox } from "antd";
import { CheckCircleFilled, CloseCircleFilled } from "@ant-design/icons";

import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useGetUserInfoUserInfoGet } from "@/types";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import {
  useCreateDeviceOrder,
  useCreatePodsOrder,
  useValidateDevicePass,
} from "@/hooks/purchase/useDevicePurchase";
import type { CreateDeviceOrderRequest } from "@/lib/puffyPurchaseApi";
import { getDeviceQuote } from "@/lib/puffyPurchaseApi";
import {
  UNIFIED_CHECKOUT_SESSION_KEY,
  ORDER_CONFIRMATION_KEY,
  getDeviceItems,
  getPodsItems,
  type UnifiedCheckoutSessionPayload,
  type UnifiedDeviceItem,
  type UnifiedPodsItem,
  type OrderConfirmationPayload,
} from "@/types/unifiedCart";
import {
  DEVICE_PRICE_USD,
  DEFAULT_DEVICE_SHIPPING_USD,
  canPlaceOrder as canPlaceOrderFn,
} from "@/types/cartCheckout";
import {
  PODS_PRICE_PER_BOX_USD,
  PODS_SHIPPING_USD,
} from "@/types/podsCheckout";
import {
  DELIVERY_COUNTRY_OPTIONS,
  getColorwayLabel,
  getProductEligibility,
  PODS_FLAVORS,
  PODS_NICOTINE_LEVELS,
} from "@/lib/puffyRules";
import type { PodsFlavorId, PodsNicotineId } from "@/types/podsCheckout";
import { useCart } from "@/contexts/CartContext";
import Header from "@/components/layout/Header";
import AddressAutocomplete from "@/components/checkout/AddressAutocomplete";
import { saveOrder, type Order, type OrderLineItem } from "@/types/order";

function getFlavorLabel(flavorId: PodsFlavorId): string {
  return PODS_FLAVORS.find((f) => f.id === flavorId)?.label ?? flavorId;
}

function getNicotineLabel(nicotineId: PodsNicotineId): string {
  return PODS_NICOTINE_LEVELS.find((n) => n.id === nicotineId)?.label ?? nicotineId;
}

function isWlHolderFromUserInfo(userInfo: any) {
  const nfts = userInfo?.nfts?.filter((n: any) => n?.status !== "new");
  return Array.isArray(nfts) && nfts.length > 0;
}

function isShippingComplete(shipping: {
  name: string;
  email: string;
  line1: string;
  city: string;
  postal_code: string;
  country: string;
}): boolean {
  return (
    !!shipping.name.trim() &&
    !!shipping.email.trim() &&
    !!shipping.line1.trim() &&
    !!shipping.city.trim() &&
    !!shipping.postal_code.trim() &&
    !!shipping.country.trim()
  );
}

export default function UnifiedCheckoutPage() {
  const router = useRouter();
  const [api, contextHolder] = message.useMessage();
  const [session, setSession] = useState<UnifiedCheckoutSessionPayload | null>(null);
  const [sessionChecked, setSessionChecked] = useState(false);
  const { clearCart, removeItemAt, items: cartItems, deviceQuote: cartDeviceQuote, deviceQuoteReq: cartDeviceQuoteReq } = useCart();
  const { signin, logout } = useWalletLogin();
  const { publicKey } = useWallet();

  const { data: userInfo } = useGetUserInfoUserInfoGet({
    query: { enabled: true },
  });

  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);
  const displayWallet = useMemo(() => {
    const pk = publicKey?.toBase58();
    if (pk) return pk;
    if (typeof userInfo?.wallet_address === "string") return userInfo.wallet_address;
    return "";
  }, [publicKey, userInfo?.wallet_address]);

  const [devicePassCode, setDevicePassCode] = useState("");
  const [devicePassValid, setDevicePassValid] = useState<boolean | null>(null);
  const { mutateAsync: validatePass, isPending: isValidatingPass } = useValidateDevicePass();

  const handleValidatePass = async () => {
    const code = devicePassCode.trim();
    if (!code || !session?.deviceQuoteReq) return;
    setDevicePassValid(null);
    try {
      const res = await validatePass(code);
      setDevicePassValid(res.valid);
      if (res.valid) {
        const newQuote = await getDeviceQuote({
          ...session.deviceQuoteReq,
          device_pass_code: code,
          pay_device_with: "waived",
        });
        const updated: UnifiedCheckoutSessionPayload = {
          ...session,
          deviceQuote: newQuote,
          deviceQuoteReq: { ...session.deviceQuoteReq, device_pass_code: code, pay_device_with: "waived" },
        };
        setSession(updated);
        try {
          sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(updated));
        } catch {}
        api.success({
          content: "Device Pass applied. Device price is now $0 (shipping still applies).",
          ...NOTIFICATION_CONFIG,
          icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
        });
      } else {
        api.error({
          content: res.message || "Invalid or already-used Device Pass code.",
          ...NOTIFICATION_CONFIG,
          icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
        });
      }
    } catch (e: any) {
      setDevicePassValid(false);
      api.error({
        content: e?.response?.data?.detail || e?.message || "Failed to validate Device Pass.",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  };

  const [shipping, setShipping] = useState({
    name: "",
    email: (userInfo?.email as string) ?? "",
    phone: "",
    line1: "",
    line2: "",
    city: "",
    state: "",
    postal_code: "",
    country: "US",
  });

  const [referralCode, setReferralCode] = useState("");
  const [agreed, setAgreed] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = sessionStorage.getItem(UNIFIED_CHECKOUT_SESSION_KEY);
      if (!raw) {
        const deviceItemsFromCart = getDeviceItems(cartItems);
        const hasDeviceItems = deviceItemsFromCart.length > 0;
        const hasQuoteForDevice = !hasDeviceItems || (!!cartDeviceQuote && !!cartDeviceQuoteReq);
        if (cartItems.length > 0 && hasQuoteForDevice) {
          const payloadFromContext: UnifiedCheckoutSessionPayload = {
            cart: cartItems,
            ...(hasDeviceItems && cartDeviceQuote && cartDeviceQuoteReq
              ? { deviceQuote: cartDeviceQuote, deviceQuoteReq: cartDeviceQuoteReq }
              : {}),
          };
          try {
            sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(payloadFromContext));
          } catch {}
          setSession(payloadFromContext);
          setReferralCode(cartDeviceQuoteReq?.referral_code ?? "");
        } else {
          setSession(null);
        }
        setSessionChecked(true);
        return;
      }
      const payload = JSON.parse(raw) as UnifiedCheckoutSessionPayload;
      if (!payload?.cart?.length) {
        setSession(null);
        setSessionChecked(true);
        return;
      }
      const deviceItems = getDeviceItems(payload.cart);
      if (deviceItems.length > 0 && (!payload.deviceQuote || !payload.deviceQuoteReq)) {
        router.replace("/device");
        return;
      }
      setSession(payload);
      setReferralCode(payload.deviceQuoteReq?.referral_code ?? "");
    } catch {
      setSession(null);
      setSessionChecked(true);
    } finally {
      setSessionChecked(true);
    }
  }, [router, cartItems, cartDeviceQuote, cartDeviceQuoteReq]);

  useEffect(() => {
    if (userInfo?.email) {
      setShipping((s) => ({ ...s, email: userInfo.email as string }));
    }
  }, [userInfo?.email]);

  const shippingComplete = useMemo(() => isShippingComplete(shipping), [shipping]);
  const canProceedHere = !!session;
  const eligibility = useMemo(
    () => getProductEligibility({ countryCode: shipping.country }),
    [shipping.country]
  );
  const ineligibleCartIndices = useMemo(() => {
    if (!session?.cart) return new Set<number>();
    const set = new Set<number>();
    session.cart.forEach((item, index) => {
      if (item.type !== "device") return;
      const eligible =
        item.variant === "vape" ? eligibility.vape.eligible : eligibility.fresh.eligible;
      if (!eligible) set.add(index);
    });
    return set;
  }, [session?.cart, eligibility]);
  const hasIneligibleItems = ineligibleCartIndices.size > 0;
  const walletConnected = !!publicKey;
  const canPlaceOrder = useMemo(
    () =>
      !hasIneligibleItems &&
      canPlaceOrderFn({
        canProceedToCheckout: canProceedHere,
        walletConnected,
        shippingComplete,
        agreedToTerms: agreed,
      }),
    [hasIneligibleItems, canProceedHere, walletConnected, shippingComplete, agreed]
  );

  const { mutateAsync: createDeviceOrder, isPending: isCreatingDeviceOrder } =
    useCreateDeviceOrder();
  const { mutateAsync: createPodsOrder, isPending: isCreatingPodsOrder } =
    useCreatePodsOrder();
  const isCreatingOrder = isCreatingDeviceOrder || isCreatingPodsOrder;

  const handleRemoveItemAtCheckout = (index: number) => {
    if (!session?.cart || index < 0 || index >= session.cart.length) return;
    const newCart = session.cart.filter((_, i) => i !== index);
    if (newCart.length === 0) {
      try {
        sessionStorage.removeItem(UNIFIED_CHECKOUT_SESSION_KEY);
        clearCart();
      } catch {}
      router.replace("/device");
      return;
    }
    const deviceItemsLeft = getDeviceItems(newCart);
    const updated: UnifiedCheckoutSessionPayload = {
      ...session,
      cart: newCart,
      ...(deviceItemsLeft.length === 0
        ? { deviceQuote: undefined, deviceQuoteReq: undefined }
        : {}),
    };
    setSession(updated);
    try {
      sessionStorage.setItem(UNIFIED_CHECKOUT_SESSION_KEY, JSON.stringify(updated));
    } catch {}
    removeItemAt(index);
  };

  const handlePlaceOrder = async () => {
    if (!session) return;
    const deviceItems = getDeviceItems(session.cart);
    const podsItems = getPodsItems(session.cart);
    const shippingAddress = {
      name: shipping.name.trim(),
      email: shipping.email.trim(),
      phone: shipping.phone.trim() || undefined,
      line1: shipping.line1.trim(),
      line2: shipping.line2.trim() || undefined,
      city: shipping.city.trim(),
      state: shipping.state.trim() || undefined,
      postal_code: shipping.postal_code.trim(),
      country: shipping.country.trim(),
    };

    const mockOrders =
      typeof window !== "undefined" &&
      (process.env.NEXT_PUBLIC_MOCK_ORDERS === "true" || process.env.NEXT_PUBLIC_MOCK_ORDERS === "1");

    try {
      const orderIds: string[] = [];
      if (mockOrders) {
        if (deviceItems.length > 0) orderIds.push(`mock-device-${Date.now()}`);
        if (podsItems.length > 0) orderIds.push(`mock-pods-${Date.now()}`);
        if (orderIds.length === 0) orderIds.push(`mock-${Date.now()}`);
      } else {
        if (deviceItems.length > 0 && session.deviceQuote && session.deviceQuoteReq) {
          const devicePayload: CreateDeviceOrderRequest = {
            ...session.deviceQuoteReq,
            referral_code: referralCode.trim() || undefined,
            variant: deviceItems[0].variant,
            colorway: deviceItems[0].colorway,
            line_items: deviceItems.map((item: UnifiedDeviceItem) => ({
              variant: item.variant,
              colorway: item.colorway,
              quantity: item.quantity,
            })),
            shipping_address: shippingAddress,
          };
          const deviceRes = await createDeviceOrder(devicePayload);
          if (deviceRes?.order_id) orderIds.push(deviceRes.order_id);
        }
        if (podsItems.length > 0) {
          const podsRes = await createPodsOrder({
            line_items: podsItems.map((item: UnifiedPodsItem) => ({
              flavor: item.flavor,
              nicotine: item.variant === "vape" ? item.nicotine : "0",
              quantity: item.quantity,
            })),
            shipping_address: shippingAddress,
            referral_code: referralCode.trim() || undefined,
          });
          if (podsRes?.order_id) orderIds.push(podsRes.order_id);
        }
      }
      const deviceQty = deviceItems.reduce((s, i) => s + i.quantity, 0);
      const podsBoxes = podsItems.reduce((s, i) => s + i.quantity, 0);
      const deviceSubtotal = deviceQty > 0 ? (wlHolder ? (deviceQty - 1) * DEVICE_PRICE_USD : DEVICE_PRICE_USD * deviceQty) : 0;
      const deviceShipping = deviceQty > 0 ? (session.deviceQuote?.shipping_usdt ?? DEFAULT_DEVICE_SHIPPING_USD) : 0;
      const podsSubtotal = podsBoxes * PODS_PRICE_PER_BOX_USD;
      const podsShipping = podsBoxes > 0 ? PODS_SHIPPING_USD : 0;
      const subtotal = deviceSubtotal + podsSubtotal;
      const shippingTotal = deviceShipping + podsShipping;
      const total = subtotal + shippingTotal;
      const summaryItems: OrderConfirmationPayload["orderSummary"]["items"] = [];
      let deviceUnitsSeen = 0;
      deviceItems.forEach((item) => {
        const label = `Puffy 1 ${item.variant === "vape" ? "Vape" : "Fresh"} — ${getColorwayLabel(item.colorway)}`;
        if (wlHolder && deviceUnitsSeen === 0) {
          summaryItems.push({ label, quantity: 1, price: 0 });
          if (item.quantity > 1) summaryItems.push({ label, quantity: item.quantity - 1, price: DEVICE_PRICE_USD });
        } else {
          summaryItems.push({ label, quantity: item.quantity, price: DEVICE_PRICE_USD });
        }
        deviceUnitsSeen += item.quantity;
      });
      podsItems.forEach((item) => {
        const flavorLabel = getFlavorLabel(item.flavor);
        const nicLabel = item.variant === "vape" ? getNicotineLabel(item.nicotine) : "";
        summaryItems.push({
          label: item.variant === "vape" ? `Puffy Vape Pods — ${flavorLabel}${nicLabel ? ` · ${nicLabel}` : ""}` : `Puffy Fresh Pods — ${flavorLabel}`,
          quantity: item.quantity,
          price: PODS_PRICE_PER_BOX_USD,
        });
      });
      const confirmation: OrderConfirmationPayload = {
        orderIds,
        status: "payment_pending",
        email: shippingAddress.email,
        shippingAddress: {
          name: shippingAddress.name,
          phone: shippingAddress.phone,
          line1: shippingAddress.line1,
          line2: shippingAddress.line2,
          city: shippingAddress.city,
          state: shippingAddress.state,
          postal_code: shippingAddress.postal_code,
          country: shippingAddress.country,
        },
        orderSummary: {
          items: summaryItems,
          subtotal,
          shipping: shippingTotal,
          total,
        },
        referralCode: referralCode.trim() || undefined,
        walletAddress: displayWallet || undefined,
      };
      try {
        sessionStorage.setItem(ORDER_CONFIRMATION_KEY, JSON.stringify(confirmation));
        sessionStorage.removeItem(UNIFIED_CHECKOUT_SESSION_KEY);
        clearCart();
      } catch {}

      // Persist order to localStorage for the My Orders page
      try {
        const now = new Date().toISOString();
        const orderLineItems: OrderLineItem[] = [];
        deviceItems.forEach((item) => {
          orderLineItems.push({
            label: `Puffy 1 ${item.variant === "vape" ? "Vape" : "Fresh"} — ${getColorwayLabel(item.colorway)}`,
            productType: "device",
            variant: item.variant,
            colorway: item.colorway,
            quantity: item.quantity,
            unitPrice: DEVICE_PRICE_USD,
            image: "/preorder/device_small.png",
          });
        });
        podsItems.forEach((item) => {
          const flavorLabel = getFlavorLabel(item.flavor);
          const nicLabel = item.variant === "vape" ? getNicotineLabel(item.nicotine) : "";
          orderLineItems.push({
            label: item.variant === "vape"
              ? `Puffy Vape Pods — ${flavorLabel}${nicLabel ? ` · ${nicLabel}` : ""}`
              : `Puffy Fresh Pods — ${flavorLabel}`,
            productType: "pods",
            variant: item.variant,
            flavor: item.flavor,
            nicotine: item.variant === "vape" ? item.nicotine : undefined,
            quantity: item.quantity,
            unitPrice: PODS_PRICE_PER_BOX_USD,
            image: "/preorder/pod_small.png",
          });
        });
        orderIds.forEach((oid) => {
          const persistedOrder: Order = {
            order_id: oid,
            status: "payment_pending",
            created_at: now,
            items: orderLineItems,
            subtotal,
            shipping: shippingTotal,
            total,
            currency: "USD",
            shipping_address: {
              name: shippingAddress.name,
              email: shippingAddress.email,
              phone: shippingAddress.phone,
              line1: shippingAddress.line1,
              line2: shippingAddress.line2,
              city: shippingAddress.city,
              state: shippingAddress.state,
              postal_code: shippingAddress.postal_code,
              country: shippingAddress.country,
            },
            payment_method: "USDT (Solana)",
            status_history: [
              { status: "created", timestamp: now, description: "Order placed" },
              { status: "payment_pending", timestamp: now, description: "Awaiting blockchain confirmation" },
            ],
            wallet_address: displayWallet || undefined,
          };
          saveOrder(persistedOrder);
        });
      } catch {}

      api.success({
        content: mockOrders
          ? "Order placed (mock mode). Redirecting to confirmation."
          : "Order placed. Awaiting blockchain confirmation.",
        ...NOTIFICATION_CONFIG,
        icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
      });
      router.push("/checkout/success");
    } catch (e: unknown) {
      const err = e as {
        response?: { status?: number; config?: { url?: string }; data?: { detail?: string } };
        message?: string;
      };
      const status = err?.response?.status;
      const url = err?.response?.config?.url;
      let content = err?.response?.data?.detail || err?.message || "Failed to place order.";
      if (status === 404) {
        content = "Order API returned 404. The backend may not implement POST /device/orders or POST /pods/orders, or the base URL may be wrong.";
        if (url) content += ` Requested: ${url}`;
      }
      api.error({
        content,
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  };

  const isEmptyCart =
    !sessionChecked || !session || !session.cart || session.cart.length === 0;

  if (isEmptyCart) {
    return (
      <div className="min-h-screen w-full flex flex-col bg-white">
        <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5">
          <Header />
        </header>
        <div className="flex flex-1 flex-col px-4 pb-8 md:px-6">
          {contextHolder}
          <div className="mx-auto w-full max-w-2xl">
            <Link
              href="/device"
              className="text-sm text-black/60 hover:text-black mb-6 inline-block"
            >
              ← Back to shop
            </Link>
            <h1 className="text-xl font-semibold text-[#111111] mb-6">Checkout</h1>
            <div className="w-full rounded-3xl border border-black/10 bg-white p-6 md:p-8 text-center">
              <p className="text-black/70 mb-4">Your cart is empty.</p>
              <Link
                href="/device"
                className="inline-block rounded-full bg-black text-white px-6 py-3 text-sm font-medium hover:opacity-90"
              >
                Continue shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const deviceItems = getDeviceItems(session.cart);
  const podsItems = getPodsItems(session.cart);
  const deviceQty = deviceItems.reduce((s, i) => s + i.quantity, 0);
  const podsBoxes = podsItems.reduce((s, i) => s + i.quantity, 0);

  const deviceSubtotal = deviceQty > 0 ? (wlHolder ? (deviceQty - 1) * DEVICE_PRICE_USD : DEVICE_PRICE_USD * deviceQty) : 0;
  const deviceShipping = deviceQty > 0 ? (session.deviceQuote?.shipping_usdt ?? DEFAULT_DEVICE_SHIPPING_USD) : 0;
  const podsSubtotal = podsBoxes * PODS_PRICE_PER_BOX_USD;
  const podsShipping = podsBoxes > 0 ? PODS_SHIPPING_USD : 0;
  const orderTotal =
    deviceSubtotal + deviceShipping + podsSubtotal + podsShipping;

  return (
    <div className="min-h-screen w-full flex flex-col bg-white">
      <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5">
        <Header />
      </header>
      <div className="flex flex-1 flex-col px-4 pb-8 md:px-6">
        {contextHolder}
        <div className="mx-auto w-full max-w-2xl">
          <Link
            href="/device"
            className="text-sm text-black/60 hover:text-black mb-6 inline-block"
          >
            ← Back to shop
          </Link>

          <h1 className="text-xl font-semibold text-[#111111] mb-6">Checkout</h1>

          {/* Order summary — products and pricing first */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5 mb-6">
            <div className="flex flex-col gap-4">
              <div className="text-black font-medium mb-1">Order Summary</div>
              {hasIneligibleItems && (
                <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-xl px-3 py-2">
                  Some items are not available for delivery to{" "}
                  {DELIVERY_COUNTRY_OPTIONS.find((o) => o.code === shipping.country)?.name ??
                    shipping.country}
                  . Remove them to place your order.
                </p>
              )}
              <div className="flex flex-col gap-3">
                {session.cart.map((item, index) => {
                  const isIneligible = ineligibleCartIndices.has(index);
                  if (item.type === "device") {
                    const deviceUnitsBefore = session.cart
                      .slice(0, index)
                      .filter((i) => i.type === "device")
                      .reduce((s, i) => s + i.quantity, 0);
                    const paidQty = wlHolder && deviceUnitsBefore === 0
                      ? Math.max(0, item.quantity - 1)
                      : item.quantity;
                    const deviceLineTotal = paidQty * DEVICE_PRICE_USD;
                    return (
                      <div
                        key={`device-${index}-${item.variant}-${item.colorway}`}
                        className={`flex gap-3 items-start p-3 rounded-xl border ${
                          isIneligible ? "border-red-200 bg-red-50" : "border-black/10 bg-[#FAFAFA]"
                        }`}
                      >
                        <div className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-white border border-black/10 flex items-center justify-center shrink-0 overflow-hidden">
                          <Image
                            src="/preorder/device_small.png"
                            alt="Puffy Device"
                            width={80}
                            height={80}
                            className="object-contain"
                          />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className={`text-sm font-medium ${isIneligible ? "text-red-700" : "text-black"}`}>
                            Puffy 1 {item.variant === "vape" ? "Vape" : "Fresh"} —{" "}
                            {getColorwayLabel(item.colorway)}
                          </div>
                          {isIneligible && (
                            <div className="text-xs text-red-600 mt-1">
                              Not available for this country
                            </div>
                          )}
                          <div className="text-xs text-black/60 mt-1">
                            Quantity: {item.quantity}
                            {wlHolder && deviceUnitsBefore === 0 && item.quantity >= 1 && (
                              <span className="text-green-600"> · 1 free (Puffy Pass WL)</span>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1 shrink-0">
                          <div className={`text-sm font-medium ${isIneligible ? "text-red-700" : "text-black"}`}>
                            ${deviceLineTotal.toFixed(2)}
                          </div>
                          <Button
                            type="link"
                            size="small"
                            className="p-0 text-xs text-red-600 hover:text-red-700 h-auto"
                            onClick={() => handleRemoveItemAtCheckout(index)}
                          >
                            Remove
                          </Button>
                        </div>
                      </div>
                    );
                  }
                  return (
                    <div
                      key={`pods-${index}-${item.variant}-${item.flavor}-${item.variant === "vape" ? item.nicotine : "na"}`}
                      className="flex gap-3 items-start p-3 rounded-xl border border-black/10 bg-[#FAFAFA]"
                    >
                      <div className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-white border border-black/10 flex items-center justify-center shrink-0 overflow-hidden">
                        <Image
                          src="/preorder/pod_small.png"
                          alt="Puffy Pods"
                          width={80}
                          height={80}
                          className="object-contain"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-black">
                          {item.variant === "fresh" ? "Puffy Fresh Pods" : "Puffy Vape Pods"} —{" "}
                          {getFlavorLabel(item.flavor)}
                          {item.variant === "vape" ? ` — ${getNicotineLabel(item.nicotine)}` : ""}
                        </div>
                        <div className="text-xs text-black/60 mt-1">
                          {item.quantity} box{item.quantity !== 1 ? "es" : ""}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 shrink-0">
                        <div className="text-sm font-medium text-black">
                          ${(PODS_PRICE_PER_BOX_USD * item.quantity).toFixed(2)}
                        </div>
                        <Button
                          type="link"
                          size="small"
                          className="p-0 text-xs text-red-600 hover:text-red-700 h-auto"
                          onClick={() => handleRemoveItemAtCheckout(index)}
                        >
                          Remove
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="pt-3 border-t border-black/10 space-y-2 text-sm">
                <div className="flex justify-between text-black/70">
                  <span>Subtotal</span>
                  <span>${(deviceSubtotal + podsSubtotal).toFixed(2)}</span>
                </div>
                {(deviceShipping > 0 || podsShipping > 0) && (
                  <div className="flex justify-between text-black/70">
                    <span>Shipping</span>
                    <span>${(deviceShipping + podsShipping).toFixed(2)}</span>
                  </div>
                )}
                <div className="flex justify-between border-t border-black/5 pt-2 mt-2 font-semibold text-black">
                  <span>Total</span>
                  <span>${orderTotal.toFixed(2)}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Wallet / Payment */}
          <div className={`w-full rounded-3xl border ${walletConnected ? "border-black/10" : "border-amber-300 bg-amber-50/30"} bg-white p-4 md:p-5 mb-6`}>
            <div className="text-black font-medium mb-1">Payment</div>
            <div className="text-black/50 mb-3 text-xs">
              Connect your Solana wallet to pay with USDT.
            </div>
            <div className="flex flex-row gap-2 items-center">
              <div className="flex w-full items-center justify-between rounded-2xl border border-black/10 bg-[#FAFAFA] px-3 py-2.5">
                <div className="flex items-center gap-2">
                  {walletConnected ? (
                    <div className="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                  )}
                  <div className="text-sm text-black/70 truncate">
                    {walletConnected
                      ? `${displayWallet.slice(0, 6)}...${displayWallet.slice(-4)}`
                      : "No wallet connected"}
                  </div>
                </div>
                {walletConnected && (
                  <div className="text-[11px] text-green-600 font-medium">Connected</div>
                )}
              </div>
              <Button
                className="rounded-full flex items-center justify-center shrink-0"
                style={{
                  height: 36,
                  paddingInline: 20,
                  background: walletConnected ? "#FFFFFF" : "#000000",
                  color: walletConnected ? "#050505" : "#FFFFFF",
                  borderColor: walletConnected ? "#D9D9D9" : "#000000",
                  boxShadow: "none",
                }}
                onClick={() => (publicKey ? logout() : signin())}
              >
                {publicKey ? "Disconnect" : "Connect wallet"}
              </Button>
            </div>
            {!walletConnected && (
              <p className="mt-2 text-xs text-amber-700">
                You must connect a wallet to complete your purchase.
              </p>
            )}
          </div>

          {/* Shipping Address */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5 mb-6">
            <div className="text-black font-medium mb-1">Shipping Address</div>
            <div className="text-black/50 mb-4 text-xs md:text-[12px]">
              Address language should match the selected country.
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:gap-3">
              <Input
                value={shipping.name}
                onChange={(e) => setShipping((s) => ({ ...s, name: e.target.value }))}
                placeholder="Full name *"
              />
              <select
                value={shipping.country}
                onChange={(e) =>
                  setShipping((s) => ({
                    ...s,
                    country: e.target.value.trim() || "US",
                  }))
                }
                className="w-full rounded-md border border-black/10 bg-white px-3 py-2 text-sm text-[#111111] focus:outline-none focus:ring-2 focus:ring-black/10"
                aria-label="Country"
              >
                {DELIVERY_COUNTRY_OPTIONS.map(({ code, name }) => (
                  <option key={code} value={code}>
                    {name}
                  </option>
                ))}
              </select>
              <div className="md:col-span-2">
                <AddressAutocomplete
                  countryCode={shipping.country}
                  onSelect={(addr) =>
                    setShipping((s) => ({
                      ...s,
                      line1: addr.line1,
                      line2: addr.line2,
                      city: addr.city,
                      state: addr.state,
                      postal_code: addr.postal_code,
                      country: addr.country || s.country,
                    }))
                  }
                  placeholder="Search address (start typing to autocomplete)"
                  className="w-full"
                />
              </div>
              <Input
                value={shipping.line1}
                onChange={(e) => setShipping((s) => ({ ...s, line1: e.target.value }))}
                placeholder="Address Line 1 *"
                className="md:col-span-2"
              />
              <Input
                value={shipping.line2}
                onChange={(e) => setShipping((s) => ({ ...s, line2: e.target.value }))}
                placeholder="Address Line 2"
                className="md:col-span-2"
              />
              <Input
                value={shipping.city}
                onChange={(e) => setShipping((s) => ({ ...s, city: e.target.value }))}
                placeholder="City *"
              />
              <Input
                value={shipping.state}
                onChange={(e) => setShipping((s) => ({ ...s, state: e.target.value }))}
                placeholder="State/Province"
              />
              <Input
                value={shipping.postal_code}
                onChange={(e) =>
                  setShipping((s) => ({ ...s, postal_code: e.target.value }))
                }
                placeholder="Postal Code *"
              />
              <Input
                value={shipping.phone}
                onChange={(e) =>
                  setShipping((s) => ({ ...s, phone: e.target.value }))
                }
                placeholder="Phone Number"
              />
            </div>
            <div className="mt-4 grid grid-cols-1 gap-2">
              <Input
                value={shipping.email}
                onChange={(e) =>
                  setShipping((s) => ({ ...s, email: e.target.value }))
                }
                placeholder="Email *"
              />
            </div>
          </div>

          {/* Promotion */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5 mb-6">
            <div className="text-black font-medium mb-3 text-base leading-6">Promotion</div>
            {walletConnected && (
              <div className="flex items-center justify-between rounded-2xl border border-black/10 bg-[#FAFAFA] px-3 py-2 mb-3">
                <div className="text-xs text-black/70">Puffy Pass WL</div>
                <div className="text-[11px] font-medium" style={{ color: wlHolder ? "#16a34a" : "#9ca3af" }}>
                  {wlHolder ? "Eligible" : "Not eligible"}
                </div>
              </div>
            )}
            <div>
              <div className="text-black font-medium mb-2 text-sm">Have a Device Pass code?</div>
              <div className="flex gap-2 items-center">
                <ConfigProvider
                  theme={{
                    components: {
                      Input: {
                        colorPrimary: "black",
                        activeBorderColor: "transparent",
                        hoverBorderColor: "transparent",
                        activeShadow: "0 0 0 0px transparent",
                        boxShadow: "none",
                        borderRadius: 9999,
                      },
                    },
                  }}
                >
                  <Input
                    value={devicePassCode}
                    onChange={(e) => {
                      setDevicePassCode(e.target.value);
                      setDevicePassValid(null);
                    }}
                    placeholder="Enter one-time Device Pass code"
                    className="flex-1"
                  />
                </ConfigProvider>
                <Button
                  type="primary"
                  onClick={handleValidatePass}
                  disabled={!devicePassCode.trim() || isValidatingPass || !session?.deviceQuoteReq}
                  loading={isValidatingPass}
                  className="rounded-full shrink-0"
                  style={{
                    background: "#FFFFFF",
                    borderColor: "#D9D9D9",
                    color: "#000000",
                  }}
                >
                  Apply
                </Button>
              </div>
            </div>
          </div>

          {/* Referral, terms, and place order */}
          <div className="w-full rounded-3xl border border-black/10 bg-white p-4 md:p-5">
            <div className="flex flex-col gap-4">
              <div className="pt-1">
                <div className="text-black font-medium mb-1 text-sm">
                  Referral code (optional)
                </div>
                <ConfigProvider theme={{ components: { Input: { borderRadius: 9999 } } }}>
                  <Input
                    value={referralCode}
                    onChange={(e) => setReferralCode(e.target.value)}
                    placeholder="Enter a code from a friend"
                  />
                </ConfigProvider>
              </div>

              <div className="pt-2 border-t border-black/5">
                <Checkbox
                  checked={agreed}
                  onChange={(e) => setAgreed(e.target.checked)}
                  className="text-xs text-black/70"
                >
                  I acknowledge that this order is final and non-refundable.
                </Checkbox>
              </div>

              <Button
                type="primary"
                onClick={handlePlaceOrder}
                disabled={!canPlaceOrder || isCreatingOrder}
                loading={isCreatingOrder}
                className="rounded-full w-full"
                style={{
                  height: 44,
                  background: canPlaceOrder ? "black" : "rgba(0,0,0,0.25)",
                  borderColor: canPlaceOrder ? "black" : "transparent",
                }}
              >
                Place order
              </Button>
              {!walletConnected && (
                <p className="text-xs text-center text-amber-700 mt-2">
                  Please connect your wallet above to place your order.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
