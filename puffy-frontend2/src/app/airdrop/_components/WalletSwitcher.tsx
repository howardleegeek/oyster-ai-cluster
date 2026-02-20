"use client";

import { fluidSize } from "@/lib/utils";
import walletImage from "@/public/airdrop/wallet.svg";
import Image, { StaticImageData } from "next/image";

export interface WalletSwitchProps {
  icon?: StaticImageData;
  wallet: string;
  disconnect: () => void;
  showSwitchButton?: boolean;
}

export default function WalletSwitch({
  icon,
  wallet,
  disconnect,
  showSwitchButton = true,
}: WalletSwitchProps) {
  return (
    <div
      className="flex flex-row items-center gap-4 text-black/90"
      style={{ fontSize: fluidSize(12, 16) }}
    >
      <div className="flex flex-row items-center gap-2">
        <Image
          src={icon || walletImage}
          alt="wallet"
          width={24}
          height={24}
          className="rounded-full"
        />
        <div className="font-inter font-medium">
          {wallet.slice(0, 4)}...{wallet.slice(-4)}
        </div>
      </div>
      {showSwitchButton && (
        <button
          className="font-pingfang px-[18px] py-[5px] border border-black/10 rounded-[60px] cursor-pointer active:scale-95 transition-all duration-300"
          onClick={disconnect}
        >
          Swicth
        </button>
      )}
    </div>
  );
}
