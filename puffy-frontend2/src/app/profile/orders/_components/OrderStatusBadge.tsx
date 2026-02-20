"use client";

import type { OrderStatus } from "@/types/order";
import { ORDER_STATUS_LABELS } from "@/types/order";

const STATUS_COLORS: Record<OrderStatus, { bg: string; text: string }> = {
  created: { bg: "bg-gray-100", text: "text-gray-600" },
  payment_pending: { bg: "bg-amber-50", text: "text-amber-700" },
  paid: { bg: "bg-blue-50", text: "text-blue-700" },
  shipped: { bg: "bg-indigo-50", text: "text-indigo-700" },
  in_transit: { bg: "bg-purple-50", text: "text-purple-700" },
  delivered: { bg: "bg-green-50", text: "text-green-700" },
};

export default function OrderStatusBadge({ status }: { status: OrderStatus }) {
  const colors = STATUS_COLORS[status] ?? STATUS_COLORS.created;
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colors.bg} ${colors.text}`}
    >
      {ORDER_STATUS_LABELS[status] ?? status}
    </span>
  );
}
