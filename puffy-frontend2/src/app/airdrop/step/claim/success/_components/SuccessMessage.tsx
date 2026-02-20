"use client";

import { fluidSize } from "@/lib/utils";
import CheckCircleFilled from "@/public/airdrop/claim/success.svg";
import Image from "next/image";

interface SuccessMessageProps {
  title?: string;
  onViewNft?: () => void;
}

export default function SuccessMessage({
  title = "Puffy-1 WL Minted!",
  onViewNft,
}: SuccessMessageProps) {
  return (
    <div className="w-full flex flex-col justify-start items-center gap-3">
      <div className="flex justify-start items-center gap-3">
        <Image
          src={CheckCircleFilled}
          alt="Success"
          width={32}
          height={32}
          style={{ width: fluidSize(28, 32) }}
        />
        <div
          className="text-black/90 font-medium"
          style={{
            fontSize: fluidSize(20, 32),
            lineHeight: "22px",
          }}
        >
          {title}
        </div>
      </div>
      <div
        className="text-black/90 underline cursor-pointer active:scale-95 transition-all duration-300"
        style={{
          fontSize: fluidSize(12, 16),
        }}
        onClick={onViewNft}
      >
        View My NFT →
      </div>
    </div>
  );
}
