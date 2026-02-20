"use client";

import type {
  OrderStatusEntry,
  OrderStatus,
  OrderPackage,
  PackageStatus,
  PackageStatusEntry,
} from "@/types/order";
import {
  ORDER_STATUS_LABELS,
  PACKAGE_STATUS_FLOW,
  PACKAGE_STATUS_LABELS,
} from "@/types/order";

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** The order-level steps we render before the per-package section. */
const ORDER_LEVEL_STEPS: OrderStatus[] = ["created", "payment_pending", "paid"];

/* ------------------------------------------------------------------ */
/* Sub-components                                                      */
/* ------------------------------------------------------------------ */

/** A single step circle + optional connecting line. */
function StepCircle({
  completed,
  active,
  future,
  last,
  lineColor,
  size = "md",
}: {
  completed: boolean;
  active: boolean;
  future: boolean;
  last: boolean;
  lineColor?: string;
  size?: "md" | "sm";
}) {
  const dim = size === "sm" ? "w-5 h-5" : "w-6 h-6";
  const checkSize = size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5";
  const dotSize = size === "sm" ? "w-1.5 h-1.5" : "w-2 h-2";
  const minH = size === "sm" ? "min-h-[24px]" : "min-h-[28px]";

  return (
    <div className="flex flex-col items-center">
      <div
        className={`${dim} rounded-full flex items-center justify-center shrink-0 ${
          completed
            ? "bg-green-500 text-white"
            : active
              ? "bg-black text-white"
              : "bg-gray-200 text-gray-400"
        }`}
      >
        {completed ? (
          <svg
            className={checkSize}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={3}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <div
            className={`${dotSize} rounded-full ${future ? "bg-gray-300" : "bg-white"}`}
          />
        )}
      </div>
      {!last && (
        <div
          className={`w-0.5 flex-1 ${minH} ${lineColor ?? "bg-gray-200"}`}
        />
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Package section                                                     */
/* ------------------------------------------------------------------ */

function PackageSection({
  pkg,
  isLastPackage,
}: {
  pkg: OrderPackage;
  isLastPackage: boolean;
}) {
  const completedMap = new Map<PackageStatus, PackageStatusEntry>();
  pkg.status_history.forEach((e) => completedMap.set(e.status, e));
  const currentIdx = PACKAGE_STATUS_FLOW.indexOf(pkg.status);

  return (
    <div className="mt-1">
      {/* Package label */}
      <div className="flex items-center gap-2 mb-2 ml-9">
        <span className="text-xs font-semibold text-black/70">{pkg.label}</span>
        {pkg.carrier && (
          <span className="text-[11px] text-black/40">· {pkg.carrier}</span>
        )}
      </div>

      {/* Package steps */}
      {PACKAGE_STATUS_FLOW.map((status, idx) => {
        const entry = completedMap.get(status);
        const isCompleted = entry !== undefined;
        const isFuture = idx > currentIdx;
        const isLastStep =
          idx === PACKAGE_STATUS_FLOW.length - 1 && isLastPackage;

        return (
          <div key={`${pkg.package_id}-${status}`} className="flex gap-3">
            <StepCircle
              completed={isCompleted}
              active={false}
              future={isFuture}
              last={isLastStep}
              lineColor={
                isCompleted && idx < currentIdx ? "bg-green-500" : undefined
              }
              size="sm"
            />
            <div className={`pb-3 ${isLastStep ? "pb-0" : ""}`}>
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

/* ------------------------------------------------------------------ */
/* Main component                                                      */
/* ------------------------------------------------------------------ */

interface CombinedStatusTimelineProps {
  statusHistory: OrderStatusEntry[];
  currentStatus: OrderStatus;
  packages?: OrderPackage[];
}

export default function CombinedStatusTimeline({
  statusHistory,
  currentStatus,
  packages,
}: CombinedStatusTimelineProps) {
  const completedMap = new Map<OrderStatus, OrderStatusEntry>();
  statusHistory.forEach((e) => completedMap.set(e.status, e));

  const currentIdx = ORDER_LEVEL_STEPS.indexOf(
    ORDER_LEVEL_STEPS.includes(currentStatus) ? currentStatus : "paid",
  );

  const hasPackages = packages && packages.length > 0;

  return (
    <div className="flex flex-col gap-0">
      {/* ---- Order-level steps (Created → Payment Pending → Paid) ---- */}
      {ORDER_LEVEL_STEPS.map((status, idx) => {
        const entry = completedMap.get(status);
        const isCompleted = entry !== undefined;
        const isCurrent = status === currentStatus;
        const isFuture = !isCompleted && !isCurrent;
        // The last order-level step gets a line only if packages follow
        const isLastOrderStep = idx === ORDER_LEVEL_STEPS.length - 1;
        const showLine = !isLastOrderStep || hasPackages;

        return (
          <div key={status} className="flex gap-3">
            <StepCircle
              completed={isCompleted}
              active={isCurrent && !isCompleted}
              future={isFuture}
              last={!showLine}
              lineColor={
                isCompleted && idx < currentIdx ? "bg-green-500" : undefined
              }
            />
            <div className={`pb-4 ${!showLine ? "pb-0" : ""}`}>
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

      {/* ---- Per-package shipping steps ---- */}
      {hasPackages &&
        packages!.map((pkg, idx) => (
          <PackageSection
            key={pkg.package_id}
            pkg={pkg}
            isLastPackage={idx === packages!.length - 1}
          />
        ))}
    </div>
  );
}
