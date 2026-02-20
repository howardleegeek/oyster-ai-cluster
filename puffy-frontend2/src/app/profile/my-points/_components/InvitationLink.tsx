"use client";

import { cn, fluidSize } from "@/lib/utils";
import Image from "next/image";
import copyIcon from "@/public/profile/copy.svg";
import { message } from "antd";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { CheckCircleFilled } from "@ant-design/icons";

interface InvitationLinkProps {
  referralCode: string;
  containerClassName?: string;
  showDescription?: boolean;
}

export default function InvitationLink({
  referralCode,
  containerClassName = "",
  showDescription = true,
}: InvitationLinkProps) {
  const [api, contextHolder] = message.useMessage();

  const handleCopy = () => {
    navigator.clipboard.writeText(referralCode);
    api.success({
      content: "Copied the referral code to clipboard successfully!",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
  };

  return (
    <>
      {contextHolder}
      <div
        className={cn(
          "flex flex-col md:flex-row gap-4 items-start md:items-center",
          containerClassName
        )}
      >
        <div
          className="text-[#17191A] font-normal"
          style={{ fontSize: fluidSize(14, 14) }}
        >
          My Invitation Code:
        </div>

        <div className="flex flex-row gap-2 items-center">
          <div
            className="text-[#17191A] font-medium"
            style={{ fontSize: fluidSize(14, 14) }}
          >
            {referralCode}
          </div>
          <button
            className="flex flex-row gap-2 items-center justify-center bg-[#FF2CFF]/10 border border-[#FF2CFF]/20 rounded-full min-w-[85px] py-1 cursor-pointer active:scale-95 transition-all duration-200 ml-2 px-0 md:px-2"
            onClick={handleCopy}
          >
            <Image src={copyIcon} alt="Copy" />
            <div
              className="text-[#FF2CFF] font-normal"
              style={{ fontSize: fluidSize(12, 12) }}
            >
              Copy
            </div>
          </button>
        </div>
      </div>
      {showDescription && (
        <div
          className="text-black/50 font-normal mt-4"
          style={{ fontSize: fluidSize(10, 14) }}
        >
          Earn Puffy Points when friends purchase a device with your referral. Rewards
          are assigned after a successful checkout (including shipping payment).
        </div>
      )}
    </>
  );
}
