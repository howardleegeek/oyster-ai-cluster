"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import { useSearchParams } from "next/navigation";
import { URL_PARAMS } from "@/lib/urlParams";
import { message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CheckCircleFilled } from "@ant-design/icons";
import RouteGuard from "@/components/common/RouterGuard";

export default function CopyLinkPage() {
  const searchParams = useSearchParams();
  const [api, contextHolder] = message.useMessage();
  // read campaign id and auth code from url
  const authCode = searchParams.get(URL_PARAMS.AUTH_CODE);
  const campaignId = searchParams.get(URL_PARAMS.CAMPAIGN_ID);
  const promotionId = searchParams.get(URL_PARAMS.PROMOTION_ID);

  const handleCopyLink = () => {
    const link = `${process.env.NEXT_PUBLIC_APP_URL}/airdrop/step/claim/connect-wallet?${URL_PARAMS.CAMPAIGN_ID}=${campaignId}&${URL_PARAMS.AUTH_CODE}=${authCode}&${URL_PARAMS.PROMOTION_ID}=${promotionId}`;
    navigator.clipboard.writeText(link);
    api.success({
      content:
        "Link copied to clipboard, please paste it in your solana wallet browser",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
  };

  return (
    <RouteGuard guardType="campaign-required">
      {contextHolder}
      <div className="w-full flex flex-col items-center justify-center">
        <MainSection
          image={null}
          title="Copy Link to Wallet Browser"
          description={
            <div className="max-w-[800px] text-center flex flex-col items-center justify-center gap-4">
              Click the button to copy the link, then paste it in your Solana
              wallet&apos;s built-in browser.
            </div>
          }
          button={
            <MainButton onClick={handleCopyLink}>Copy the Link</MainButton>
          }
        />
      </div>
    </RouteGuard>
  );
}
