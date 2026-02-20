"use client";

import { useState } from "react";
import type { OrderPackage } from "@/types/order";
import { PACKAGE_STATUS_LABELS } from "@/types/order";
import OrderItemRow from "./OrderItemRow";

const PKG_STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  processing: { bg: "bg-gray-100", text: "text-gray-600" },
  shipped: { bg: "bg-indigo-50", text: "text-indigo-700" },
  in_transit: { bg: "bg-purple-50", text: "text-purple-700" },
  delivered: { bg: "bg-green-50", text: "text-green-700" },
};

export default function PackageCard({ pkg }: { pkg: OrderPackage }) {
  const [expanded, setExpanded] = useState(true);
  const colors = PKG_STATUS_COLORS[pkg.status] ?? PKG_STATUS_COLORS.processing;
  const itemCount = pkg.items.reduce((sum, i) => sum + i.quantity, 0);

  return (
    <div
      id={`pkg-${pkg.package_id}`}
      className="rounded-2xl border border-black/10 bg-white overflow-hidden"
    >
      {/* Header */}
      <div
        className="flex items-center justify-between p-4 md:p-5 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-black">{pkg.label}</span>
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium ${colors.bg} ${colors.text}`}
            >
              {PACKAGE_STATUS_LABELS[pkg.status]}
            </span>
          </div>
          {pkg.carrier && (
            <div className="text-xs text-black/50 mt-1">
              {pkg.carrier}
              {pkg.tracking_number && (
                <span className="ml-1">· {pkg.tracking_number}</span>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs text-black/50">
            {itemCount} item{itemCount !== 1 ? "s" : ""}
          </span>
          <svg
            className={`w-4 h-4 text-black/40 transition-transform ${
              expanded ? "rotate-180" : ""
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

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-black/5">
          {/* Items */}
          <div className="px-4 md:px-5 divide-y divide-black/5">
            {pkg.items.map((item, idx) => (
              <OrderItemRow key={idx} item={item} />
            ))}
          </div>

          {/* Tracking link */}
          {pkg.tracking_url && (
            <div className="px-4 md:px-5 py-3 border-t border-black/5">
              <a
                href={pkg.tracking_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full border border-black/10 px-3.5 py-1.5 text-xs font-medium text-black hover:bg-black/5 transition-colors"
              >
                <svg
                  className="w-3.5 h-3.5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                  />
                </svg>
                Track shipment
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
