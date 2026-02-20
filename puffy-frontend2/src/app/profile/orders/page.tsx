"use client";

import Link from "next/link";
import { useOrders } from "@/hooks/purchase/useOrders";
import OrderCard from "./_components/OrderCard";

export default function OrdersListPage() {
  const { data: orders, isLoading } = useOrders();

  if (isLoading) {
    return (
      <div className="w-full px-4 py-8">
        <p className="text-black/50 text-sm">Loading orders...</p>
      </div>
    );
  }

  return (
    <div className="w-full px-4 py-6 md:py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-black">
          My Orders
          {orders.length > 0 && (
            <span className="ml-2 text-sm font-normal text-black/50">
              ({orders.length})
            </span>
          )}
        </h1>
      </div>

      {orders.length === 0 ? (
        <div className="w-full rounded-2xl border border-black/10 bg-white p-8 text-center">
          <p className="text-black/60 mb-4">No orders yet.</p>
          <Link
            href="/device"
            className="inline-block rounded-full bg-black text-white px-6 py-2.5 text-sm font-medium hover:opacity-90 transition-opacity"
          >
            Start shopping
          </Link>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {orders.map((order) => (
            <OrderCard key={order.order_id} order={order} />
          ))}
        </div>
      )}
    </div>
  );
}
