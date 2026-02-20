"use client";

import MainButton from "@/app/airdrop/_components/MainButton";
import MainSection from "@/app/airdrop/_components/MainSection";
import { useRouter } from "next/navigation";

export default function CampaignIdNotFound() {
  const router = useRouter();

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <MainSection
        image={null}
        title="Campaign not found"
        description="The campaign you are looking for does not exist."
        button={
          <MainButton onClick={() => router.push("/airdrop")}>
            Go to home
          </MainButton>
        }
      />
    </div>
  );
}
