/**
 * Country-based product eligibility for Puffy-1 device variants.
 *
 * UI BEHAVIOR RULES
 * -----------------
 * 1. Visibility: Both Puffy Vape and Puffy Fresh are always visible in the product selector.
 *
 * 2. Enabled vs disabled:
 *    - Eligible: Card is clickable, can be selected, shows normal eligibility text
 *      (e.g. "Some countries are not eligible" / "Eligible for all countries").
 *    - Ineligible: Card is disabled (not clickable), visually distinct (e.g. muted,
 *      cursor not-allowed), and MUST show a clear reason (see rule 3).
 *
 * 3. Disabled reason (required when product is ineligible):
 *    - Shown on the product card (e.g. under the product name or in the status line).
 *    - Must be user-facing copy explaining why the product is not available
 *      (e.g. "Not available for delivery to [country]" or "Puffy Vape is not eligible in your country").
 *
 * 4. Selection state:
 *    - User can only select an eligible product. If the currently selected product
 *      becomes ineligible (e.g. user changes shipping country), clear selection
 *      or auto-switch to an eligible default (e.g. Puffy Fresh).
 *
 * 5. Checkout: Order submission must only allow eligible products for the
 *    current shipping country; block submit if selection is ineligible.
 */

/** Puffy-1 device product variant. */
export type DeviceProductVariant = "vape" | "fresh";

/** Colorway option id (vape: black/white or community; fresh: silver or community). */
export type DeviceColorwayId = "black" | "white" | "silver" | "community";

/** Display label for colorway selection. */
export interface ColorwayOption {
  id: DeviceColorwayId;
  label: string;
}

/** Human-readable reason shown when a product is disabled. */
export type EligibilityDisabledReason =
  | "not_available_in_country"
  | "country_restriction";

/** Result of eligibility check for a single product. */
export interface ProductEligibility {
  /** Whether this product can be selected and ordered for the given country. */
  eligible: boolean;
  /**
   * When eligible: optional status line (e.g. "Eligible for all countries").
   * When ineligible: MUST be set — short reason shown on the disabled card.
   */
  reason: string;
  /** Optional code for analytics or i18n; set when ineligible. */
  reasonCode?: EligibilityDisabledReason;
}

/** Eligibility for both products keyed by variant. */
export type ProductEligibilityByVariant = Record<
  DeviceProductVariant,
  ProductEligibility
>;

/** Props needed to compute eligibility (e.g. from shipping or early country selector). */
export interface EligibilityContext {
  /** ISO 3166-1 alpha-2 country code (e.g. "US", "GB"). */
  countryCode: string;
}
