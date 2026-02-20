"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CheckCircleFilled } from "@ant-design/icons";

import { ORDER_CONFIRMATION_KEY, type OrderConfirmationPayload } from "@/types/unifiedCart";
import Header from "@/components/layout/Header";

export default function CheckoutSuccessPage() {
  const [data, setData] = useState<OrderConfirmationPayload | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = sessionStorage.getItem(ORDER_CONFIRMATION_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as OrderConfirmationPayload;
        setData(parsed);
      }
    } catch {
      setData(null);
    } finally {
      setChecked(true);
    }
  }, []);

  if (!checked) {
    return (
      <div className="min-h-screen w-full flex flex-col bg-white">
        <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5 border-b border-black/5">
          <Header />
        </header>
        <div className="flex flex-1 items-center justify-center py-16">
          <p className="text-black/60">Loading…</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen w-full flex flex-col bg-white">
        <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5 border-b border-black/5">
          <Header />
        </header>
        <div className="flex flex-1 flex-col items-center justify-center px-4 py-16">
          <p className="text-black/70 mb-6">No order confirmation found.</p>
          <Link
            href="/device"
            className="inline-block rounded-full bg-black text-white px-6 py-3 text-sm font-medium hover:opacity-90"
          >
            Continue shopping
          </Link>
        </div>
      </div>
    );
  }

  const primaryOrderId = data.orderIds[0] ?? "—";

  return (
    <div className="min-h-screen w-full flex flex-col bg-white">
      <header className="w-full z-10 px-4 py-4 md:px-6 md:py-5 border-b border-black/5">
        <Header />
      </header>

      <main className="flex flex-1 flex-col px-4 py-8 md:px-6 lg:px-10">
        <div className="mx-auto w-full max-w-2xl">
          {/* Pending confirmation header */}
          <div className="flex flex-col items-center text-center mb-10">
            <div className="w-16 h-16 rounded-full bg-[#FF2CFF]/15 flex items-center justify-center mb-4">
              <CheckCircleFilled className="text-3xl text-[#FF2CFF]" />
            </div>
            <h1 className="text-2xl font-semibold text-[#111111] mb-2">
              Awaiting blockchain confirmation
            </h1>
            <p className="text-black/70 mb-4">
              Your order has been placed and is being recorded on-chain.
            </p>
            <p className="text-sm text-black/60">
              Order number: <span className="font-medium text-black">{primaryOrderId}</span>
            </p>
            <Link
              href="/device"
              className="mt-4 text-sm text-[#FF2CFF] hover:underline"
            >
              You can check the status here
            </Link>
          </div>

          {/* Order summary */}
          <section className="rounded-2xl border border-black/10 bg-white p-5 mb-6">
            <h2 className="text-lg font-semibold text-black mb-4">Order summary</h2>
            <ul className="space-y-3 mb-4">
              {data.orderSummary.items.map((item, i) => (
                <li key={i} className="flex items-center justify-between text-sm">
                  <span className="text-black/80">
                    {item.label} × {item.quantity}
                  </span>
                  <span className="font-medium text-black">
                    ${(item.price * item.quantity).toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
            <div className="border-t border-black/10 pt-3 space-y-1 text-sm">
              <div className="flex justify-between text-black/70">
                <span>Subtotal</span>
                <span>${data.orderSummary.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-black/70">
                <span>Shipping</span>
                <span>
                  {data.orderSummary.shipping === 0
                    ? "Free"
                    : `$${data.orderSummary.shipping.toFixed(2)}`}
                </span>
              </div>
              <div className="flex justify-between font-semibold text-black pt-2">
                <span>Total</span>
                <span>${data.orderSummary.total.toFixed(2)}</span>
              </div>
            </div>
          </section>

          {/* User details */}
          <section className="rounded-2xl border border-black/10 bg-white p-5 space-y-5">
            <div>
              <h3 className="text-sm font-semibold text-black mb-1 flex items-center gap-2">
                <span className="text-black/50">Email</span>
              </h3>
              <p className="text-sm text-black/80">
                Order confirmation sent to {data.email}
              </p>
            </div>

            {data.walletAddress && (
              <div>
                <h3 className="text-sm font-semibold text-black mb-1">Wallet</h3>
                <p className="text-xs text-black/60 mb-1">
                  This wallet is used for rewards. Use a non-custodial wallet.
                </p>
                <p className="text-sm font-mono text-black/80 break-all">
                  {data.walletAddress.slice(0, 6)}…{data.walletAddress.slice(-4)}
                </p>
              </div>
            )}

            {data.referralCode && (
              <div>
                <h3 className="text-sm font-semibold text-black mb-1">Referral code</h3>
                <p className="text-sm text-black/80">{data.referralCode}</p>
              </div>
            )}

            <div>
              <h3 className="text-sm font-semibold text-black mb-1">Shipping address</h3>
              <p className="text-sm text-black/80">
                {data.shippingAddress.name}
                {data.shippingAddress.phone && ` · ${data.shippingAddress.phone}`}
                <br />
                {data.shippingAddress.line1}
                {data.shippingAddress.line2 && `, ${data.shippingAddress.line2}`}
                <br />
                {data.shippingAddress.city}
                {data.shippingAddress.state && `, ${data.shippingAddress.state}`}{" "}
                {data.shippingAddress.postal_code}
                <br />
                {data.shippingAddress.country}
              </p>
            </div>
          </section>

          <div className="mt-8 text-center">
            <Link
              href="/device"
              className="inline-block rounded-full bg-black text-white px-8 py-3 text-sm font-medium hover:opacity-90"
            >
              Continue shopping
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
