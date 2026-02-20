"use client";

import { useWallet } from "@solana/wallet-adapter-react";
import CommunitiesPageTemplate from "../../_components/CommunitiesPageTemplate";

export default function SolanaCommunitiesPage() {
  const { publicKey } = useWallet();

  return (
    <CommunitiesPageTemplate
      chain="sol"
      wallet={{
        address: publicKey?.toString() || null,
        isConnected: !!publicKey,
      }}
      nonEligibleRoute="/airdrop/step/check-eligibility/solana/non-eligible"
    />
  );
}
