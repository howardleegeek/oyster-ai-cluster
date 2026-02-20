"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import { Input, ConfigProvider, message } from "antd";
import { useState, useEffect } from "react";
import { useUpdateUserEmailUserEmailPost } from "@/types";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CloseCircleFilled } from "@ant-design/icons";
import Image from "next/image";
import EmailIcon from "@/public/airdrop/claim/email.png";
import { useRouter, useSearchParams } from "next/navigation";
import { useCampaign } from "@/hooks/reward-center/useCampaign";
import { URL_PARAMS } from "@/lib/urlParams";

export default function EmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [api, contextHolder] = message.useMessage();
  const { mutateAsync: updateEmail, isPending } =
    useUpdateUserEmailUserEmailPost();
  const { userInfo, campaignInfo, promotionId, refetchUserInfo } =
    useCampaign();

  // Check if email already exists and redirect to choose page
  useEffect(() => {
    if (userInfo?.email) {
      const campaignId = campaignInfo?.campaign_id;
      let choosePath = "/airdrop/step/claim/choose";

      if (campaignId) {
        choosePath = `/airdrop/step/claim/choose?${URL_PARAMS.CAMPAIGN_ID}=${campaignId}`;
        const authCode = searchParams.get(URL_PARAMS.AUTH_CODE);
        if (authCode) {
          choosePath += `&${URL_PARAMS.AUTH_CODE}=${authCode}`;
        }
        if (promotionId) {
          choosePath += `&${URL_PARAMS.PROMOTION_ID}=${promotionId}`;
        }
      }

      router.replace(choosePath);
    }
  }, [
    userInfo?.email,
    campaignInfo?.campaign_id,
    promotionId,
    searchParams,
    router,
  ]);

  const handleSubmit = async () => {
    if (!email.trim()) {
      return;
    }

    try {
      await updateEmail({
        data: {
          email: email.trim(),
        },
      });

      // Refetch user info to get updated email
      await refetchUserInfo();
    } catch (error: any) {
      api.error({
        content:
          error?.response?.data?.detail ||
          error?.message ||
          "Failed to update email. Please try again.",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      {contextHolder}
      <MainSection
        image={
          <Image
            src={EmailIcon}
            alt="email"
            className=""
            width={60}
            height={60}
          />
        }
        title="Stay in the Loop"
        description={
          <div className="max-w-[450px] text-center">
            Enter your email to receive product updates and important
            announcements
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
                  type="email"
                  placeholder="Email Address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1"
                  style={{
                    background: "white",
                    caretColor: "black",
                  }}
                  onPressEnter={handleSubmit}
                />
                <MainButton
                  onClick={handleSubmit}
                  disabled={!email.trim() || isPending}
                  className="w-[120px] md:w-[160px] max-w-[120px] md:max-w-[160px] min-w-[120px] md:min-w-[160px]"
                >
                  {isPending ? "Submitting..." : "Confirm"}
                </MainButton>
              </div>
            </ConfigProvider>
          </div>
        }
      />
    </div>
  );
}
