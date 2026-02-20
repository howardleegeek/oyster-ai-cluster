import type {
  DeviceProductVariant,
  ProductEligibility,
  ProductEligibilityByVariant,
  EligibilityContext,
  DeviceColorwayId,
  ColorwayOption,
} from "@/types/deviceEligibility";
import type { PodsFlavorId, PodsNicotineId } from "@/types/podsCheckout";

export const REFERRAL_POINTS = {
  devicePassReferralReferrer: 100,
  paidDeviceReferralReferrer: 500,
  paidDeviceReferralReferee: 100,
} as const;

export const MIN_CASHOUT_POINTS = Number(
  process.env.NEXT_PUBLIC_MIN_CASHOUT_POINTS ?? 5000
);

export function formatNumber(n: number) {
  return new Intl.NumberFormat("en-US").format(n);
}

// --- Country-based product eligibility ---

/** ISO 3166-1 alpha-2 country codes where Puffy Vape is eligible for sale/shipping. */
export const PUFFY_VAPE_ELIGIBLE_COUNTRIES: ReadonlySet<string> = new Set([
  "US",
  "CA",
  "GB",
  "DE",
  "FR",
  "AU",
  "JP",
  // Add or remove codes as per business rules; consider loading from API later.
]);

/** Options for delivery country selector (code + display name). */
export const DELIVERY_COUNTRY_OPTIONS: ReadonlyArray<{ code: string; name: string }> = [
  { code: "US", name: "United States" },
  { code: "CA", name: "Canada" },
  { code: "GB", name: "United Kingdom" },
  { code: "DE", name: "Germany" },
  { code: "FR", name: "France" },
  { code: "AU", name: "Australia" },
  { code: "JP", name: "Japan" },
  { code: "CN", name: "China" },
  { code: "IN", name: "India" },
  { code: "BR", name: "Brazil" },
  { code: "MX", name: "Mexico" },
  { code: "ES", name: "Spain" },
  { code: "IT", name: "Italy" },
  { code: "NL", name: "Netherlands" },
  { code: "KR", name: "South Korea" },
];

/** Puffy Fresh is always eligible. */
const PUFFY_FRESH_ELIGIBLE = true;

/**
 * Returns eligibility for both Puffy-1 variants for a given country.
 * - Puffy Fresh: always eligible.
 * - Puffy Vape: eligible only in PUFFY_VAPE_ELIGIBLE_COUNTRIES.
 */
export function getProductEligibility(
  ctx: EligibilityContext
): ProductEligibilityByVariant {
  const country = (ctx.countryCode || "").trim().toUpperCase();
  const vapeEligible = country
    ? PUFFY_VAPE_ELIGIBLE_COUNTRIES.has(country)
    : false;

  const fresh: ProductEligibility = {
    eligible: PUFFY_FRESH_ELIGIBLE,
    reason: "Eligible for all countries",
  };

  const vape: ProductEligibility = vapeEligible
    ? {
        eligible: true,
        reason: "Some countries are not eligible",
      }
    : {
        eligible: false,
        reason: country
          ? `Not available for delivery to ${country}`
          : "Select a delivery country to see availability",
        reasonCode: "not_available_in_country",
      };

  return { vape, fresh };
}

/** Returns whether the given variant is eligible for the given country. */
export function isVariantEligible(
  variant: DeviceProductVariant,
  countryCode: string
): boolean {
  const byVariant = getProductEligibility({ countryCode });
  return byVariant[variant].eligible;
}

// --- Colorway options (WL = Puffy Pass WL NFT holder) ---

/** Puffy Vape default colorways (non-WL): Black, White. */
export const PUFFY_VAPE_DEFAULT_COLORWAYS: ColorwayOption[] = [
  { id: "black", label: "Black" },
  { id: "white", label: "White" },
];

/** Puffy Fresh default colorway (non-WL): Silver. */
export const PUFFY_FRESH_DEFAULT_COLORWAYS: ColorwayOption[] = [
  { id: "silver", label: "Silver" },
];

/** Community version colorway (WL holders only). */
export const COMMUNITY_COLORWAY: ColorwayOption = {
  id: "community",
  label: "Community Edition",
};

/**
 * Returns available colorway options for a variant and WL status.
 * - Puffy Vape: WL → community only; non-WL → Black, White.
 * - Puffy Fresh: WL → community only; non-WL → Silver.
 */
export function getColorwaysForVariant(
  variant: DeviceProductVariant,
  isWlHolder: boolean
): ColorwayOption[] {
  if (isWlHolder) {
    return [COMMUNITY_COLORWAY];
  }
  if (variant === "vape") return PUFFY_VAPE_DEFAULT_COLORWAYS;
  return PUFFY_FRESH_DEFAULT_COLORWAYS;
}

/**
 * Default colorway when variant or WL status changes.
 * Vape non-WL: black; Fresh non-WL: silver; WL: community.
 */
export function getDefaultColorway(
  variant: DeviceProductVariant,
  isWlHolder: boolean
): DeviceColorwayId {
  const options = getColorwaysForVariant(variant, isWlHolder);
  return options[0]?.id ?? (variant === "vape" ? "black" : "silver");
}

/** Human-readable label for a colorway id (e.g. for order summary). */
export function getColorwayLabel(colorwayId: DeviceColorwayId): string {
  const map: Record<DeviceColorwayId, string> = {
    black: "Black",
    white: "White",
    silver: "Silver",
    community: "Community Edition",
  };
  return map[colorwayId] ?? colorwayId;
}

// --- Smart Pods ---

export interface PodsFlavorOption {
  id: PodsFlavorId;
  label: string;
}

export interface PodsNicotineOption {
  id: PodsNicotineId;
  label: string;
}

export const PODS_FLAVORS: PodsFlavorOption[] = [
  { id: "peach_oolong", label: "Peach Oolong" },
  { id: "mint_ice", label: "Mint Ice" },
  { id: "watermelon_ice", label: "Watermelon Ice" },
];

export const PODS_NICOTINE_LEVELS: PodsNicotineOption[] = [
  { id: "0", label: "0%" },
  { id: "2", label: "2%" },
];

/** Quantity options (boxes) for Smart Pods: 1, 2, 3, 5, 10, 15. */
export const PODS_QUANTITY_OPTIONS = [1, 2, 3, 5, 10, 15] as const;

