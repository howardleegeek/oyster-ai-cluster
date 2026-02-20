"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import InvitationLargeIcon from "@/public/airdrop/check-eligibility/invitation-large.svg";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { Input, ConfigProvider } from "antd";
import { useState, useEffect } from "react";
import { REFERRAL_CODE_KEY } from "@/hooks/reward-center/useCampaign";
import { useGetCampaignsCampaignsGet } from "@/types/api/reward-center-api/reward-center-api";

export default function InvitationPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [invitationCode, setInvitationCode] = useState("");
  const { data: campaigns } = useGetCampaignsCampaignsGet({
    query: {
      enabled: true,
    },
  });
  const campaignInfo = campaigns?.find((campaign) => campaign.name === "Puffy");
  const postUrl = campaignInfo?.x_post_url || "https://x.com/puffy_ai";
  // Read referral code from URL params on component mount
  useEffect(() => {
    const refCode = searchParams.get(REFERRAL_CODE_KEY);
    if (refCode) {
      setInvitationCode(refCode);
    }
  }, [searchParams]);

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={
          <Image
            src={InvitationLargeIcon}
            alt="invitation"
            className=""
            width={60}
            height={60}
          />
        }
        title="Enter Your Puffy Invitation Code"
        description={
          <div className="max-w-[450px] text-center">
            Have an invite code? Enter it below to unlock your whitelist access.
            Need a code? Simply reply &quot;Code&quot; to{" "}
            <span
              className="text-black/90 underline hover:text-black/50 cursor-pointer font-medium"
              onClick={() => {
                window.open(postUrl, "_blank");
              }}
            >
              this post
            </span>{" "}
            and get your free Puffy-1 WL invite!
          </div>
        }
        button={
          <div className="w-full md:w-[650px]">
            <ConfigProvider
              theme={{
                components: {
                  Input: {
                    colorPrimary: "black",
                    colorPrimaryHover: "transparent",
                    activeBorderColor: "transparent",
                    hoverBorderColor: "transparent",
                    colorBorder: "transparent",
                    activeShadow: "0 0 0 0px transparent",
                    boxShadow: "none",
                    paddingInline: 20,
                    paddingBlock: 10,
                    borderRadius: 60,
                    fontSize: 16,
                    fontFamily: "PingFang SC",
                    colorText: "rgba(0, 0, 0, 0.90)",
                    colorTextPlaceholder: "rgba(0, 0, 0, 0.30)",
                  },
                },
              }}
            >
              <div className="w-full flex flex-row md:gap-4 gap-2">
                <Input
                  placeholder="Invitation Code"
                  value={invitationCode}
                  onChange={(e) => setInvitationCode(e.target.value)}
                  className="flex-1"
                  style={{
                    background: "white",
                    caretColor: "black",
                  }}
                />
                <MainButton
                  onClick={() => {
                    // Redirect to invitation-specific communities page with referral code
                    const nextUrl = invitationCode
                      ? `/airdrop/step/check-eligibility/invitation/communities?${REFERRAL_CODE_KEY}=${encodeURIComponent(invitationCode)}`
                      : "/airdrop/step/check-eligibility/invitation/communities";
                    router.push(nextUrl);
                  }}
                  disabled={!invitationCode.trim()}
                  className="w-[120px] md:w-[160px] max-w-[120px] md:max-w-[160px] min-w-[120px] md:min-w-[160px]"
                >
                  Confirm
                </MainButton>
              </div>
            </ConfigProvider>
          </div>
        }
      />
    </div>
  );
}
