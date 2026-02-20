"use client";

import { useAccount, useDisconnect } from "wagmi";
import NonEligible from "../../_components/NonEligible";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function EthNonEligiblePage() {
  const { address } = useAccount();
  const { disconnect } = useDisconnect();
  const router = useRouter();

  useEffect(() => {
    if (!address) {
      router.push("/airdrop/step/check-eligibility");
    }
  }, [address, router]);

  const handleDisconnect = async () => {
    try {
      disconnect();
      // Optionally open the connect modal after disconnecting
      // open({ view: "Connect" });
    } catch (error) {
      console.error("Error disconnecting ETH wallet:", error);
    }
  };

  return (
    <NonEligible wallet={address || "ETH"} disconnect={handleDisconnect} />
  );
}
