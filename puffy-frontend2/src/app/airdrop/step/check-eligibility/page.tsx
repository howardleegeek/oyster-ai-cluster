"use client";

import MainSection from "@/app/airdrop/_components/MainSection";
import CheckButton from "./_components/CheckButton";
import TonIcon from "@/public/airdrop/check-eligibility/ton.svg";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import EthIcon from "@/public/airdrop/check-eligibility/eth.svg";
import BerachainIcon from "@/public/airdrop/check-eligibility/berachain.png";
import InvitationIcon from "@/public/airdrop/check-eligibility/invitation.svg";
import { useRouter } from "next/navigation";

export default function CheckEligibility() {
  return (
    <div className="w-full flex flex-col">
      <MainSection
        image={null}
        title="Check Eligibility"
        description={
          <div className="max-w-[320px] text-center">
            Select the blockchain where you hold your NFT. This is for
            eligibility check only — minting happens on Solana.
          </div>
        }
        button={<CheckEligibilityButtons />}
      />
    </div>
  );
}

function CheckEligibilityButtons() {
  const router = useRouter();
  return (
    <div
      className="flex flex-col gap-3 md:p-10 p-6 bg-white rounded-[16px] md:rounded-[24px]"
      style={{ boxShadow: "0px 4px 20px rgba(0, 0, 0, 0.05)" }}
    >
      <CheckButton
        title="ETH"
        icon={EthIcon}
        onClick={() =>
          router.push("/airdrop/step/check-eligibility/eth?chain=eth")
        }
      />
      <CheckButton
        title="Solana"
        icon={SolIcon}
        onClick={() => router.push("/airdrop/step/check-eligibility/solana")}
      />
      <CheckButton
        title="TON"
        icon={TonIcon}
        onClick={() => router.push("/airdrop/step/check-eligibility/ton")}
      />
      <CheckButton
        title="Berachain"
        icon={BerachainIcon.src}
        onClick={() =>
          router.push("/airdrop/step/check-eligibility/eth?chain=berachain")
        }
      />
      <p className="text-black/50 text-[14px] text-center">or</p>
      <CheckButton
        title="Invitation Code"
        icon={InvitationIcon}
        className="bg-black"
        arrowClassName="text-white/90"
        titleClassName="text-white/90"
        onClick={() =>
          router.push("/airdrop/step/check-eligibility/invitation")
        }
      />
    </div>
  );
}
