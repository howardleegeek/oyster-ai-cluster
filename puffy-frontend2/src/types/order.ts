/**
 * Purchase order model, localStorage helpers, and mock data generator.
 */

// ---------------------------------------------------------------------------
// Status
// ---------------------------------------------------------------------------

export type OrderStatus =
  | "created"
  | "payment_pending"
  | "paid"
  | "shipped"
  | "in_transit"
  | "delivered";

/** Ordered list of all statuses for timeline rendering. */
export const ORDER_STATUS_FLOW: OrderStatus[] = [
  "created",
  "payment_pending",
  "paid",
  "shipped",
  "in_transit",
  "delivered",
];

export const ORDER_STATUS_LABELS: Record<OrderStatus, string> = {
  created: "Created",
  payment_pending: "Payment Pending",
  paid: "Paid",
  shipped: "Shipped",
  in_transit: "In Transit",
  delivered: "Delivered",
};

export interface OrderStatusEntry {
  status: OrderStatus;
  timestamp: string; // ISO-8601
  description?: string;
}

// ---------------------------------------------------------------------------
// Package status (per-package tracking, independent of order-level status)
// ---------------------------------------------------------------------------

export type PackageStatus = "processing" | "shipped" | "in_transit" | "delivered";

export const PACKAGE_STATUS_FLOW: PackageStatus[] = [
  "processing",
  "shipped",
  "in_transit",
  "delivered",
];

export const PACKAGE_STATUS_LABELS: Record<PackageStatus, string> = {
  processing: "Processing",
  shipped: "Shipped",
  in_transit: "In Transit",
  delivered: "Delivered",
};

export interface PackageStatusEntry {
  status: PackageStatus;
  timestamp: string; // ISO-8601
  description?: string;
}

// ---------------------------------------------------------------------------
// Line item
// ---------------------------------------------------------------------------

export interface OrderLineItem {
  label: string;
  /** "device" or "pods" */
  productType: "device" | "pods";
  variant?: string;
  colorway?: string;
  flavor?: string;
  nicotine?: string;
  quantity: number;
  unitPrice: number;
  /** Path to product thumbnail in /public */
  image: string;
}

// ---------------------------------------------------------------------------
// Shipping address (mirrors puffyPurchaseApi.ShippingAddress)
// ---------------------------------------------------------------------------

export interface OrderShippingAddress {
  name: string;
  email?: string;
  phone?: string;
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
}

// ---------------------------------------------------------------------------
// Package (per-shipment grouping within an order)
// ---------------------------------------------------------------------------

export interface OrderPackage {
  package_id: string;
  /** Display label, e.g. "Package 1 of 2" */
  label: string;
  status: PackageStatus;
  carrier?: string;
  tracking_number?: string;
  tracking_url?: string;
  /** Line items shipped in this package */
  items: OrderLineItem[];
  status_history: PackageStatusEntry[];
}

// ---------------------------------------------------------------------------
// Order
// ---------------------------------------------------------------------------

export interface Order {
  order_id: string;
  status: OrderStatus;
  created_at: string; // ISO-8601
  items: OrderLineItem[];
  subtotal: number;
  shipping: number;
  total: number;
  currency: string;
  shipping_address: OrderShippingAddress;
  payment_method: string;
  status_history: OrderStatusEntry[];
  wallet_address?: string;
  /** When present, items are grouped into separate shipment packages. */
  packages?: OrderPackage[];
}

// ---------------------------------------------------------------------------
// localStorage helpers
// ---------------------------------------------------------------------------

export const ORDERS_STORAGE_KEY = "puffy_orders";

/** Bump this whenever mock data shape changes to force a re-seed in dev. */
export const MOCK_DATA_VERSION = "4";

export function getOrders(): Order[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(ORDERS_STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Order[];
  } catch {
    return [];
  }
}

export function getOrderById(orderId: string): Order | undefined {
  return getOrders().find((o) => o.order_id === orderId);
}

export function saveOrder(order: Order): void {
  if (typeof window === "undefined") return;
  const orders = getOrders();
  const existing = orders.findIndex((o) => o.order_id === order.order_id);
  if (existing >= 0) {
    orders[existing] = order;
  } else {
    orders.push(order);
  }
  localStorage.setItem(ORDERS_STORAGE_KEY, JSON.stringify(orders));
}

// ---------------------------------------------------------------------------
// Mock data generator
// ---------------------------------------------------------------------------

function daysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString();
}

export function generateMockOrders(): Order[] {
  const mockOrders: Order[] = [
    {
      order_id: "PFY-100234",
      status: "delivered",
      created_at: daysAgo(14),
      items: [
        {
          label: "Puffy 1 Vape — Black",
          productType: "device",
          variant: "vape",
          colorway: "black",
          quantity: 1,
          unitPrice: 99,
          image: "/preorder/device_small.png",
        },
        {
          label: "Puffy Vape Pods — Peach Oolong",
          productType: "pods",
          variant: "vape",
          flavor: "peach_oolong",
          nicotine: "2",
          quantity: 2,
          unitPrice: 15,
          image: "/preorder/pod_small.png",
        },
      ],
      subtotal: 129,
      shipping: 13,
      total: 142,
      currency: "USD",
      shipping_address: {
        name: "Alice W.",
        email: "alice@example.com",
        phone: "+1 555-0100",
        line1: "123 Blockchain Ave",
        city: "San Francisco",
        state: "CA",
        postal_code: "94105",
        country: "US",
      },
      payment_method: "USDT (Solana)",
      status_history: [
        { status: "created", timestamp: daysAgo(14), description: "Order placed" },
        { status: "payment_pending", timestamp: daysAgo(14), description: "Awaiting blockchain confirmation" },
        { status: "paid", timestamp: daysAgo(14), description: "Payment confirmed on-chain" },
        { status: "shipped", timestamp: daysAgo(10), description: "Your order has been shipped" },
        { status: "in_transit", timestamp: daysAgo(7), description: "Packages in transit" },
        { status: "delivered", timestamp: daysAgo(2), description: "All packages delivered" },
      ],
      packages: [
        {
          package_id: "PKG-100234-1",
          label: "Package 1 of 2",
          status: "delivered",
          carrier: "DHL Express",
          tracking_number: "DHL1234567890",
          tracking_url: "https://www.dhl.com/track?id=DHL1234567890",
          items: [
            {
              label: "Puffy 1 Vape — Black",
              productType: "device",
              variant: "vape",
              colorway: "black",
              quantity: 1,
              unitPrice: 99,
              image: "/preorder/device_small.png",
            },
          ],
          status_history: [
            { status: "processing", timestamp: daysAgo(14), description: "Preparing shipment" },
            { status: "shipped", timestamp: daysAgo(10), description: "Picked up by DHL Express" },
            { status: "in_transit", timestamp: daysAgo(7), description: "In transit — San Francisco hub" },
            { status: "delivered", timestamp: daysAgo(2), description: "Delivered to recipient" },
          ],
        },
        {
          package_id: "PKG-100234-2",
          label: "Package 2 of 2",
          status: "delivered",
          carrier: "USPS",
          tracking_number: "USPS9876543210",
          tracking_url: "https://tools.usps.com/go/TrackConfirmAction?tLabels=USPS9876543210",
          items: [
            {
              label: "Puffy Vape Pods — Peach Oolong",
              productType: "pods",
              variant: "vape",
              flavor: "peach_oolong",
              nicotine: "2",
              quantity: 2,
              unitPrice: 15,
              image: "/preorder/pod_small.png",
            },
          ],
          status_history: [
            { status: "processing", timestamp: daysAgo(13), description: "Preparing shipment" },
            { status: "shipped", timestamp: daysAgo(11), description: "Picked up by USPS" },
            { status: "in_transit", timestamp: daysAgo(8), description: "In transit" },
            { status: "delivered", timestamp: daysAgo(3), description: "Delivered to mailbox" },
          ],
        },
      ],
    },
    {
      order_id: "PFY-100289",
      status: "shipped",
      created_at: daysAgo(5),
      items: [
        {
          label: "Puffy 1 Fresh — Silver",
          productType: "device",
          variant: "fresh",
          colorway: "silver",
          quantity: 1,
          unitPrice: 99,
          image: "/preorder/device_small.png",
        },
      ],
      subtotal: 99,
      shipping: 8,
      total: 107,
      currency: "USD",
      shipping_address: {
        name: "Bob T.",
        email: "bob@example.com",
        line1: "456 Crypto Lane",
        city: "Austin",
        state: "TX",
        postal_code: "73301",
        country: "US",
      },
      payment_method: "USDT (Solana)",
      status_history: [
        { status: "created", timestamp: daysAgo(5), description: "Order placed" },
        { status: "payment_pending", timestamp: daysAgo(5), description: "Awaiting blockchain confirmation" },
        { status: "paid", timestamp: daysAgo(5), description: "Payment confirmed on-chain" },
        { status: "shipped", timestamp: daysAgo(3), description: "Your order has been shipped" },
      ],
      packages: [
        {
          package_id: "PKG-100289-1",
          label: "Package 1 of 1",
          status: "shipped",
          carrier: "FedEx",
          tracking_number: "FDX7778889990",
          tracking_url: "https://www.fedex.com/fedextrack/?trknbr=FDX7778889990",
          items: [
            {
              label: "Puffy 1 Fresh — Silver",
              productType: "device",
              variant: "fresh",
              colorway: "silver",
              quantity: 1,
              unitPrice: 99,
              image: "/preorder/device_small.png",
            },
          ],
          status_history: [
            { status: "processing", timestamp: daysAgo(5), description: "Preparing shipment" },
            { status: "shipped", timestamp: daysAgo(3), description: "Picked up by FedEx" },
          ],
        },
      ],
    },
    {
      order_id: "PFY-100295",
      status: "shipped",
      created_at: daysAgo(3),
      items: [
        {
          label: "Puffy 1 Vape — White",
          productType: "device",
          variant: "vape",
          colorway: "white",
          quantity: 1,
          unitPrice: 99,
          image: "/preorder/device_small.png",
        },
        {
          label: "Puffy Vape Pods — Mint Ice",
          productType: "pods",
          variant: "vape",
          flavor: "mint_ice",
          nicotine: "2",
          quantity: 2,
          unitPrice: 15,
          image: "/preorder/pod_small.png",
        },
        {
          label: "Puffy Vape Pods — Watermelon Ice",
          productType: "pods",
          variant: "vape",
          flavor: "watermelon_ice",
          nicotine: "0",
          quantity: 1,
          unitPrice: 15,
          image: "/preorder/pod_small.png",
        },
      ],
      subtotal: 144,
      shipping: 13,
      total: 157,
      currency: "USD",
      shipping_address: {
        name: "Dave M.",
        email: "dave@example.com",
        phone: "+1 555-0199",
        line1: "789 Token Blvd",
        city: "Miami",
        state: "FL",
        postal_code: "33101",
        country: "US",
      },
      payment_method: "USDT (Solana)",
      status_history: [
        { status: "created", timestamp: daysAgo(3), description: "Order placed" },
        { status: "payment_pending", timestamp: daysAgo(3), description: "Awaiting blockchain confirmation" },
        { status: "paid", timestamp: daysAgo(3), description: "Payment confirmed on-chain" },
        { status: "shipped", timestamp: daysAgo(2), description: "Your order has been shipped" },
      ],
      packages: [
        {
          package_id: "PKG-100295-1",
          label: "Package 1 of 2",
          status: "shipped",
          carrier: "UPS",
          tracking_number: "1Z999AA10123456784",
          tracking_url: "https://www.ups.com/track?tracknum=1Z999AA10123456784",
          items: [
            {
              label: "Puffy 1 Vape — White",
              productType: "device",
              variant: "vape",
              colorway: "white",
              quantity: 1,
              unitPrice: 99,
              image: "/preorder/device_small.png",
            },
          ],
          status_history: [
            { status: "processing", timestamp: daysAgo(3), description: "Preparing shipment" },
            { status: "shipped", timestamp: daysAgo(2), description: "Picked up by UPS" },
          ],
        },
        {
          package_id: "PKG-100295-2",
          label: "Package 2 of 2",
          status: "in_transit",
          carrier: "USPS",
          tracking_number: "USPS5556667770",
          tracking_url: "https://tools.usps.com/go/TrackConfirmAction?tLabels=USPS5556667770",
          items: [
            {
              label: "Puffy Vape Pods — Mint Ice",
              productType: "pods",
              variant: "vape",
              flavor: "mint_ice",
              nicotine: "2",
              quantity: 2,
              unitPrice: 15,
              image: "/preorder/pod_small.png",
            },
            {
              label: "Puffy Vape Pods — Watermelon Ice",
              productType: "pods",
              variant: "vape",
              flavor: "watermelon_ice",
              nicotine: "0",
              quantity: 1,
              unitPrice: 15,
              image: "/preorder/pod_small.png",
            },
          ],
          status_history: [
            { status: "processing", timestamp: daysAgo(3), description: "Preparing shipment" },
            { status: "shipped", timestamp: daysAgo(2), description: "Picked up by USPS" },
            { status: "in_transit", timestamp: daysAgo(1), description: "In transit — Miami sorting facility" },
          ],
        },
      ],
    },
    {
      order_id: "PFY-100301",
      status: "payment_pending",
      created_at: daysAgo(0),
      items: [
        {
          label: "Puffy Vape Pods — Mint Ice",
          productType: "pods",
          variant: "vape",
          flavor: "mint_ice",
          nicotine: "0",
          quantity: 3,
          unitPrice: 15,
          image: "/preorder/pod_small.png",
        },
        {
          label: "Puffy Vape Pods — Watermelon Ice",
          productType: "pods",
          variant: "vape",
          flavor: "watermelon_ice",
          nicotine: "2",
          quantity: 1,
          unitPrice: 15,
          image: "/preorder/pod_small.png",
        },
      ],
      subtotal: 60,
      shipping: 5,
      total: 65,
      currency: "USD",
      shipping_address: {
        name: "Carol S.",
        email: "carol@example.com",
        phone: "+44 7700 900123",
        line1: "10 Web3 Street",
        city: "London",
        postal_code: "EC1A 1BB",
        country: "GB",
      },
      payment_method: "USDT (Solana)",
      status_history: [
        { status: "created", timestamp: daysAgo(0), description: "Order placed" },
        { status: "payment_pending", timestamp: daysAgo(0), description: "Awaiting blockchain confirmation" },
      ],
    },
  ];

  localStorage.setItem(ORDERS_STORAGE_KEY, JSON.stringify(mockOrders));
  return mockOrders;
}
