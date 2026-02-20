"use client";

import { useAccount } from "wagmi";
import CommunitiesPageTemplate from "../../_components/CommunitiesPageTemplate";

export default function EthCommunitiesPage() {
  const { address, isConnected } = useAccount();

  return (
    <CommunitiesPageTemplate
      chain="eth"
      wallet={{
        address: address || null,
        isConnected,
      }}
      nonEligibleRoute="/airdrop/step/check-eligibility/eth/non-eligible"
    />
  );
}