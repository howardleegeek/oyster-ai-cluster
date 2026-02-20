"use client";

import type { PackageStatusEntry, PackageStatus } from "@/types/order";
import { PACKAGE_STATUS_FLOW, PACKAGE_STATUS_LABELS } from "@/types/order";

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

interface PackageStatusTimelineProps {
  statusHistory: PackageStatusEntry[];
  currentStatus: PackageStatus;
}

export default function PackageStatusTimeline({
  statusHistory,
  currentStatus,
}: PackageStatusTimelineProps) {
  const completedMap = new Map<PackageStatus, PackageStatusEntry>();
  statusHistory.forEach((entry) => completedMap.set(entry.status, entry));

  const currentIdx = PACKAGE_STATUS_FLOW.indexOf(currentStatus);

  return (
    <div className="flex flex-col gap-0">
      {PACKAGE_STATUS_FLOW.map((status, idx) => {
        const entry = completedMap.get(status);
        const isCompleted = entry !== undefined;
        const isFuture = idx > currentIdx;
        const isLast = idx === PACKAGE_STATUS_FLOW.length - 1;

        return (
          <div key={status} className="flex gap-3">
            {/* Vertical line + circle */}
            <div className="flex flex-col items-center">
              <div
                className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                  isCompleted
                    ? "bg-green-500 text-white"
                    : "bg-gray-200 text-gray-400"
                }`}
              >
                {isCompleted ? (
                  <svg
                    className="w-3 h-3"
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
                    className={`w-1.5 h-1.5 rounded-full ${
                      isFuture ? "bg-gray-300" : "bg-white"
                    }`}
                  />
                )}
              </div>
              {!isLast && (
                <div
                  className={`w-0.5 flex-1 min-h-[24px] ${
                    isCompleted && idx < currentIdx
                      ? "bg-green-500"
                      : "bg-gray-200"
                  }`}
                />
              )}
            </div>

            {/* Content */}
            <div className={`pb-3 ${isLast ? "pb-0" : ""}`}>
              <div
                className={`text-xs font-medium ${
                  isFuture ? "text-black/30" : "text-black"
                }`}
              >
                {PACKAGE_STATUS_LABELS[status]}
              </div>
              {entry?.description && (
                <div className="text-[11px] text-black/50 mt-0.5">
                  {entry.description}
                </div>
              )}
              {entry?.timestamp && (
                <div className="text-[11px] text-black/40 mt-0.5">
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
