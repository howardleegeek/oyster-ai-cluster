import { axiosInstance } from "@/lib/custom-instance";

export type PurchaseRole = "regular" | "wl_holder" | "device_pass_user";

export interface DevicePassSummary {
  available: number;
}

export interface ValidateDevicePassResponse {
  valid: boolean;
  message?: string;
}

export interface DeviceQuoteRequest {
  device_pass_code?: string;
  pay_device_with: "usdt" | "points" | "waived";
  pay_shipping_with: "usdt" | "points";
  referral_code?: string;
  /** Optional: variant/colorway for future backend support. */
  variant?: "vape" | "fresh";
  colorway?: string;
}

export interface DeviceQuoteResponse {
  device_price_usdt: number;
  device_price_points: number;
  shipping_usdt: number;
  shipping_points: number;
  total_usdt: number;
  total_points: number;
  currency: "USDT";
}

export interface ShippingAddress {
  name: string;
  email: string;
  phone?: string;
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
}

/** Single line item for order (variant + colorway + quantity). */
export interface DeviceOrderLineItem {
  variant: "vape" | "fresh";
  colorway: string;
  quantity: number;
}

export interface CreateDeviceOrderRequest extends DeviceQuoteRequest {
  shipping_address: ShippingAddress;
  /** Variant and colorway from first item (backward compat). */
  variant?: "vape" | "fresh";
  colorway?: string;
  /** Full cart line items for multi-item orders (backend may use when supported). */
  line_items?: DeviceOrderLineItem[];
}

export interface CreateDeviceOrderResponse {
  order_id: string;
  status: "created" | "payment_pending" | "paid" | "failed";
  payment_url?: string;
}

// NOTE: These endpoints are assumed to exist on backend per product spec.
export async function getDevicePassSummary() {
  return axiosInstance.get<DevicePassSummary>("/device-pass/summary").then((r) => r.data);
}

export async function createDevicePass() {
  return axiosInstance.post<{ code: string }>("/device-pass").then((r) => r.data);
}

export async function validateDevicePass(code: string) {
  return axiosInstance
    .post<ValidateDevicePassResponse>("/device-pass/validate", { code })
    .then((r) => r.data);
}

export async function getDeviceQuote(req: DeviceQuoteRequest) {
  return axiosInstance.post<DeviceQuoteResponse>("/device/quote", req).then((r) => r.data);
}

/** POST /device/orders — backend must implement this route. 404 = route missing or wrong base URL. */
export async function createDeviceOrder(req: CreateDeviceOrderRequest) {
  return axiosInstance.post<CreateDeviceOrderResponse>("/device/orders", req).then((r) => r.data);
}

// --- Smart Pods orders (backend may implement /pods/orders) ---

export interface PodsOrderLineItem {
  flavor: string;
  nicotine: string;
  quantity: number;
}

export interface CreatePodsOrderRequest {
  line_items: PodsOrderLineItem[];
  shipping_address: ShippingAddress;
  referral_code?: string;
}

export interface CreatePodsOrderResponse {
  order_id: string;
  status: "created" | "payment_pending" | "paid" | "failed";
  payment_url?: string;
}

/** POST /pods/orders — backend must implement this route. 404 = route missing or wrong base URL. */
export async function createPodsOrder(req: CreatePodsOrderRequest) {
  return axiosInstance
    .post<CreatePodsOrderResponse>("/pods/orders", req)
    .then((r) => r.data);
}

