"use client";

import { fluidSize } from "@/lib/utils";
import disconnectIcon from "@/public/profile/disconnect.svg";
import polygonIcon from "@/public/profile/polygon.svg";
import invitationIcon from "@/public/profile/invitation.svg";
import Image from "next/image";

interface MenuItemConfig {
  icon: string;
  text: string;
  onClick: () => void;
  active?: boolean;
}

interface ProfileMenuProps {
  walletAddress?: string;
  onDisconnect?: () => void;
  menuItems?: MenuItemConfig[];
}

export default function ProfileMenu({
  walletAddress = "Solana Address",
  onDisconnect,
  menuItems = [
    {
      icon: invitationIcon,
      text: "My points",
      onClick: () => {},
      active: true,
    },
    {
      icon: polygonIcon,
      text: "My NFT",
      onClick: () => {},
      active: false,
    },
  ],
}: ProfileMenuProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-6">
        <div
          className="rounded-[60px] border-4 border-white flex items-center justify-center text-white font-bold"
          style={{
            width: fluidSize(60, 80),
            height: fluidSize(60, 80),
            fontSize: fluidSize(24, 32),
            background: "linear-gradient(to bottom right, #a855f7, #ec4899)",
          }}
        >
          {walletAddress.charAt(0).toUpperCase()}
        </div>

        <div
          className="text-start text-black font-semibold"
          style={{ fontSize: fluidSize(20, 24) }}
        >
          {walletAddress}

          <div
            className="py-2 rounded-[60px] flex items-center gap-2 cursor-pointer hover:opacity-70 transition-opacity"
            onClick={onDisconnect}
          >
            <Image
              src={disconnectIcon}
              alt="Disconnect"
              width={24}
              height={24}
              className="text-black/50"
            />
            <div className="text-black/50 text-sm font-normal">Disconnect</div>
          </div>
        </div>
      </div>
      <div className="w-full h-[1px] bg-black opacity-10 hidden md:block" />
      <div className="w-full grid grid-cols-2 md:flex md:flex-col gap-3">
        {menuItems.map((item, index) => (
          <ProfileMenuItem
            key={index}
            icon={item.icon}
            text={item.text}
            onClick={item.onClick}
            active={item.active}
          />
        ))}
      </div>
    </div>
  );
}

interface ProfileMenuItemProps {
  icon: string;
  text: string;
  onClick: () => void;
  active?: boolean;
}

function ProfileMenuItem({
  icon,
  text,
  onClick,
  active = false,
}: ProfileMenuItemProps) {
  return (
    <div
      className={`w-full py-2.5 px-4 rounded-[60px] flex items-center gap-2 cursor-pointer transition-colors bg-[#F1F1F1] ${
        active ? "border-[1.50px] border-[#ED00ED]" : "border border-black/10"
      }`}
      onClick={onClick}
    >
      <div
        className={`flex items-center gap-2 ${active ? "opacity-90" : "opacity-50"}`}
      >
        <Image src={icon} alt={text} width={16} height={16} />
        <div className="text-sm text-black">{text}</div>
      </div>
    </div>
  );
}
