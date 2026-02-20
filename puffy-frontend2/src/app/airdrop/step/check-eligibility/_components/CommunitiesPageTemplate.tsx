"use client";

import MainSection from "@/app/airdrop/_components/MainSection";
import CampaignTable from "./CampaignTable";
import { useRouter } from "next/navigation";
import { Modal, message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CloseCircleFilled } from "@ant-design/icons";
import { useCheckEligibleFirstEligibleFirstPost } from "@/types";
import { useEffect, useState } from "react";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { URL_PARAMS } from "@/lib/urlParams";
import { Chain } from "@/types/api/fastAPI.schemas";
import useWindow from "@/hooks/common/useWindow";

interface WalletAdapter {
  address: string | null;
  isConnected: boolean;
}

interface CommunitiesPageTemplateProps {
  chain?: "sol" | "ton" | "eth";
  wallet?: WalletAdapter;
  nonEligibleRoute: string;
  title?: string;
  description?: React.ReactNode;
  referralCode?: string;
}

export default function CommunitiesPageTemplate({
  chain,
  wallet,
  nonEligibleRoute,
  title = "Choose your Puffy-1",
  description = (
    <div className="max-w-[650px] text-center">
      Your Puffy Pass WL unlocks a free $199 Puffy-1 device at launch. Select
      the Original Puffy Edition or a community-exclusive colorway to check
      eligibility and claim.
    </div>
  ),
  referralCode,
}: CommunitiesPageTemplateProps) {
  const router = useRouter();
  const [api, contextHolder] = message.useMessage();
  const [campaignIds, setCampaignIds] = useState<number[]>([]);
  const [auth_code, setAuthCode] = useState<string>("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCampaignId, setSelectedCampaignId] = useState<number | null>(
    null
  );
  const { isMobile } = useWindow();

  const { mutate: checkEligibility, isPending } =
    useCheckEligibleFirstEligibleFirstPost({
      mutation: {
        onSuccess: (data) => {
          if (data?.campaigns && data.campaigns.length > 0) {
            setCampaignIds(data.campaigns);
            setAuthCode(data.token ?? "");
          } else {
            router.replace(nonEligibleRoute);
          }
        },
        onError: (error) => {
          console.error("Eligibility check failed:", error);
          api.error({
            content:
              "Unable to verify your eligibility. Please refresh the page.",
            ...NOTIFICATION_CONFIG,
            icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
          });
          router.replace(nonEligibleRoute);
        },
      },
    });

  useEffect(() => {
    // For referral type, we can check eligibility even without wallet connection
    if (referralCode) {
      const requestData: {
        wallet?: string;
        chain?: Chain;
        referral_code?: string;
      } = {
        referral_code: referralCode,
      };

      // Add wallet and chain if available
      if (wallet?.address && wallet.isConnected) {
        requestData.wallet = wallet.address;
      }
      if (chain) {
        requestData.chain = chain as Chain;
      }

      checkEligibility({
        data: requestData,
      });
    } else if (wallet?.address && wallet.isConnected && chain) {
      // For non-referral types, require wallet connection
      const requestData: {
        wallet?: string;
        chain?: Chain;
        referral_code?: string;
      } = {
        wallet: wallet.address,
        chain: chain as Chain,
      };

      checkEligibility({
        data: requestData,
      });
    }
  }, [
    wallet?.address,
    wallet?.isConnected,
    checkEligibility,
    chain,
    referralCode,
  ]);

  const handleCampaignSelect = (campaignId: number) => {
    // Check if the device is mobile
    // If yes, show a modal for user to choose the next page
    if (isMobile) {
      setSelectedCampaignId(campaignId);
      setIsModalOpen(true);
      return;
    }
    // For desktop, go directly to connect-wallet page
    goToNextPage(campaignId, "connect-wallet");
  };

  const handleModalChoice = (nextPage: "connect-wallet" | "copy-link") => {
    if (selectedCampaignId !== null) {
      goToNextPage(selectedCampaignId, nextPage);
      setIsModalOpen(false);
      setSelectedCampaignId(null);
    }
  };

  const goToNextPage = (
    campaignId: number,
    nextPage: "connect-wallet" | "copy-link"
  ) => {
    const params = new URLSearchParams();
    params.set(URL_PARAMS.CAMPAIGN_ID, campaignId.toString());
    if (auth_code) {
      params.set(URL_PARAMS.AUTH_CODE, auth_code);
    }
    if (nextPage === "connect-wallet") {
      router.push(`/airdrop/step/claim/connect-wallet?${params.toString()}`);
    } else if (nextPage === "copy-link") {
      router.push(`/airdrop/step/claim/copy-link?${params.toString()}`);
    }
  };

  if (isPending) {
    return (
      <div className="w-full flex flex-col items-center justify-center">
        <LoadingSpinner />
        <p className="mt-4 text-gray-600">Checking eligibility...</p>
      </div>
    );
  }

  return (
    <>
      {contextHolder}
      <div className="w-full flex flex-col items-center justify-center">
        <MainSection
          title={title}
          description={description}
          image={null}
          button={
            <div className="w-full flex flex-col items-center justify-center">
              <CampaignTable
                campaigns={campaignIds.map((id) => ({
                  id,
                  onClick: () => handleCampaignSelect(id),
                }))}
              />
            </div>
          }
        />
      </div>

      <Modal
        open={isModalOpen}
        footer={null}
        closable={false}
        centered
        width={400}
      >
        <div className="flex flex-col gap-4 p-2">
          <h3 className="text-black/90 text-xl font-medium">
            Are you using Solana wallet&apos;s built-in browser?
          </h3>
          <div className="flex justify-end items-center gap-2">
            <button
              onClick={() => handleModalChoice("copy-link")}
              className="px-2 py-0.5 rounded text-[#ED00ED] text-sm font-medium active:scale-95 transition-all duration-300"
            >
              No
            </button>
            <button
              onClick={() => handleModalChoice("connect-wallet")}
              className="px-2 py-0.5 rounded text-[#ED00ED] text-sm font-medium active:scale-95 transition-all duration-300"
            >
              Yes, Continue
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
