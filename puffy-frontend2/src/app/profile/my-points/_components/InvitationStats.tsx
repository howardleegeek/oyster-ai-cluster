"use client";

import { fluidSize } from "@/lib/utils";
import Image from "next/image";
import podsPackImage from "@/public/profile/pack.png";

interface InvitationStatsProps {
  invitationCount: number;
  puffyPoints: number;
  podsPack: number;
}

export default function InvitationStats({
  invitationCount,
  puffyPoints = 600,
  podsPack = 0,
}: InvitationStatsProps) {
  return (
    <div className="flex gap-6 sm:gap-10">
      <div className="flex flex-col gap-2">
        <div
          className="text-[#17191A] font-normal"
          style={{ fontSize: fluidSize(14, 16) }}
        >
          Current inviter
        </div>
        <div
          className="text-[#1A1A1A] font-medium"
          style={{ fontSize: fluidSize(28, 32) }}
        >
          {invitationCount}
        </div>
      </div>

      <div className="w-[1px] bg-black/10" />

      <div className="flex flex-col gap-2">
        <div
          className="text-[#17191A] font-normal"
          style={{ fontSize: fluidSize(14, 16) }}
        >
          Puffy points
        </div>
        <div
          className="text-[#1A1A1A] font-medium"
          style={{ fontSize: fluidSize(28, 32) }}
        >
          {puffyPoints}
        </div>
      </div>

      <div className="w-[1px] bg-black/10" />

      <div className="flex flex-col gap-2">
        <div
          className="text-[#17191A] font-normal"
          style={{ fontSize: fluidSize(14, 16) }}
        >
          Pods Pack
        </div>
        <div
          className="text-[#1A1A1A] font-medium flex flex-row gap-2 items-center"
          style={{ fontSize: fluidSize(28, 32) }}
        >
          <Image src={podsPackImage} alt="Pods Pack" width={28} height={28} />
          {podsPack}
        </div>
      </div>
    </div>
  );
}
