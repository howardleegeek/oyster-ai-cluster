"use client";

import { useMemo, useState } from "react";
import { Button, message } from "antd";
import { CheckCircleFilled, CloseCircleFilled } from "@ant-design/icons";

import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import { useGetUserInfoUserInfoGet } from "@/types";
import { NOTIFICATION_CONFIG } from "@/components/common/notificationConfig";
import { fluidSize } from "@/lib/utils";
import {
  useCreateDevicePass,
  useDevicePassSummary,
} from "@/hooks/purchase/useDevicePurchase";

function isWlHolderFromUserInfo(userInfo: any) {
  const nfts = userInfo?.nfts?.filter((n: any) => n?.status !== "new");
  return Array.isArray(nfts) && nfts.length > 0;
}

export default function DevicePassPage() {
  const { status } = useWalletLogin();
  const [api, contextHolder] = message.useMessage();
  const { data: userInfo } = useGetUserInfoUserInfoGet({
    query: { enabled: status === "authenticated" },
  });

  const wlHolder = useMemo(() => isWlHolderFromUserInfo(userInfo), [userInfo]);

  const { data: summary, refetch, isFetching } = useDevicePassSummary(
    status === "authenticated" && wlHolder
  );
  const { mutateAsync: createPass, isPending } = useCreateDevicePass();
  const [latestCode, setLatestCode] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      const res = await createPass();
      setLatestCode(res.code);
      await refetch();
      api.success({
        content: "Device Pass created. Copy and share it with your friend.",
        ...NOTIFICATION_CONFIG,
        icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
      });
    } catch (e: any) {
      api.error({
        content:
          e?.response?.data?.detail || e?.message || "Failed to create Device Pass.",
        ...NOTIFICATION_CONFIG,
        icon: <CloseCircleFilled style={{ color: "#E62C4B" }} />,
      });
    }
  };

  const handleCopy = async () => {
    if (!latestCode) return;
    await navigator.clipboard.writeText(latestCode);
    api.success({
      content: "Copied Device Pass code.",
      ...NOTIFICATION_CONFIG,
      icon: <CheckCircleFilled style={{ color: "#FF2CFF" }} />,
    });
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      {contextHolder}
      <div className="flex flex-col max-w-[600px] w-full px-[12px]">
        <div
          className="text-[#17191A] font-semibold font-pingfang mb-6 md:mb-10"
          style={{ fontSize: fluidSize(20, 24) }}
        >
          Device Pass
        </div>

        {!wlHolder ? (
          <div className="w-full p-4 rounded-2xl border border-black/10 bg-white">
            <div className="text-black font-medium mb-1">Not eligible</div>
            <div className="text-black/60" style={{ fontSize: 13 }}>
              Device Passes are issued to Puffy WL NFT holders. If you have a WL NFT,
              reconnect your wallet and refresh.
            </div>
          </div>
        ) : (
          <div className="w-full p-4 rounded-2xl border border-black/10 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-black font-medium">Available passes</div>
                <div className="text-black/60" style={{ fontSize: 13 }}>
                  {isFetching ? "Loading…" : summary ? summary.available : "—"}
                </div>
              </div>
              <Button
                type="primary"
                onClick={handleGenerate}
                disabled={isPending}
                loading={isPending}
                className="rounded-full"
                style={{ background: "black", borderColor: "black" }}
              >
                Generate
              </Button>
            </div>

            <div className="mt-3 text-black/50" style={{ fontSize: 12 }}>
              Each Device Pass is one-time-use. It covers the device price only; your
              friend still pays shipping.
            </div>

            {latestCode && (
              <div className="mt-4 p-3 rounded-xl border border-black/10 bg-[#F7F7F7]">
                <div className="text-black/60" style={{ fontSize: 12 }}>
                  Latest code
                </div>
                <div className="mt-1 flex items-center justify-between gap-2">
                  <div className="text-black font-mono break-all">{latestCode}</div>
                  <Button onClick={handleCopy} className="rounded-full">
                    Copy
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

