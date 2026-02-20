"use client";

import WagmiContext from "@/components/features/wagmi/WagmiContext";
import { ReactNode } from "react";

export default function EthLayout({ children }: { children: ReactNode }) {
  return (
    <WagmiContext cookies={null}>
      {children}
    </WagmiContext>
  );
}