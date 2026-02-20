"use client";

import { useRef, useState, useEffect } from "react";
import { toPng } from "html-to-image";
import { message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CheckCircleFilled } from "@ant-design/icons";
import ConnectX from "./_components/ConnectX";
import { useCampaign } from "@/hooks/reward-center/useCampaign";
import SuccessMessage from "./_components/SuccessMessage";
import NFTDisplay from "./_components/NFTDisplay";
import useWindow from "@/hooks/common/useWindow";
import Confetti from "react-confetti";
import RouteGuard from "@/components/common/RouterGuard";
import { fluidSize } from "@/lib/utils";
import { URL_PARAMS } from "@/lib/urlParams";
import { useSearchParams } from "next/navigation";

export default function SuccessPage() {
  const copyRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const [isCoping, setIsCoping] = useState(false);
  const [api, contextHolder] = message.useMessage();
  const [isFirefox, setIsFirefox] = useState(false);
  const { userInfo, refetchUserInfo, campaignInfo, promotionId } =
    useCampaign();

  // Get real campaign and NFT data
  const nft = userInfo?.nfts?.find(
    (nft) =>
      nft.campaign_id === campaignInfo?.campaign_id &&
      nft.promotion_id === promotionId
  );
  const promoteInfo = campaignInfo?.campaign_promotions?.find(
    (promotion) => promotion.promotion_id === promotionId
  );
  const nftId = nft?.seq ? `#${nft.seq}` : "#0000";
  const description = campaignInfo?.edition || "Puffy Edition";
  const posterUrl = promoteInfo?.nft_text_front_image_url || "";
  const videoUrl = promoteInfo?.nft_text_front_video_url || "";
  const shareUrl = nft?.x_post_url || campaignInfo?.x_post_url || "";
  const { width, height } = useWindow();
  const [showConfetti, setShowConfetti] = useState(true);
  const [confettiOpacity, setConfettiOpacity] = useState(1);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsFirefox(navigator.userAgent.toLowerCase().includes("firefox"));
    }
  }, []);

  useEffect(() => {
    const fadeTimer = setTimeout(() => {
      setConfettiOpacity(0);
    }, 7000);

    const hideTimer = setTimeout(() => {
      setShowConfetti(false);
    }, 8000);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(hideTimer);
    };
  }, []);

  // Copy component as image to clipboard
  const copyComponentAsImage = async () => {
    // check if the device is mobile
    if (
      typeof window !== "undefined" &&
      navigator.userAgent.includes("Mobile")
    ) {
      setIsCoping(false);
      return;
    }

    if (!copyRef.current) return;
    setIsCoping(true);
    // Convert component to PNG image with higher quality settings
    const dataUrl = await toPng(copyRef.current, {
      quality: 1.0,
      pixelRatio: 4, // Increased from 2 to 4 for better clarity
      backgroundColor: "#ffffff",
      skipAutoScale: true, // Prevent automatic scaling
      style: {
        transform: "scale(1)",
        transformOrigin: "top left",
      },
      filter: (node) => {
        // Ensure all images and videos are properly rendered
        return node.tagName !== "SCRIPT";
      },
      skipFonts: isFirefox,
    });

    // Convert dataUrl to proper PNG blob
    const base64Data = dataUrl.split(",")[1];
    const binaryData = atob(base64Data);
    const bytes = new Uint8Array(binaryData.length);
    for (let i = 0; i < binaryData.length; i++) {
      bytes[i] = binaryData.charCodeAt(i);
    }
    const pngBlob = new Blob([bytes], { type: "image/png" });

    // Check if browser supports clipboard API
    if (
      typeof window === "undefined" ||
      !navigator.clipboard ||
      !navigator.clipboard.write
    ) {
      setIsCoping(false);
      return;
    }

    // Create ClipboardItem and write to clipboard
    const clipboardItem = new ClipboardItem({
      "image/png": pngBlob,
    });

    await navigator.clipboard.write([clipboardItem]);
    api.success({
      content: "Copied the image to clipboard successfully!",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
    // wait for 2 seconds
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsCoping(false);
  };

  const handleShare = async () => {
    try {
      await copyComponentAsImage();
    } catch (error) {
      setIsCoping(false);
      console.error(error);
    }

    window.open(
      `https://x.com/intent/tweet?text=${encodeURIComponent(`${campaignInfo?.name || "Puffy Pass"} Whitelist`)}&url=${encodeURIComponent(shareUrl || "")}`,
      "_blank"
    );
  };

  return (
    <RouteGuard
      guardType={[
        "authenticated",
        "campaign-required",
        "minted",
        "promotion-required",
        "email-required",
      ]}
    >
      {showConfetti && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            zIndex: 9999,
            opacity: confettiOpacity,
            transition: "opacity 1s ease-out",
            pointerEvents: "none",
          }}
        >
          <Confetti
            width={width}
            height={height}
            recycle={false}
            numberOfPieces={500}
          />
        </div>
      )}
      {contextHolder}

      {/* Desktop Layout */}
      <div className="hidden md:flex w-full flex-col flex-1 items-center justify-center gap-6 md:gap-10">
        {nftId && (
          <SuccessMessage
            onViewNft={() => {
              window.open(`https://magiceden.us/marketplace/puffy`, "_blank");
            }}
          />
        )}

        {/* Main Content */}
        <div className="w-full max-w-[900px] bg-white rounded-[44px] p-6">
          {/* NFT Info */}
          <div className="w-full flex flex-row items-center justify-center gap-[24px]">
            <NFTDisplay
              ref={copyRef}
              nftId={nftId}
              description={description}
              posterUrl={posterUrl}
              videoUrl={videoUrl}
              isCoping={isCoping}
            />

            {/* Desktop ConnectX Component */}
            <div className="w-full h-full max-w-[350px]">
              <ConnectX
                onlyShared={true}
                userInfo={userInfo!}
                refetchUserInfo={refetchUserInfo}
                shareFunction={handleShare}
                openNftDialog={false}
                isLoading={isCoping}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Layout */}
      <div className="md:hidden w-full h-full flex flex-col">
        {/* Scrollable content area - fills remaining space */}
        <div className="flex-1 overflow-y-auto flex flex-col items-center justify-start gap-6 pb-6">
          {nftId && (
            <SuccessMessage
              onViewNft={() => {
                window.open(`https://magiceden.us/marketplace/puffy`, "_blank");
              }}
            />
          )}

          {/* Main Content */}
          <div className="w-[220px] bg-white rounded-[24px] p-2">
            <NFTDisplay
              ref={copyRef}
              nftId={nftId}
              description={description}
              posterUrl={posterUrl}
              videoUrl={videoUrl}
              isCoping={isCoping}
            />
          </div>
        </div>

        {/* Fixed bottom component */}
        <div
          className="flex-shrink-0 rounded-t-[40px] bg-white p-5"
          style={{
            marginLeft: `calc(-1 * ${fluidSize(16, 24)})`,
            marginRight: `calc(-1 * ${fluidSize(16, 24)})`,
            marginBottom: `calc(-1 * ${fluidSize(16, 24)})`,
            width: `calc(100% + 2 * ${fluidSize(16, 24)})`,
          }}
        >
          <ConnectX
            onlyShared={true}
            userInfo={userInfo!}
            refetchUserInfo={refetchUserInfo}
            shareFunction={handleShare}
            openNftDialog={true}
            isLoading={isCoping}
          />
        </div>
      </div>
    </RouteGuard>
  );
}
