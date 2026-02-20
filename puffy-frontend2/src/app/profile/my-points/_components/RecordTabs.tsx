"use client";

import { ConfigProvider, Tabs } from "antd";
import { Campaign, ReferralResp } from "@/types";
import InvitationRecordTable from "./InvitationRecordTable";
import PointsRecordTable from "./PointsRecordTable";

interface RecordTabsProps {
  invitationRecord: ReferralResp[];
  campaigns: Campaign[];
  pointsRecord: {
    timestamp: number;
    points: string;
    details: string;
  }[];
  width: number;
}

export default function RecordTabs({
  invitationRecord,
  campaigns,
  pointsRecord,
  width,
}: RecordTabsProps) {
  return (
    <ConfigProvider
      theme={{
        components: {
          Tabs: {
            colorPrimary: "#FF2CFF",
            itemSelectedColor: "#FF2CFF",
            itemHoverColor: "#000000",
            itemColor: "#00000080",
            fontWeightStrong: 400,
            titleFontSize: width > 768 ? 16 : 12,
          },
        },
      }}
    >
      <Tabs
        items={[
          {
            key: "1",
            label: "Invitation Record",
            children: (
              <InvitationRecordTable
                referralData={invitationRecord}
                campaigns={campaigns}
              />
            ),
          },
          {
            key: "2",
            label: "Points Record",
            children: <PointsRecordTable pointsRecord={pointsRecord} />,
          },
        ]}
        style={{
          width: "100%",
          backgroundColor: "#F1F1F1",
          fontFamily: "Lexend",
        }}
      />
    </ConfigProvider>
  );
}
