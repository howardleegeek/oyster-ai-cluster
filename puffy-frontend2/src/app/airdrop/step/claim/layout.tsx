"use client";

import { URL_PARAMS } from "@/lib/urlParams";
import { useSearchParams } from "next/navigation";
import { useGetCampaignCampaignsCampaignGet } from "@/types";
import { CampaignProvider } from "@/hooks/reward-center/useCampaign";
import { useMemo } from "react";

export default function ClaimLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const searchParams = useSearchParams();
  const campaignId = searchParams.get(URL_PARAMS.CAMPAIGN_ID);
  const promotionIdParam = searchParams.get(URL_PARAMS.PROMOTION_ID);

  const { data: campaignInfo } = useGetCampaignCampaignsCampaignGet(
    campaignId || "",
    {
      query: {
        enabled: !!campaignId,
      },
    }
  );

  const promotionId = useMemo(() => {
    if (promotionIdParam) {
      return parseInt(promotionIdParam, 10);
    }
    return campaignInfo?.campaign_promotions?.[0]?.promotion_id;
  }, [promotionIdParam, campaignInfo?.campaign_promotions]);

  return (
    <CampaignProvider
      key={`${campaignId}-${promotionId}`}
      campaignName={campaignId || ""}
      promotionId={promotionId}
    >
      {children}
    </CampaignProvider>
  );
}
