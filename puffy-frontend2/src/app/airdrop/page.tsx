"use client";

import Header from "@/components/layout/Header";
import MainButton from "./_components/MainButton";
import { useRouter } from "next/navigation";
import CenterSlick from "./_components/CenterSlick";
import { fluidSize } from "@/lib/utils";
import { useEffect } from "react";

export default function Airdrop() {
  const router = useRouter();

  useEffect(() => {
    // Disable scrolling on mount
    document.body.style.overflow = "hidden";
    document.documentElement.style.overflow = "hidden";

    // Re-enable scrolling on unmount
    return () => {
      document.body.style.overflow = "";
      document.documentElement.style.overflow = "";
    };
  }, []);

  return (
    <div className="w-full flex flex-col items-center justify-center h-screen">
      <header className="w-full z-10">
        <Header />
      </header>

      {/* Main Section */}
      <div className="w-full flex flex-col flex-1 items-center justify-center">
        <p className="md:text-6xl text-4xl font-semibold mb-3 font-pingfang text-center">
          Puffy-1 Whitelist Drop
        </p>
        <p className="md:text-base text-sm text-black/50 max-w-[700px] text-center mb-10 font-pingfang text-center">
            Claim your free whitelist spot, redeemable for a $199 Puffy-1 device at launch. Your Puffy Pass WL unlocks the Original Edition or an exclusive community colorway if you hold an eligible community NFT. Limited supply — check your eligibility and claim today.
        </p>
        <MainButton
          onClick={() => {
            router.push("/airdrop/step/check-eligibility");
          }}
        >
          Check Eligibility
        </MainButton>
      </div>

      {/* Carousel Section */}
      <div
        className="w-full flex-shrink-0 mb-6 md:mb-8"
        style={{
          marginLeft: `calc(-1 * ${fluidSize(16, 24)})`,
          marginRight: `calc(-1 * ${fluidSize(16, 24)})`,
          width: `calc(100% + 2 * ${fluidSize(16, 24)})`,
        }}
      >
        <CenterSlick />
      </div>
    </div>
  );
}
