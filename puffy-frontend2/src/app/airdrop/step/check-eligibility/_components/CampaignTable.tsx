"use client";

import { useState } from "react";
import Pagination from "@mui/material/Pagination";
import Stack from "@mui/material/Stack";
import CampaignCard from "./CampaignCard";

interface CampaignTableProps {
  campaigns: { id: number; onClick: () => void }[];
  className?: string;
}

export default function CampaignTable({
  campaigns,
  className = "",
}: CampaignTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 4; // 2 rows × 2 columns = 4 items per page

  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentCampaignIds = campaigns.slice(startIndex, endIndex);

  const handlePageChange = (
    event: React.ChangeEvent<unknown>,
    page: number
  ) => {
    setCurrentPage(page);
  };

  const totalPages = Math.ceil(campaigns.length / pageSize);

  return (
    <div className={`max-w-[1000px] w-full flex flex-col gap-4 ${className}`}>
      {/* Campaign Grid - 2x2 layout */}
      <div className="w-auto grid grid-cols-1 md:grid-cols-2 gap-4">
        {currentCampaignIds.map((campaign) => (
          <div
            className="w-full flex flex-col items-center justify-center"
            key={campaign.id}
          >
            <CampaignCard
              campaignId={campaign.id.toString()}
              onClick={campaign.onClick}
            />
          </div>
        ))}
      </div>

      {/* Pagination */}
      {campaigns.length > pageSize && (
        <div className="flex justify-center md:mt-20 mt-10">
          <Stack spacing={2}>
            <Pagination
              count={totalPages}
              page={currentPage}
              onChange={handlePageChange}
            />
          </Stack>
        </div>
      )}
    </div>
  );
}
