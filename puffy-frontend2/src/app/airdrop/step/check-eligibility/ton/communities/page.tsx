"use client";

import { useTonAddress } from "@tonconnect/ui-react";
import CommunitiesPageTemplate from "../../_components/CommunitiesPageTemplate";

export default function TonCommunitiesPage() {
  const wallet = useTonAddress();

  return (
    <CommunitiesPageTemplate
      chain="ton"
      wallet={{
        address: wallet || null,
        isConnected: !!wallet,
      }}
      nonEligibleRoute="/airdrop/step/check-eligibility/ton/non-eligible"
    />
  );
}
