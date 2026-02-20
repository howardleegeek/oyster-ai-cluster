"use client";

import { fluidSize } from "@/lib/utils";
import { ArrowRightOutlined } from "@ant-design/icons";
import Image from "next/image";
import { useGetCampaignCampaignsCampaignGet } from "@/types/api/reward-center-api/reward-center-api";

export interface CampaignCardProps {
  campaignId: string;
  onClick?: () => void;
  className?: string;
}

export default function CampaignCard({
  campaignId,
  onClick,
  className = "",
}: CampaignCardProps) {
  const {
    data: campaignInfo,
    isLoading,
    error,
  } = useGetCampaignCampaignsCampaignGet(campaignId, {
    query: {
      enabled: !!campaignId,
    },
  });

  if (isLoading) {
    return (
      <div
        className={`w-full p-3 bg-white rounded-full flex items-center justify-between max-w-[480px] animate-pulse ${className}`}
      >
        <div className="flex items-center gap-4">
          <div className="md:w-20 md:h-20 w-10 h-10 rounded-full bg-gray-200 flex-shrink-0"></div>
          <div className="flex flex-col md:gap-2 gap-1">
            <div className="h-4 bg-gray-200 rounded w-32"></div>
            <div className="h-3 bg-gray-200 rounded w-48"></div>
          </div>
        </div>
        <div className="w-5 h-5 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (error || !campaignInfo) {
    return (
      <div
        className={`w-full p-3 bg-white rounded-full flex items-center justify-between max-w-[480px] ${className}`}
      >
        <div className="flex items-center gap-4">
          <div className="md:w-20 md:h-20 w-10 h-10 rounded-full bg-gray-100 flex-shrink-0"></div>
          <div className="flex flex-col md:gap-2 gap-1">
            <h3
              className="text-[#17191A] font-medium"
              style={{ fontSize: fluidSize(12, 16) }}
            >
              Campaign unavailable
            </h3>
            <p
              className="text-[#191919]/50 font-normal"
              style={{ fontSize: fluidSize(10, 14) }}
            >
              Unable to load campaign information
            </p>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div
      className={`w-full p-3 bg-white rounded-full flex items-center justify-between cursor-pointer active:scale-[0.98] transition-all duration-300 max-w-[470px]  ${className}`}
      onClick={onClick}
    >
      <div className="flex items-center gap-4">
        <div className="md:w-20 md:h-20 w-10 h-10 rounded-full flex-shrink-0 relative">
          <Image
            src={campaignInfo.logo_url || "/default-campaign.png"}
            alt={campaignInfo.name || "Campaign"}
            width={80}
            height={80}
            className="w-full h-full object-cover rounded-full"
          />
        </div>
        <div className="flex flex-col md:gap-2 gap-1">
          <h3
            className="text-[#17191A] font-medium"
            style={{ fontSize: fluidSize(12, 16) }}
          >
            {campaignInfo.name !== "Puffy"
              ? campaignInfo.name
              : "Puffy (Original Edition)"}
          </h3>
          <p
            className="text-[#191919]/50 font-normal"
            style={{ fontSize: fluidSize(10, 14) }}
          >
            {campaignInfo.name !== "Puffy"
              ? ` Available for ${campaignInfo.name} NFT holders`
              : ` Available for all`}
          </p>
        </div>
      </div>
      <ArrowRightOutlined className="w-5 h-5 opacity-50" />
    </div>
  );
}
