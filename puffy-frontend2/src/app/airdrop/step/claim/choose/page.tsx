"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import { useRouter, useSearchParams } from "next/navigation";
import { fluidSize } from "@/lib/utils";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";
import { useWallet } from "@solana/wallet-adapter-react";
import { useCampaign } from "@/hooks/reward-center/useCampaign";
import { URL_PARAMS } from "@/lib/urlParams";
import { message } from "antd";
import RouteGuard from "@/components/common/RouterGuard";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import {
  CampaignPromotion,
  useGetCampaignPromotionsCampaignsCampaignPGet,
} from "@/types";

export default function ChoosePage() {
  const { publicKey } = useWallet();
  const { campaignInfo } = useCampaign();
  const [api, contextHolder] = message.useMessage();
  const { logout } = useWalletLogin();
  // get campaign promotions info with api
  const { data: campaignPromotions } =
    useGetCampaignPromotionsCampaignsCampaignPGet(
      campaignInfo?.campaign_id?.toString() || "",
      {
        query: {
          enabled: !!campaignInfo?.campaign_id,
        },
      }
    );

  return (
    <RouteGuard guardType={["authenticated", "campaign-required", "eligible"]}>
      {contextHolder}
      <div className="w-full flex flex-col items-center justify-center mb-10">
        <div className="w-full flex flex-col items-center justify-center">
          <div
            className="text-black/90 font-semibold text-center"
            style={{ fontSize: fluidSize(24, 32) }}
          >
            {campaignInfo?.name} Puffy-1 Whitelist
          </div>
          <div
            className="max-w-[450px] text-center text-black/50 md:mt-4 mt-2 text-center"
            style={{ fontSize: fluidSize(14, 16) }}
          >
            Your Puffy Pass WL gives you free access to a $199 community branded
            device at launch.
          </div>
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
        <div className="w-full flex flex-col md:flex-row items-center justify-center gap-8 mt-6">
          {campaignPromotions?.campaign_promotions?.map((promotion) => (
            <NFTCard promotion={promotion} />
          ))}
        </div>
      </div>
    </RouteGuard>
  );
}

function NFTCard({ promotion }: { promotion: CampaignPromotion }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleMint = () => {
    const authCode = searchParams.get(URL_PARAMS.AUTH_CODE);
    let mintPath = `/airdrop/step/claim/mint?${URL_PARAMS.CAMPAIGN_ID}=${promotion.campaign_id}&${URL_PARAMS.PROMOTION_ID}=${promotion.promotion_id}`;

    if (authCode) {
      mintPath += `&${URL_PARAMS.AUTH_CODE}=${authCode}`;
    }

    router.push(mintPath);
  };

  return (
    <div className="aspect-square flex flex-col items-center justify-center text-pingfang p-4 bg-white rounded-2xl w-[280px] lg:w-[320px]">
      <video
        src={promotion.nft_video_url || ""}
        width={400}
        height={400}
        poster={promotion.nft_image_url || ""}
        autoPlay
        loop
        muted
        playsInline
        className="rounded-xl"
      />
      <div
        className="max-w-[450px] text-center md:my-4 my-2 text-center"
        style={{ fontSize: fluidSize(14, 16) }}
      >
        {promotion.promotion?.name || ""}
      </div>
      <MainButton onClick={handleMint} className="w-full min-w-[0px]">
        Mint Device WL
      </MainButton>
    </div>
  );
}
