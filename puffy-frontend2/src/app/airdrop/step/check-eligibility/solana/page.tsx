"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";

export default function SolanaPage() {
  const router = useRouter();
  const { publicKey, disconnect } = useWallet();
  const { setVisible } = useWalletModal();

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={
          <Image
            src={SolIcon}
            alt="SOL"
            className="rounded-full"
            width={100}
            height={100}
          />
        }
        title="Connect Your SOL Wallet"
        description={
          <div className="max-w-[450px] text-center flex flex-col items-center justify-center gap-4">
            We&apos;ll check your NFT holdings to verify whitelist eligibility.
            {publicKey && (
              <div className="mt-4">
                <WalletSwitch
                  wallet={publicKey.toString()}
                  disconnect={disconnect}
                />
              </div>
            )}
          </div>
        }
        button={
          <MainButton
            onClick={
              publicKey
                ? () =>
                    router.push(
                      "/airdrop/step/check-eligibility/solana/communities"
                    )
                : () => setVisible(true)
            }
          >
            {publicKey ? "Check Eligibility" : "Connect Wallet"}
          </MainButton>
        }
      />
    </div>
  );
}
