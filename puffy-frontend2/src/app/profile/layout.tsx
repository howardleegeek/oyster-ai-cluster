"use client";

import ProfileMenu from "./_components/ProfileMenu";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { fluidSize } from "@/lib/utils";
import { useRouter, usePathname } from "next/navigation";
import { useWallet } from "@solana/wallet-adapter-react";
import { useEffect } from "react";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import polygonIcon from "@/public/profile/polygon.svg";
import invitationIcon from "@/public/profile/invitation.svg";
import emailIcon from "@/public/profile/email.svg";
import invitationIcon2 from "@/public/profile/invitation.svg";
import ordersIcon from "@/public/layout/list.svg";

export default function ProfileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { logout } = useWalletLogin();
  const { publicKey, disconnect } = useWallet();

  const formatWalletAddress = (address: string) => {
    if (address.length <= 8) return address;
    return `${address.slice(0, 4)}...${address.slice(-4)}`;
  };

  // If no wallet connected, redirect to sign-in
  useEffect(() => {
    if (!publicKey) {
      const timer = setTimeout(() => router.push("/sign-in"), 500);
      return () => clearTimeout(timer);
    }
  }, [publicKey, router]);

  const handleDisconnect = () => {
    logout();
    disconnect();
  };

  // No wallet → show nothing while redirecting
  if (!publicKey) {
    return null;
  }

  // Wallet connected → show profile immediately
  return (
    <div className="w-full min-h-screen flex flex-col items-center justify-center bg-[#F1F1F1]">
      <header className="w-full z-10" style={{ padding: fluidSize(16, 24) }}>
        <Header />
      </header>

      <div className="w-full flex flex-1 flex-col md:flex-row items-start justify-center max-w-[900px] gap-4 md:gap-20">
        {/* menu */}
        <div className="w-full md:w-auto p-4 md:p-6">
          <ProfileMenu
            walletAddress={formatWalletAddress(publicKey.toString())}
            onDisconnect={handleDisconnect}
            menuItems={[
              {
                icon: ordersIcon,
                text: "My Orders",
                onClick: () => router.push("/profile/orders"),
                active: pathname.startsWith("/profile/orders"),
              },
              {
                icon: invitationIcon,
                text: "My Invitation",
                onClick: () => router.push("/profile/my-points"),
                active: pathname === "/profile/my-points",
              },
              {
                icon: invitationIcon2,
                text: "Device Pass",
                onClick: () => router.push("/profile/device-pass"),
                active: pathname === "/profile/device-pass",
              },
              {
                icon: polygonIcon,
                text: "My NFT",
                onClick: () => router.push("/profile/my-nfts"),
                active: pathname === "/profile/my-nfts",
              },
              {
                icon: emailIcon,
                text: "My Email",
                onClick: () => router.push("/profile/my-email"),
                active: pathname === "/profile/my-email",
              },
            ]}
          />
        </div>

        {/* content */}
        <div className="flex-1 w-full">{children}</div>
      </div>

      <footer className="w-full z-10" style={{ padding: fluidSize(16, 24) }}>
        <Footer />
      </footer>
    </div>
  );
}
