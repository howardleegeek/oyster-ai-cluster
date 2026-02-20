"use client";

import CommunitiesPageTemplate from "../../_components/CommunitiesPageTemplate";
import { useSearchParams } from "next/navigation";
import { REFERRAL_CODE_KEY } from "@/hooks/reward-center/useCampaign";

export default function InvitationCommunitiesPage() {
  // read referral code from url
  const searchParams = useSearchParams();
  const referralCode = decodeURIComponent(
    searchParams.get(REFERRAL_CODE_KEY) || ""
  );

  return (
    <CommunitiesPageTemplate
      referralCode={referralCode || undefined}
      nonEligibleRoute="/airdrop/step/check-eligibility/invitation/non-eligible"
    />
  );
}
