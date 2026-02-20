"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import TonIcon from "@/public/airdrop/check-eligibility/ton.svg";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useTonConnectUI, useTonAddress } from "@tonconnect/ui-react";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";

export default function TonPage() {
  const router = useRouter();
  const [tonConnectUI] = useTonConnectUI();
  const publicAddress = useTonAddress();

  const handleDisconnect = async () => {
    try {
      await tonConnectUI.disconnect();
    } catch (error) {
      console.error("Error disconnecting TON wallet:", error);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={
          <Image
            src={TonIcon}
            alt="TON"
            className="rounded-full"
            width={100}
            height={100}
          />
        }
        title="Connect Your TON Wallet"
        description={
          <div className="max-w-[450px] text-center flex flex-col items-center justify-center gap-4">
            We&apos;ll check your NFT holdings to verify whitelist eligibility.
            Minting will only happen on Solana.
            {publicAddress && (
              <div className="mt-4">
                <WalletSwitch
                  wallet={publicAddress}
                  disconnect={handleDisconnect}
                />
              </div>
            )}
          </div>
        }
        button={
          publicAddress ? (
            <MainButton
              onClick={() =>
                router.push("/airdrop/step/check-eligibility/ton/communities")
              }
            >
              Check Eligibility
            </MainButton>
          ) : (
            <MainButton
              onClick={async () => {
                try {
                  await tonConnectUI.openModal();
                } catch (error) {
                  console.error("Error connecting TON wallet:", error);
                }
              }}
            >
              Connect Wallet
            </MainButton>
          )
        }
      />
    </div>
  );
}
