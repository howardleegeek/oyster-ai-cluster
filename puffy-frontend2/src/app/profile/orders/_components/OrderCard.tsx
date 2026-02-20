"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import type { Order } from "@/types/order";
import OrderStatusBadge from "./OrderStatusBadge";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function OrderCard({ order }: { order: Order }) {
  const router = useRouter();
  const itemCount = order.items.reduce((sum, i) => sum + i.quantity, 0);
  const firstImage = order.items[0]?.image ?? "/preorder/device_small.png";

  return (
    <div
      onClick={() => router.push(`/profile/orders/${order.order_id}`)}
      className="w-full rounded-2xl border border-black/10 bg-white p-4 flex items-center gap-4 cursor-pointer hover:border-black/20 hover:shadow-sm transition-all active:scale-[0.99]"
    >
      {/* Product thumbnail */}
      <div className="w-14 h-14 md:w-16 md:h-16 rounded-lg bg-[#F5F5F5] border border-black/5 flex items-center justify-center shrink-0 overflow-hidden">
        <Image
          src={firstImage}
          alt="Product"
          width={64}
          height={64}
          className="object-contain"
        />
      </div>

      {/* Order info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-semibold text-black">
            #{order.order_id}
          </span>
          <OrderStatusBadge status={order.status} />
        </div>
        <div className="text-xs text-black/50 mt-1">
          {formatDate(order.created_at)} &middot; {itemCount} item
          {itemCount !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Total */}
      <div className="text-sm font-semibold text-black whitespace-nowrap">
        ${order.total.toFixed(2)}
      </div>

      {/* Arrow */}
      <svg
        className="w-4 h-4 text-black/30 shrink-0"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
      </svg>
    </div>
  );
}
