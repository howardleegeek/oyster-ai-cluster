"use client";

import { fluidSize } from "@/lib/utils";
import NoInvitationRecord from "./NoInvitationRecord";

interface PointsRecordTableProps {
  pointsRecord: {
    timestamp: number;
    points: string;
    details: string;
  }[];
}

export default function PointsRecordTable({ pointsRecord }: PointsRecordTableProps) {
  return (
    <>
      {pointsRecord.length > 0 ? (
        <div className="w-full rounded-xl border border-[#E2E2E2] max-h-[500px] overflow-hidden">
          <div
            className="overflow-y-auto max-h-[500px]"
            style={{ fontSize: fluidSize(12, 16) }}
          >
            {/* Table header for points record */}
            <div className="grid grid-cols-11 items-center px-4 py-2 text-[#17191A] border-b border-[#E2E2E2] gap-2">
              <div className="text-left col-span-3">Time</div>
              <div className="text-left col-span-4">Points</div>
              <div className="text-left col-span-4">Details</div>
            </div>
            {[...pointsRecord].map((record, idx) => (
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
                <div className="truncate col-span-4">+ {record.points}</div>
                <div className="text-left col-span-4">{record.details}</div>
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