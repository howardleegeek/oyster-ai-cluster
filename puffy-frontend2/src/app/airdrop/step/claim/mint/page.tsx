"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { fluidSize } from "@/lib/utils";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";
import { useWallet } from "@solana/wallet-adapter-react";
import { useCampaign } from "@/hooks/reward-center/useCampaign";
import { URL_PARAMS } from "@/lib/urlParams";
import { message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CloseCircleFilled } from "@ant-design/icons";
import { useState } from "react";
import RouteGuard from "@/components/common/RouterGuard";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";

export default function MintPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { publicKey } = useWallet();
  const { campaignInfo, mint, promotionId } = useCampaign();
  const [api, contextHolder] = message.useMessage();
  const [isMinting, setIsMinting] = useState(false);
  const promotionInfo = campaignInfo?.campaign_promotions?.find(
    (promotion) => promotion.promotion_id === promotionId
  );
  const { logout } = useWalletLogin();

  const handleMint = async () => {
    setIsMinting(true);
    await mint(
      () => {
        // Minting started
        console.log("Minting started");
      },
      () => {
        // Success - navigate to success page
        setIsMinting(false);
        router.push(
          `/airdrop/step/claim/success?${URL_PARAMS.CAMPAIGN_ID}=${campaignInfo?.campaign_id}&${URL_PARAMS.PROMOTION_ID}=${promotionId}`
        );
      },
      (error) => {
        // Error - show notification
        setIsMinting(false);
        api.error({
          content:
            error.message ||
            "An error occurred while minting your NFT. Please try again.",
          ...NOTIFICATION_CONFIG,
          icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
        });
      }
    );
    setIsMinting(false);
  };

  return (
    <RouteGuard
      guardType={[
        "authenticated",
        "campaign-required",
        "eligible",
        "unminted",
        "promotion-required",
        "email-required",
      ]}
    >
      {contextHolder}
      <div className="w-full flex flex-col items-center justify-center mb-10">
        <MainSection
          image={
            promotionInfo?.nft_video_url && (
              <div>
                <video
                  src={promotionInfo?.nft_video_url}
                  poster={promotionInfo?.nft_image_url || ""}
                  className="w-[200px] md:w-[280px] aspect-square"
                  // width={280}
                  // height={280}
                  autoPlay
                  loop
                  muted
                  playsInline
                  style={{
                    width: fluidSize(300, 600, 320, 1920),
                    height: fluidSize(300, 600, 320, 1920),
                  }}
                />
              </div>
            )
          }
          title={
            <div>
              {campaignInfo?.logo_url && (
                <div className="flex flex-row items-center justify-center gap-2 mb-2">
                  <Image
                    src={campaignInfo?.logo_url}
                    alt="Icon"
                    className="rounded-full"
                    width={30}
                    height={30}
                  />
                  <p
                    className="text-black/90 font-semibold"
                    style={{ fontSize: fluidSize(16, 20) }}
                  >
                    {campaignInfo?.name}
                  </p>
                </div>
              )}
              Puffy-1 Whitelist
            </div>
          }
          description={
            <div className="max-w-[450px] text-center">
              {campaignInfo?.description ||
                "Your Puffy Pass WL gives you free access to a $199 community branded device at launch."}
            </div>
          }
          button={
            <div className="w-full flex flex-col items-center justify-center">
              <MainButton onClick={handleMint} disabled={isMinting}>
                {isMinting ? "Minting..." : "Mint WL NFT"}
              </MainButton>
              <div className="w-full flex flex-row items-center justify-center gap-2 mt-6">
                <p
                  className="text-black/50"
                  style={{ fontSize: fluidSize(12, 16) }}
                >
                  Minting Wallet
                </p>
                <WalletSwitch
                  wallet={publicKey?.toString() || ""}
                  icon={SolIcon}
                  disconnect={() => {
                    logout();
                  }}
                />
              </div>
            </div>
          }
        />
      </div>
    </RouteGuard>
  );
}
