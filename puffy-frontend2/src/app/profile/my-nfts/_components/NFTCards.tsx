"use client";

import { fluidSize } from "@/lib/utils";
import Image from "next/image";
import ShareIcon from "@/public/profile/share.svg";
import { PromoteNft } from "@/types";

interface NFTCardsProps {
  nfts: PromoteNft[];
}

export default function NFTCards({ nfts }: NFTCardsProps) {
  return (
    <div className="w-full grid grid-cols-2 md:grid-cols-3 gap-2 md:gap-3">
      {nfts.map((nft, index) => (
        <NFTCard key={index} {...nft} />
      ))}
    </div>
  );
}

function NFTCard({ ...nft }: PromoteNft) {
  const nftName = nft.name;
  const imageUrl = nft.on_chain_image_url;

  const handleShare = async () => {
    const shareText = nft.name || `Puffy Pass Whitelist NFT`;

    window.open(
      `https://x.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(nft.x_post_url || "")}`,
      "_blank"
    );
  };

  const handleCheckDetails = () => {
    window.open(`https://magiceden.us/marketplace/puffy`, "_blank");
  };

  return (
    <div className="w-full flex flex-col">
      <div className="relative">
        <Image
          src={imageUrl || ""}
          alt={nftName || "Unknown"}
          width={192}
          height={192}
          className="w-full rounded-t-xl border border-black/10 p-2"
        />
        <div
          className="absolute bottom-2 right-2 bg-black/20 p-1.5 rounded-sm active:scale-95 transition-all duration-300"
          onClick={handleShare}
        >
          <Image
            src={ShareIcon}
            alt="Share"
            width={16}
            height={16}
            className="text-white cursor-pointer"
          />
        </div>
      </div>
      <div className="p-3 md:p-4 flex flex-col gap-1 bg-white rounded-b-xl overflow-hidden">
        <div
          className="text-black font-normal self-stretch"
          style={{ fontSize: fluidSize(14, 16) }}
        >
          {nftName}
        </div>
        <div
          className="flex justify-between items-center self-stretch pt-2 cursor-pointer active:opacity-50 transition-opacity duration-300"
          onClick={handleCheckDetails}
        >
          <div
            className="text-black/50 font-normal"
            style={{ fontSize: fluidSize(10, 12) }}
          >
            {nft.token_address || nft.collection_address
              ? "Check the details"
              : "Details not available"}
          </div>
          <div
            className="text-black/50 font-normal cursor-pointer"
            style={{ fontSize: fluidSize(10, 12) }}
            onClick={handleCheckDetails}
          >
            →
          </div>
        </div>
      </div>
    </div>
  );
}
