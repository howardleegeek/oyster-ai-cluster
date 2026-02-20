"use client";

import MainSection from "@/app/airdrop/_components/MainSection";
import NonEligibleIcon from "@/public/airdrop/check-eligibility/non-eligible.svg";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { REFERRAL_CODE_KEY } from "@/hooks/reward-center/useCampaign";
import MainButton from "@/app/airdrop/_components/MainButton";
import { useRouter } from "next/navigation";

export default function InvitationNonEligiblePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [referralCode, setReferralCode] = useState<string | null>(null);

  useEffect(() => {
    const refCode = searchParams.get(REFERRAL_CODE_KEY);
    setReferralCode(refCode);
  }, [searchParams]);

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
            Invalid Invitation Code
          </div>
        }
        description={
          <div className="max-w-[450px] text-center flex flex-col gap-4">
            {referralCode && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 font-medium text-sm">
                  Invitation Code:{" "}
                  <span className="font-bold">{referralCode}</span>
                </p>
                <p className="text-red-700 text-xs mt-1">
                  This invitation code is not valid or has expired.
                </p>
              </div>
            )}
            <div>
              Please check your invitation code and try again, or join our{" "}
              <span
                className="text-black/90 underline hover:text-black/50 cursor-pointer mt-2"
                onClick={() => {
                  const telegramUrl = process.env.NEXT_PUBLIC_TELEGRAM_URL;
                  if (telegramUrl) {
                    window.open(telegramUrl, "_blank");
                  }
                }}
              >
                Community→
              </span>{" "}
              to get a valid code.
            </div>
          </div>
        }
        button={
          <MainButton
            onClick={() => {
              router.replace("/airdrop/step/check-eligibility/invitation");
            }}
          >
            Apply New Code
          </MainButton>
        }
      />
    </div>
  );
}
