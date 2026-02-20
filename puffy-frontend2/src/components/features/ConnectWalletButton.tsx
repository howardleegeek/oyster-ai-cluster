"use client";

import { useWallet } from "@solana/wallet-adapter-react";
import { useEffect, useState } from "react";
import Image from "next/image";
import { fluidSize } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import walletIcon from "@/public/layout/wallet.png";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useRouter } from "next/navigation";
import exitIcon from "@/public/layout/exit.png";
import listIcon from "@/public/layout/list.png";

const MENU_ITEMS = [
  {
    id: "puffy-pass-whitelist-profile",
    text: "My Profile",
    icon: listIcon,
    link: "/profile/my-points",
  },
];

export default function ConnectWalletButton() {
  return <MainConnectWalletButton />;
}

function MainConnectWalletButton() {
  const { logout, signin, status: authStatus } = useWalletLogin();
  const { publicKey, disconnect } = useWallet();
  const [open, setOpen] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const preloadImages = [
      exitIcon,
      listIcon,
      ...MENU_ITEMS.map((item) => item.icon),
    ];
    preloadImages.forEach((src) => {
      const img = new window.Image();
      img.src = src.src;
    });
  }, []);

  // Show avatar + dropdown whenever wallet is connected (publicKey exists)
  const isWalletConnected = !!publicKey;

  const handleDisconnect = () => {
    logout();
    disconnect();
    setOpen(false);
  };

  // Not connected at all → show wallet icon to trigger connect
  if (!isWalletConnected) {
    return (
      <Image
        src={walletIcon}
        alt="wallet"
        width={96}
        height={96}
        priority
        quality={100}
        style={{
          width: fluidSize(28, 48),
          height: fluidSize(28, 48),
        }}
        className="cursor-pointer active:scale-95 transition-transform"
        onClick={() => signin()}
      />
    );
  }

  // Wallet connected → show avatar with dropdown
  return (
    <div className="relative">
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <div
            className="flex items-center justify-center rounded-full bg-[#1a1a1a] border border-black cursor-pointer active:scale-95 transition-transform"
            style={{
              width: fluidSize(28, 48),
              height: fluidSize(28, 48),
              color: "white",
              fontWeight: "bold",
              fontSize: fluidSize(12, 18),
            }}
          >
            {publicKey.toBase58().charAt(0)}
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          className="rounded-xl bg-white text-black flex flex-col gap-[20px] border border-black/10 shadow-[0_4px_20px_0_rgba(0,0,0,0.1)]"
          style={{ padding: fluidSize(12, 20) }}
          align="end"
        >
          {/* Wallet address – click to copy */}
          <DropdownMenuItem
            onClick={() => {
              navigator.clipboard.writeText(publicKey.toBase58());
              setOpen(false);
            }}
            className="gap-2xs cursor-pointer font-medium focus:bg-accent-foreground focus:text-foreground active:scale-95 transition-transform md:hover:scale-105 p-0"
            style={{ fontSize: fluidSize(12, 22) }}
          >
            <div
              className="flex items-center justify-center rounded-full bg-black"
              style={{
                width: fluidSize(16, 24),
                height: fluidSize(16, 24),
                color: "white",
                fontWeight: "bold",
                fontSize: fluidSize(8, 12),
              }}
            >
              {publicKey.toBase58().charAt(0)}
            </div>
            <span style={{ fontSize: fluidSize(12, 14), fontWeight: "bold" }}>
              {publicKey.toBase58().slice(0, 4)}...
              {publicKey.toBase58().slice(-4)}
            </span>
          </DropdownMenuItem>

          {/* My Profile */}
          {MENU_ITEMS.map((item) => (
            <DropdownMenuItem
              key={item.id}
              className="gap-2xs cursor-pointer font-medium focus:bg-accent-foreground focus:text-foreground active:scale-95 transition-transform md:hover:scale-105 p-0"
              onClick={() => {
                router.push(item.link);
                setOpen(false);
              }}
              style={{ fontSize: fluidSize(12, 22) }}
            >
              <Image
                src={item.icon}
                alt={item.text}
                width={24}
                height={24}
                priority
                style={{
                  width: fluidSize(16, 24),
                  height: fluidSize(16, 24),
                }}
              />
              <span style={{ fontSize: fluidSize(12, 14) }}>{item.text}</span>
            </DropdownMenuItem>
          ))}

          {/* Disconnect */}
          <DropdownMenuItem
            className="gap-2xs cursor-pointer font-medium focus:bg-accent-foreground focus:text-foreground active:scale-95 transition-transform md:hover:scale-105 p-0"
            onClick={handleDisconnect}
            style={{ fontSize: fluidSize(12, 22) }}
          >
            <Image
              src={exitIcon}
              alt="Exit"
              width={24}
              height={24}
              priority
              style={{
                width: fluidSize(16, 24),
                height: fluidSize(16, 24),
              }}
            />
            <span style={{ fontSize: fluidSize(12, 14) }}>Disconnect</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
