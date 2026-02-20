"use client";

import { fluidSize } from "@/lib/utils";
import { Campaign, ReferralResp } from "@/types";
import NoInvitationRecord from "./NoInvitationRecord";

interface InvitationRecordTableProps {
  referralData: ReferralResp[];
  campaigns: Campaign[];
}

export default function InvitationRecordTable({
  referralData,
  campaigns,
}: InvitationRecordTableProps) {
  return (
    <>
      {referralData.length > 0 ? (
        <div className="w-full rounded-xl border border-[#E2E2E2] max-h-[500px] overflow-hidden font-pingfang">
          <div
            className="overflow-y-auto max-h-[500px]"
            style={{ fontSize: fluidSize(12, 16) }}
          >
            {/* Table header for invitation record */}
            <div className="grid grid-cols-11 items-center px-4 py-2 text-[#17191A] border-b border-[#E2E2E2] gap-2">
              <div className="text-left col-span-3">Time</div>
              <div className="text-left col-span-4">Wallet</div>
              <div className="text-left col-span-4">Campaign</div>
            </div>
            {[...referralData].map((record, idx) => (
              <div
                key={idx}
                className={`grid grid-cols-11 items-center px-4 py-2 text-[#17191A] font-normal gap-2 ${
                  idx !== 0 ? "border-t border-[#E2E2E2]" : ""
                }`}
              >
                <div className="text-left col-span-3">
                  {new Date(
                    (record.timestamp || 0) * 1000
                  ).toLocaleDateString()}
                </div>
                <div className="truncate col-span-4">{`${record.wallet.slice(
                  0,
                  8
                )}...${record.wallet.slice(-8)}`}</div>
                <div className="text-left col-span-4">
                  {
                    campaigns.find(
                      (campaign) => campaign.campaign_id === record.campaign_id
                    )?.name
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <NoInvitationRecord />
      )}
    </>
  );
}
