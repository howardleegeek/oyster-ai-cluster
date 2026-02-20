"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { useOrderById } from "@/hooks/purchase/useOrders";
import OrderStatusBadge from "../_components/OrderStatusBadge";
import OrderItemRow from "../_components/OrderItemRow";
import OrderStatusTimeline from "../_components/OrderStatusTimeline";
import PackageCard from "../_components/PackageCard";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatShortDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const orderId = params.orderId as string;
  const { data: order, isLoading } = useOrderById(orderId);
  const [itemsExpanded, setItemsExpanded] = useState(true);

  if (isLoading) {
    return (
      <div className="w-full px-4 py-8">
        <p className="text-black/50 text-sm">Loading order...</p>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="w-full px-4 py-8">
        <Link
          href="/profile/orders"
          className="text-sm text-black/60 hover:text-black inline-flex items-center gap-1 mb-6"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to orders
        </Link>
        <div className="w-full rounded-2xl border border-black/10 bg-white p-8 text-center">
          <p className="text-black/60 mb-4">Order not found.</p>
          <Link
            href="/profile/orders"
            className="inline-block rounded-full bg-black text-white px-6 py-2.5 text-sm font-medium hover:opacity-90"
          >
            View all orders
          </Link>
        </div>
      </div>
    );
  }

  const itemCount = order.items.reduce((sum, i) => sum + i.quantity, 0);
  const hasPackages = order.packages && order.packages.length > 0;

  return (
    <div className="w-full px-4 py-6 md:py-8">
      {/* Back link */}
      <button
        onClick={() => router.push("/profile/orders")}
        className="text-sm text-black/60 hover:text-black inline-flex items-center gap-1 mb-4 bg-transparent border-0 p-0 cursor-pointer"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        Back to orders
      </button>

      {/* Order header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-6">
        <div>
          <h1 className="text-xl font-semibold text-black">
            Order #{order.order_id}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <OrderStatusBadge status={order.status} />
            <span className="text-xs text-black/50">
              {formatDate(order.created_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="flex flex-col lg:flex-row gap-4 lg:gap-6">
        {/* Left column */}
        <div className="flex-1 flex flex-col gap-4">
          {hasPackages ? (
            /* Packages view — each package is its own collapsible card */
            order.packages!.map((pkg) => (
              <PackageCard key={pkg.package_id} pkg={pkg} />
            ))
          ) : (
            /* Flat items view (no packages assigned yet) */
            <div className="rounded-2xl border border-black/10 bg-white p-4 md:p-5">
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setItemsExpanded(!itemsExpanded)}
              >
                <h2 className="text-base font-medium text-black">Items ordered</h2>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-black/50">
                    {itemCount} item{itemCount !== 1 ? "s" : ""}
                  </span>
                  <svg
                    className={`w-4 h-4 text-black/40 transition-transform ${
                      itemsExpanded ? "rotate-180" : ""
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              {itemsExpanded && (
                <div className="mt-3 divide-y divide-black/5">
                  {order.items.map((item, idx) => (
                    <OrderItemRow key={idx} item={item} />
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Order info */}
          <div className="rounded-2xl border border-black/10 bg-white p-4 md:p-5">
            <div className="flex flex-col sm:flex-row sm:items-start gap-4">
              <div className="flex-1">
                <div className="text-xs text-black/50 mb-1">Order date</div>
                <div className="text-sm font-medium text-black">
                  {formatShortDate(order.created_at)}
                </div>
              </div>
              <div className="flex-1">
                <div className="text-xs text-black/50 mb-1">Payment method</div>
                <div className="text-sm font-medium text-black">
                  {order.payment_method}
                </div>
              </div>
            </div>

            {/* Shipping address */}
            <div className="mt-4 pt-4 border-t border-black/5">
              <div className="text-xs text-black/50 mb-1">Shipping address</div>
              <div className="text-sm text-black/80">
                {order.shipping_address.name}
                {order.shipping_address.phone && ` · ${order.shipping_address.phone}`}
                <br />
                {order.shipping_address.line1}
                {order.shipping_address.line2 && `, ${order.shipping_address.line2}`}
                <br />
                {order.shipping_address.city}
                {order.shipping_address.state && `, ${order.shipping_address.state}`}{" "}
                {order.shipping_address.postal_code}
                <br />
                {order.shipping_address.country}
              </div>
            </div>
          </div>
        </div>

        {/* Right column (sidebar) */}
        <div className="w-full lg:w-[300px] flex flex-col gap-4 shrink-0">
          {/* Summary */}
          <div className="rounded-2xl border border-black/10 bg-white p-4 md:p-5">
            <h2 className="text-base font-medium text-black mb-3">Summary</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between text-black/70">
                <span>Subtotal</span>
                <span>${order.subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-black/70">
                <span>Shipping</span>
                <span>
                  {order.shipping === 0
                    ? "Free"
                    : `$${order.shipping.toFixed(2)}`}
                </span>
              </div>
              <div className="flex justify-between border-t border-black/5 pt-2 mt-2 font-semibold text-black">
                <span>Total</span>
                <span>${order.total.toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Order status */}
          <div className="rounded-2xl border border-black/10 bg-white p-4 md:p-5">
            <h2 className="text-base font-medium text-black mb-4">Order status</h2>
            <OrderStatusTimeline
              statusHistory={order.status_history}
              currentStatus={order.status}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
