"use client";

import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";
import NonEligible from "../../_components/NonEligible";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TonNonEligiblePage() {
  const wallet = useTonAddress();
  const [tonConnectUI] = useTonConnectUI();
  const router = useRouter();

  useEffect(() => {
    if (!wallet) {
      router.push("/airdrop/step/check-eligibility");
    }
  }, [wallet, router]);

  const handleDisconnect = async () => {
    try {
      await tonConnectUI.disconnect();
    } catch (error) {
      console.error("Error disconnecting TON wallet:", error);
    }
  };

  return <NonEligible wallet={wallet || "TON"} disconnect={handleDisconnect} />;
}
