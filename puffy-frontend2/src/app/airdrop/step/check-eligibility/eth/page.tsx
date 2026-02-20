"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import EthIcon from "@/public/airdrop/check-eligibility/eth.svg";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { useAccount, useDisconnect } from "wagmi";
import { useAppKit } from "@reown/appkit/react";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";
import BerachainIcon from "@/public/airdrop/check-eligibility/berachain.png";

export default function EthPage() {
  const router = useRouter();
  const { address, isConnected } = useAccount();
  const { disconnect } = useDisconnect();
  const { open } = useAppKit();
  // read chain from url
  const chain = useSearchParams().get("chain");

  const handleConnect = () => {
    open({ view: "Connect" });
  };

  const handleDisconnect = () => {
    disconnect();
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={
          <Image
            src={chain === "berachain" ? BerachainIcon : EthIcon}
            alt={chain === "berachain" ? "Berachain" : "ETH"}
            className="rounded-full"
            width={100}
            height={100}
          />
        }
        title={chain === "berachain" ? "Connect Your Berachain Wallet" : "Connect Your ETH Wallet"}
        description={
          <div className="max-w-[450px] text-center flex flex-col items-center justify-center gap-4">
            We&apos;ll check your NFT holdings to verify whitelist eligibility.
            Minting will only happen on Solana.
            {isConnected && address && (
              <div className="mt-4">
                <WalletSwitch wallet={address} disconnect={handleDisconnect} />
              </div>
            )}
          </div>
        }
        button={
          isConnected ? (
            <MainButton
              onClick={() =>
                router.push("/airdrop/step/check-eligibility/eth/communities")
              }
            >
              Check Eligibility
            </MainButton>
          ) : (
            <MainButton onClick={handleConnect}>Connect Wallet</MainButton>
          )
        }
      />
    </div>
  );
}
