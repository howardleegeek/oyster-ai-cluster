"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import SolIcon from "@/public/airdrop/check-eligibility/solana.svg";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useEffect } from "react";
import Footer from "@/components/layout/Footer";
import Header from "@/components/layout/Header";
import { fluidSize } from "@/lib/utils";

export default function ConnectWalletPage() {
  const router = useRouter();
  const { signin, status } = useWalletLogin();

  const handleConnect = () => {
    if (status === "authenticated") {
      router.push("/profile/my-points");
      return;
    }
    signin();
  };

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/profile/my-points");
    }
  }, [router, status]);

  return (
    <div className="w-full h-screen flex flex-col items-center justify-center">
      <header
        className="w-full z-50 relative"
        style={{ padding: fluidSize(16, 24) }}
      >
        <Header />
      </header>
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
        title="Connect Your Wallet"
        description={
          <div className="max-w-[450px] text-center flex flex-col items-center justify-center gap-4">
            Connect your Solana wallet to access your profile and manage your
            assets.
          </div>
        }
        button={
          <MainButton onClick={handleConnect}>
            {status === "authenticated" ? "Go to Profile" : "Connect Wallet"}
          </MainButton>
        }
      />
      <footer className="w-full z-10" style={{ padding: fluidSize(16, 24) }}>
        <Footer />
      </footer>
    </div>
  );
}
