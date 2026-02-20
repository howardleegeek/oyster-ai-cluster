"use client";

import type { OrderStatusEntry, OrderStatus } from "@/types/order";
import { ORDER_STATUS_FLOW, ORDER_STATUS_LABELS } from "@/types/order";

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface OrderStatusTimelineProps {
  statusHistory: OrderStatusEntry[];
  currentStatus: OrderStatus;
}

export default function OrderStatusTimeline({
  statusHistory,
  currentStatus,
}: OrderStatusTimelineProps) {
  // Build a map of completed statuses for quick lookup
  const completedMap = new Map<OrderStatus, OrderStatusEntry>();
  statusHistory.forEach((entry) => completedMap.set(entry.status, entry));

  const currentIdx = ORDER_STATUS_FLOW.indexOf(currentStatus);

  return (
    <div className="flex flex-col gap-0">
      {ORDER_STATUS_FLOW.map((status, idx) => {
        const entry = completedMap.get(status);
        const isCompleted = entry !== undefined;
        const isCurrent = status === currentStatus;
        const isFuture = idx > currentIdx;
        const isLast = idx === ORDER_STATUS_FLOW.length - 1;

        return (
          <div key={status} className="flex gap-3">
            {/* Vertical line + circle */}
            <div className="flex flex-col items-center">
              {/* Circle / checkmark */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 ${
                  isCompleted
                    ? "bg-green-500 text-white"
                    : isCurrent
                      ? "bg-black text-white"
                      : "bg-gray-200 text-gray-400"
                }`}
              >
                {isCompleted ? (
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={3}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  <div
                    className={`w-2 h-2 rounded-full ${
                      isFuture ? "bg-gray-300" : "bg-white"
                    }`}
                  />
                )}
              </div>
              {/* Connecting line */}
              {!isLast && (
                <div
                  className={`w-0.5 flex-1 min-h-[28px] ${
                    isCompleted && idx < currentIdx
                      ? "bg-green-500"
                      : "bg-gray-200"
                  }`}
                />
              )}
            </div>

            {/* Content */}
            <div className={`pb-4 ${isLast ? "pb-0" : ""}`}>
              <div
                className={`text-sm font-medium ${
                  isFuture ? "text-black/30" : "text-black"
                }`}
              >
                {ORDER_STATUS_LABELS[status]}
              </div>
              {entry?.description && (
                <div className="text-xs text-black/50 mt-0.5">
                  {entry.description}
                </div>
              )}
              {entry?.timestamp && (
                <div className="text-xs text-black/40 mt-0.5">
                  {formatDate(entry.timestamp)}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
