"use client";

import { useWalletLogin } from "@/hooks";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useRef } from "react";
import { URL_PARAMS } from "@/lib/urlParams";
import { useCampaign, CampaignStatus } from "@/hooks/reward-center/useCampaign";

export type GuardType =
  | "authenticated"
  | "guest"
  | "campaign-required"
  | "promotion-required"
  | "email-required"
  | "wallet-connected"
  | "non-eligible"
  | "eligible"
  | "unminted"
  | "minted";

export type CombinedGuardType = GuardType | GuardType[];

// Type for custom redirect paths
export type GuardRedirectPaths = {
  [K in GuardType]?: string;
};

interface RouteGuardProps {
  children: React.ReactNode;
  guardType: CombinedGuardType;
  fallback?: React.ReactNode;
  // Optional custom redirect paths - overrides default behavior
  redirectPaths?: GuardRedirectPaths;
}

/**
 * RouteGuard - Unified guard component with support for combined requirements and custom redirect paths
 *
 * Router Logic:
 * - "authenticated": Requires wallet authentication → unauthenticated goes to connect-wallet (or custom path)
 * - "guest": Guest only → authenticated users redirected to /airdrop/step/claim/mint (or custom path)
 * - "campaign-required": Requires campaign ID → missing campaign ID goes to eligibility check (or custom path)
 * - "promotion-required": Requires promotion ID → missing promotion ID goes to choose page (or custom path)
 * - "email-required": Requires user email → missing email goes to email page (or custom path)
 * - "wallet-connected": Requires connected wallet → disconnected goes to connect-wallet (or custom path)
 * - "eligible": Requires user to be eligible for campaign → non-eligible goes to eligibility check (or custom path)
 * - "non-eligible": Requires user to be non-eligible for campaign → eligible users go to mint page (or custom path)
 * - "unminted": Requires user to not have minted NFT → minted users go to success page (or custom path)
 * - "minted": Requires user to have minted NFT → unminted users go to mint page (or custom path)
 * - Array of types: ALL requirements must be met (AND logic)
 *
 * Custom Redirect Paths:
 * - Use `redirectPaths` prop to override default redirect behavior for specific guard types
 * - Example: redirectPaths={{ authenticated: "/connect", "campaign-required": "/eligibility" }}
 *
 * Usage Examples:
 * // Default behavior
 * <RouteGuard guardType="authenticated">...</RouteGuard>
 *
 * // Claim flow with campaign requirement
 * <RouteGuard guardType={["authenticated", "campaign-required"]}>...</RouteGuard>
 *
 * // Allow guests only (for sign-up pages)
 * <RouteGuard guardType="guest">...</RouteGuard>
 */
export default function RouteGuard({
  children,
  guardType,
  redirectPaths = {},
}: RouteGuardProps) {
  const { status } = useWalletLogin();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [redirectPath, setRedirectPath] = useState<string | null>(null);
  const hasRedirectedRef = useRef(false);

  const authCode = searchParams.get(URL_PARAMS.AUTH_CODE);
  const campaignIdFromParams = searchParams.get(URL_PARAMS.CAMPAIGN_ID);
  const promotionIdFromParams = searchParams.get(URL_PARAMS.PROMOTION_ID);

  const {
    status: campaignStatus,
    promotionId,
    campaignInfo,
    userInfo,
  } = useCampaign();
  const campaignId = campaignInfo?.campaign_id;

  // Use params from URL as fallback to ensure we don't lose them during redirects
  const effectiveCampaignId =
    campaignId ||
    (campaignIdFromParams ? parseInt(campaignIdFromParams, 10) : undefined);
  const effectivePromotionId =
    promotionId ||
    (promotionIdFromParams ? parseInt(promotionIdFromParams, 10) : undefined);
  const effectiveAuthCode = authCode;

  // Compute status flags once (used in both effects and render logic)
  const isAuthenticated = status === "authenticated";
  const isConnected = status === "connected" || status === "authenticated";
  const hasCampaignId = !!effectiveCampaignId;
  const hasPromotionId = !!effectivePromotionId;
  const hasEmail = !!userInfo?.email;

  // Campaign-related status
  const isEligible = campaignStatus > CampaignStatus.UNELIGIBLE;
  const isMinted = campaignStatus === CampaignStatus.CLAIMED;

  // Separate effect for determining redirect path
  useEffect(() => {
    // Reset redirect flag when guard type changes
    hasRedirectedRef.current = false;

    // Don't redirect while still loading
    if (status === "unchecked" || status === "loading") {
      return;
    }

    // Don't redirect while campaign status is still being determined
    if (
      campaignStatus === CampaignStatus.UNCHECKED ||
      campaignStatus === CampaignStatus.LOADING
    ) {
      return;
    }

    // Normalize guardType to array for consistent processing
    const guards = Array.isArray(guardType) ? guardType : [guardType];

    // Determine redirect path based on guard requirements
    let targetPath: string | null = null;

    const getRedirectPath = (guard: GuardType, defaultPath: string): string => {
      const customPath = redirectPaths[guard];
      return customPath || defaultPath;
    };

    // Check each guard requirement
    for (const guard of guards) {
      switch (guard) {
        case "guest":
          if (isAuthenticated) {
            targetPath = getRedirectPath("guest", "/airdrop/step/claim/mint");
            break;
          }
          break;

        case "authenticated":
          if (!isAuthenticated) {
            let connectPath = "/airdrop/step/claim/connect-wallet";
            if (hasCampaignId) {
              connectPath = `/airdrop/step/claim/connect-wallet?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                connectPath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
              if (effectivePromotionId) {
                connectPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("authenticated", connectPath);
            break;
          }
          break;

        case "wallet-connected":
          if (!isConnected) {
            let connectPath = "/airdrop/step/claim/connect-wallet";
            if (hasCampaignId) {
              connectPath = `/airdrop/step/claim/connect-wallet?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                connectPath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
              if (effectivePromotionId) {
                connectPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("wallet-connected", connectPath);
            break;
          }
          break;

        case "campaign-required":
          if (!hasCampaignId) {
            targetPath = getRedirectPath(
              "campaign-required",
              "/airdrop/step/check-eligibility"
            );
            break;
          }
          break;

        case "promotion-required":
          if (!hasPromotionId) {
            let choosePath = "/airdrop/step/claim/choose";
            if (hasCampaignId) {
              choosePath = `/airdrop/step/claim/choose?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                choosePath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
            }
            targetPath = getRedirectPath("promotion-required", choosePath);
            break;
          }
          break;

        case "email-required":
          if (!hasEmail) {
            let emailPath = "/airdrop/step/claim/email";
            if (hasCampaignId) {
              emailPath = `/airdrop/step/claim/email?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                emailPath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
              if (effectivePromotionId) {
                emailPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("email-required", emailPath);
            break;
          }
          break;

        case "eligible":
          if (!isEligible) {
            targetPath = getRedirectPath(
              "eligible",
              "/airdrop/step/check-eligibility"
            );
            break;
          }
          break;

        case "non-eligible":
          if (isEligible) {
            let emailPath = "/airdrop/step/claim/email";
            if (hasCampaignId) {
              emailPath = `/airdrop/step/claim/email?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                emailPath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
              if (effectivePromotionId) {
                emailPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("non-eligible", emailPath);
            break;
          }
          break;

        case "unminted":
          if (isMinted) {
            let successPath = "/airdrop/step/claim/success";
            if (hasCampaignId) {
              successPath = `/airdrop/step/claim/success?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectivePromotionId) {
                successPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("unminted", successPath);
            break;
          }
          break;

        case "minted":
          if (!isMinted) {
            let mintPath = "/airdrop/step/claim/mint";
            if (hasCampaignId) {
              mintPath = `/airdrop/step/claim/mint?${URL_PARAMS.CAMPAIGN_ID}=${effectiveCampaignId}`;
              if (effectiveAuthCode) {
                mintPath += `&${URL_PARAMS.AUTH_CODE}=${effectiveAuthCode}`;
              }
              if (effectivePromotionId) {
                mintPath += `&${URL_PARAMS.PROMOTION_ID}=${effectivePromotionId}`;
              }
            }
            targetPath = getRedirectPath("minted", mintPath);
            break;
          }
          break;
      }

      // If we found a redirect path, break out early
      if (targetPath) {
        break;
      }
    }

    // Only set redirect path if it's different from current and not empty
    if (targetPath && targetPath !== redirectPath) {
      setRedirectPath(targetPath);
    } else if (!targetPath && redirectPath) {
      // Clear redirect path if no target path is needed
      setRedirectPath(null);
      hasRedirectedRef.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    status,
    effectiveCampaignId,
    effectiveAuthCode,
    campaignStatus,
    effectivePromotionId,
    userInfo?.email,
    guardType,
    searchParams,
  ]);

  // Separate effect for actual redirect
  useEffect(() => {
    if (redirectPath && !hasRedirectedRef.current) {
      hasRedirectedRef.current = true;
      const timeoutId = setTimeout(() => {
        router.replace(redirectPath);
      }, 100);
      return () => clearTimeout(timeoutId);
    }
  }, [redirectPath, router, guardType]);

  // Normalize guardType to array for consistent processing
  const guards = Array.isArray(guardType) ? guardType : [guardType];

  // Check if ALL guard requirements are met
  const meetsAllRequirements = guards.every((guard) => {
    switch (guard) {
      case "guest":
        return !isAuthenticated;
      case "authenticated":
        return isAuthenticated;
      case "wallet-connected":
        return isConnected;
      case "campaign-required":
        return hasCampaignId;
      case "promotion-required":
        return hasPromotionId;
      case "email-required":
        return hasEmail;
      case "eligible":
        return isEligible;
      case "non-eligible":
        return !isEligible;
      case "unminted":
        return !isMinted;
      case "minted":
        return isMinted;
      default:
        return true;
    }
  });

  return meetsAllRequirements ? <>{children}</> : null;
}
