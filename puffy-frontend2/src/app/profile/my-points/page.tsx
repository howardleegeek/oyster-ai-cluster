"use client";

import { fluidSize } from "@/lib/utils";
import React, { useMemo } from "react";
import { useWalletLogin } from "@/hooks/common/useWalletLogin";
import {
  useGetAllReferralRelationReferralRelationGet,
  useGetCampaignsCampaignsGet,
  useGetUserInfoUserInfoGet,
} from "@/types";
import "@/mocks/init";
import useWindow from "@/hooks/common/useWindow";
import InvitationStats from "./_components/InvitationStats";
import InvitationLink from "./_components/InvitationLink";
import RecordTabs from "./_components/RecordTabs";
import { MIN_CASHOUT_POINTS, REFERRAL_POINTS, formatNumber } from "@/lib/puffyRules";
import { Button } from "antd";

export default function MyPointsPage() {
  const { status } = useWalletLogin();
  const { width } = useWindow();
  const { data: campaigns } = useGetCampaignsCampaignsGet({
    query: {
      enabled: true,
    },
  });
  const { data: userInfo } = useGetUserInfoUserInfoGet({
    query: {
      enabled: status === "authenticated",
    },
  });
  // Use correct options structure for TanStack Query hooks
  const { data: invitationRecord } =
    useGetAllReferralRelationReferralRelationGet({
      query: {
        enabled: !!campaigns && status === "authenticated",
        select: (data) => {
          return [...data].sort((a, b) => {
            if (a.timestamp && b.timestamp) {
              return b.timestamp - a.timestamp;
            }
            return 0;
          });
        },
      },
    });

  const pointsRecord = useMemo(() => {
    if (!userInfo) {
      return [];
    }
    const pointsRecord = [];
    for (const activity of userInfo.user_activities || []) {
      // Convert completed_at to timestamp (seconds), default to 0 if not present
      pointsRecord.push({
        timestamp: activity.completed_at
          ? Math.floor(new Date(activity.completed_at).getTime() / 1000)
          : 0,
        points: activity.points?.toString() || "0",
        details: activity.activity?.description || "",
      });
    }
    return pointsRecord;
  }, [userInfo]);

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <div className="flex flex-col max-w-[600px] w-full px-[12px]">
        <div
          className="text-[#17191A] font-semibold font-pingfang mb-6 md:mb-10"
          style={{ fontSize: fluidSize(20, 24) }}
        >
          My Invitation
        </div>

        <InvitationStats
          invitationCount={invitationRecord?.length || 0}
          puffyPoints={userInfo?.points || 0}
          podsPack={userInfo?.products?.length || 0}
        />
        <div className="mt-4 p-4 rounded-2xl border border-black/10 bg-white">
          <div className="text-black font-medium mb-2">Cash out</div>
          <div className="text-black/60" style={{ fontSize: 13 }}>
            Cash out requires at least {formatNumber(MIN_CASHOUT_POINTS)} points, a verified
            email + wallet, and no abnormal behavior flags.
          </div>
          <div className="mt-3 flex flex-col gap-1 text-black/70" style={{ fontSize: 13 }}>
            <div>
              - Points threshold:{" "}
              {(userInfo?.points || 0) >= MIN_CASHOUT_POINTS ? "met" : "not met"}
            </div>
            <div>- Email: {userInfo?.email ? "added" : "missing"}</div>
            <div>- Wallet: {userInfo?.wallet_address ? "connected" : "missing"}</div>
          </div>
          <div className="mt-3">
            <Button
              disabled={
                (userInfo?.points || 0) < MIN_CASHOUT_POINTS || !userInfo?.email || !userInfo?.wallet_address
              }
              className="rounded-full"
            >
              Cash out (coming soon)
            </Button>
          </div>
        </div>
        <div className="mt-6 md:mt-10" />
        {userInfo?.referral_code && (
          <InvitationLink
            referralCode={userInfo.referral_code}
            containerClassName=""
          />
        )}
        <div className="mt-4 p-4 rounded-2xl border border-black/10 bg-white">
          <div className="text-black font-medium mb-2">How you earn Puffy Points</div>
          <div className="text-black/70" style={{ fontSize: 13 }}>
            - Device Pass referral: +{REFERRAL_POINTS.devicePassReferralReferrer} to referrer
          </div>
          <div className="text-black/70" style={{ fontSize: 13 }}>
            - Paid device referral ($99): +{REFERRAL_POINTS.paidDeviceReferralReferrer} to referrer, +{REFERRAL_POINTS.paidDeviceReferralReferee} to referee
          </div>
        </div>
        <div style={{ height: fluidSize(32, 50) }} />
        <RecordTabs
          invitationRecord={invitationRecord || []}
          campaigns={campaigns || []}
          pointsRecord={pointsRecord}
          width={width}
        />
      </div>
    </div>
  );
}
