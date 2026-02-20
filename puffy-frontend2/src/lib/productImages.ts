/**
 * Centralised product image paths.
 *
 * Each variant exposes an ordered array of gallery images.
 * The first image is treated as the hero / default.
 * Images live in /public/products/{variant}/.
 */

import type { DeviceProductVariant } from "@/types/deviceEligibility";
import type { PodsProductVariant } from "@/types/podsCheckout";

const DEVICE_GALLERY: Record<DeviceProductVariant, string[]> = {
  vape: [
    "/products/vape/device-1.png",
    "/products/vape/device-2.png",
    "/products/vape/device-3.png",
  ],
  fresh: [
    "/products/fresh/device-1.png",
    "/products/fresh/device-2.png",
    "/products/fresh/device-3.png",
    "/products/fresh/device-4.png",
  ],
};

const PODS_GALLERY: Record<PodsProductVariant, string[]> = {
  vape: [
    "/products/vape/pods-1.png",
    "/products/vape/pods-2.png",
    "/products/vape/pods-3.png",
  ],
  fresh: [
    "/products/fresh/pods-1.png",
    "/products/fresh/pods-2.png",
    "/products/fresh/pods-3.png",
  ],
};

/** Returns the gallery image array for a device variant. */
export function getDeviceImages(variant: DeviceProductVariant): string[] {
  return DEVICE_GALLERY[variant];
}

/** Returns the first (hero) image for a device variant. */
export function getDeviceImage(variant: DeviceProductVariant): string {
  return DEVICE_GALLERY[variant][0];
}

/** Returns the gallery image array for a pods variant. */
export function getPodsImages(variant: PodsProductVariant): string[] {
  return PODS_GALLERY[variant];
}

/** Returns the first (hero) image for a pods variant. */
export function getPodsImage(variant: PodsProductVariant): string {
  return PODS_GALLERY[variant][0];
}
