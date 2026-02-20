"use client";

import NonEligible from "../../_components/NonEligible";
import { useWallet } from "@solana/wallet-adapter-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function SolanaNonEligiblePage() {
  const router = useRouter();
  const { publicKey, disconnect } = useWallet();

  useEffect(() => {
    if (!publicKey) {
      router.push("/airdrop/step/check-eligibility");
    }
  }, [publicKey, router]);

  if (!publicKey) {
    return null; // Don't render anything while redirecting
  }

  return <NonEligible wallet={publicKey.toString()} disconnect={disconnect} />;
}
