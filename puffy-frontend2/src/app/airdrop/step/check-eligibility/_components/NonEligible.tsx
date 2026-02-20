"use client";

import MainSection from "@/app/airdrop/_components/MainSection";
import WalletSwitch, {
  WalletSwitchProps,
} from "@/app/airdrop/_components/WalletSwitcher";
import NonEligibleIcon from "@/public/airdrop/check-eligibility/non-eligible.svg";
import Image from "next/image";
import { useRouter } from "next/navigation";

export default function NonEligible({ ...props }: WalletSwitchProps) {
  const router = useRouter();

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={
          <Image
            src={NonEligibleIcon}
            alt="non eligible"
            className="rounded-full"
            width={80}
            height={81}
          />
        }
        title={
          <div className="text-center max-w-[450px]">
            No eligible NFT found or you have already claimed all of your Puffy
            Passes.
          </div>
        }
        description={
          <div className="max-w-[450px] text-center">
            Go to the profile to view your
            <span
              className="text-black/90 underline hover:text-black/50 cursor-pointer font-medium"
              onClick={() => {
                router.push("/profile/my-nfts");
              }}
            >
              {" "}
              Puffy Passes →
            </span>
          </div>
        }
        button={<WalletSwitch {...props} />}
      />
    </div>
  );
}
