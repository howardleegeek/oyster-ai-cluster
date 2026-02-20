"use client";

import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useGetUserInfoUserInfoGet } from "@/types";
import "@/mocks/init";
import ConnectX from "@/app/airdrop/step/claim/success/_components/ConnectX";
import NoNFTsFound from "./_components/NoNFTsFound";
import NFTCards from "./_components/NFTCards";
import { fluidSize } from "@/lib/utils";
import CoinImage from "@/public/profile/point.png";
import { useMemo } from "react";

export default function MyNFTsPage() {
  const { status } = useWalletLogin();
  const { data: userInfo, refetch: refetchUserInfo } =
    useGetUserInfoUserInfoGet({
      query: {
        enabled: status === "authenticated",
      },
    });
  const nfts = useMemo(() => {
    return userInfo?.nfts?.filter((nft) => nft.status !== "new");
  }, [userInfo]);
  const hasNfts = nfts?.length && nfts.length > 0;

  return (
    <div className="w-full flex flex-col items-start justify-start gap-6 md:gap-10 px-4">
      {userInfo && (
        <div className="flex flex-col max-w-[600px] w-full">
          <div className="w-full p-2 md:p-4 border border-black/10 rounded-xl">
            <ConnectX
              userInfo={userInfo}
              refetchUserInfo={refetchUserInfo}
              showShareButton={false}
              hasLineWrap={false}
              styleOverrides={{
                wrapper: "w-full",
                container: "items-start",
                title: "text-left",
                description: "text-left",
                buttonContainer: "max-w-[200px] md:mt-[24px] mt-[16px]",
                twitterImageContainer: "flex flex-row gap-4",
                divider: "my-[10px] h-0",
              }}
              hasSkipButton={false}
              coinImage={CoinImage}
            />
          </div>
        </div>
      )}
      <div
        className="w-full text-[#17191A] font-semibold font-pingfang"
        style={{ fontSize: fluidSize(20, 24) }}
      >
        My NFTs
      </div>
      {hasNfts ? <NFTCards nfts={nfts || []} /> : <NoNFTsFound />}
    </div>
  );
}
