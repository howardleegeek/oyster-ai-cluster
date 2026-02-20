"use client";

import Image from "next/image";
import type { OrderLineItem } from "@/types/order";

export default function OrderItemRow({ item }: { item: OrderLineItem }) {
  const lineTotal = item.unitPrice * item.quantity;

  return (
    <div className="flex items-center gap-3 py-3">
      {/* Product thumbnail */}
      <div className="w-14 h-14 rounded-lg bg-[#F5F5F5] border border-black/5 flex items-center justify-center shrink-0 overflow-hidden">
        <Image
          src={item.image}
          alt={item.label}
          width={56}
          height={56}
          className="object-contain"
        />
      </div>

      {/* Product info */}
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-black truncate">
          {item.label}
        </div>
        {(item.colorway || item.flavor) && (
          <div className="text-xs text-black/50 mt-0.5">
            {[item.colorway, item.flavor, item.nicotine ? `${item.nicotine}mg` : null]
              .filter(Boolean)
              .join(" · ")}
          </div>
        )}
      </div>

      {/* Qty x price */}
      <div className="text-sm text-black/60 whitespace-nowrap">
        {item.quantity} &times; ${item.unitPrice.toFixed(2)}
      </div>

      {/* Line total */}
      <div className="text-sm font-medium text-black whitespace-nowrap min-w-[70px] text-right">
        ${lineTotal.toFixed(2)}
      </div>
    </div>
  );
}
