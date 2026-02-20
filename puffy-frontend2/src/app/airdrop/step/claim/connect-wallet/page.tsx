"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { URL_PARAMS } from "@/lib/urlParams";
import { useWalletLogin } from "@/hooks";
import RouteGuard from "@/components/common/RouterGuard";
import { useEffect } from "react";
import { useCampaign } from "@/hooks/reward-center/useCampaign";
import { message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CloseCircleFilled } from "@ant-design/icons";
import { useWallet } from "@solana/wallet-adapter-react";
import WalletSwitch from "@/app/airdrop/_components/WalletSwitcher";

export default function ConnectWalletPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [api, contextHolder] = message.useMessage();
  const { publicKey } = useWallet();
  const { logout } = useWalletLogin();
  // read campaign id and auth code from url
  const authCode = searchParams.get(URL_PARAMS.AUTH_CODE);
  const {
    signin,
    eligibleVerificationStatus,
    eligibleVerificationError,
    resetEligibleVerification,
    signinStatus,
    signinError,
    resetSignin,
  } = useWalletLogin();
  const { campaignInfo } = useCampaign();
  const { refetchUserInfo } = useCampaign();

  const handleConnect = async () => {
    try {
      await signin({
        authCode: authCode || undefined,
        campaignId: campaignInfo?.campaign_id
          ? campaignInfo.campaign_id
          : undefined,
      });
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  // Show notification for signin errors
  useEffect(() => {
    if (signinStatus === "error" && signinError) {
      api.error({
        content:
          "Verification failed, please switch to a different wallet or go back to check your eligibility again",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
      resetSignin();
    }
  }, [signinStatus, signinError, api]);

  // Show notification for verification errors
  useEffect(() => {
    if (eligibleVerificationStatus === "error" && eligibleVerificationError) {
      api.error({
        content:
          "Verification failed, please switch to a different wallet or go back to check your eligibility again",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  }, [eligibleVerificationStatus, eligibleVerificationError, api]);

  // Navigate when verification is successful
  useEffect(() => {
    if (eligibleVerificationStatus === "success") {
      resetEligibleVerification();
      refetchUserInfo();
    }
  }, [
    eligibleVerificationStatus,
    router,
    campaignInfo?.campaign_id,
    resetEligibleVerification,
    refetchUserInfo,
  ]);

  return (
    <RouteGuard guardType={["campaign-required", "non-eligible"]}>
      {contextHolder}
      <div className="w-full flex flex-col items-center justify-center">
        <MainSection
          image={
            <Image
              src={SolIcon}
              alt="SOL"
              className="rounded-full"
              width={100}
              height={100}
            />
          }
          title="Connect Your Minting Wallet on Solana"
          description={
            <div className="max-w-[450px] text-center flex flex-col items-center justify-center gap-4">
              The whitelist NFT will be issued directly to your connected Solana
              wallet.
              {publicKey && (
                <div className="mt-4">
                  <WalletSwitch
                    wallet={publicKey.toString()}
                    icon={SolIcon}
                    disconnect={() => logout()}
                  />
                </div>
              )}
            </div>
          }
          button={
            <MainButton
              onClick={handleConnect}
              disabled={
                signinStatus === "pending" ||
                eligibleVerificationStatus === "pending"
              }
            >
              {signinStatus === "pending"
                ? publicKey
                  ? "Signing In..."
                  : "Connecting..."
                : eligibleVerificationStatus === "pending"
                  ? "Verifying..."
                  : publicKey
                    ? "Sign to Verify"
                    : "Connect"}
            </MainButton>
          }
        />
      </div>
    </RouteGuard>
  );
}
