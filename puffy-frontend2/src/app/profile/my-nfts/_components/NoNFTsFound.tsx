"use client";

import { fluidSize } from "@/lib/utils";
import { useRouter } from "next/navigation";
import Image from "next/image";
import PolygonIcon from "@/public/profile/polygon.svg";
import MainButton from "@/app/airdrop/_components/MainButton";

export default function NoNFTsFound() {
  const router = useRouter();
  return (
    <div className="w-full flex flex-col justify-center items-center gap-10">
      <Image
        src={PolygonIcon}
        alt="No NFTs found"
        className="opacity-30"
        width={80}
        height={80}
      />
      <div className="flex flex-col items-center gap-4 self-stretch">
        <div
          className="text-center text-black font-semibold self-stretch"
          style={{ fontSize: fluidSize(18, 20) }}
        >
          No NFTs found
        </div>
        <div
          className="text-black/50 font-normal"
          style={{ fontSize: fluidSize(14, 16) }}
        >
          Participate in the event to receive NFT.
        </div>
      </div>

      <MainButton
        className="min-w-[160px]"
        onClick={() => router.push("/airdrop")}
      >
        Go to Mint
      </MainButton>
    </div>
  );
}
