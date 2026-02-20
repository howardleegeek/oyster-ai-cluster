"use client";

import { useState } from "react";
import { fluidSize } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useRouter } from "next/navigation";

export default function DropDownList({
  items,
}: {
  items: {
    name: string;
    link: string;
  }[];
}) {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  return (
    <>
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild disabled={false}>
          <div>
            <ListIcon
              className="cursor-pointer active:scale-95"
              onClick={() => {
                if (open) {
                  setOpen(false);
                } else {
                  setOpen(true);
                }
              }}
            />
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="border-none font-medium rounded-xl bg-white text-black">
          {items.map((item) => (
            <DropdownMenuItem
              key={item.name}
              className="gap-2xs cursor-pointer focus:bg-accent-foreground focus:text-foreground active:scale-95 transition-transform md:hover:scale-105"
              onClick={() => {
                setOpen(false);
                if (item.link) {
                  router.push(item.link);
                }
              }}
              style={{
                fontSize: fluidSize(12, 14),
              }}
            >
              <span style={{ fontSize: fluidSize(12, 14) }}>{item.name}</span>
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu >
    </>
  );
}

function ListIcon({
  className,
  onClick,
}: {
  className: string;
  onClick: () => void;
}) {
  return (
    <svg
      className={className}
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      onClick={onClick}
    >
      <rect x="4" y="4.5" width="16" height="2" rx="1" fill="black" />
      <rect x="4" y="10.5" width="16" height="2" rx="1" fill="black" />
      <rect x="4" y="16.5" width="16" height="2" rx="1" fill="black" />
    </svg>
  );
}
