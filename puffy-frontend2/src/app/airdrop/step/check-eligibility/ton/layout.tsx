"use client";

import { TonConnectUIProvider } from "@tonconnect/ui-react";
import { ReactNode } from "react";

export default function TonLayout({ children }: { children: ReactNode }) {
  return (
    <TonConnectUIProvider
      manifestUrl={
        process.env.NEXT_PUBLIC_APP_URL + "/tonconnect-manifest.json"
      }
    >
      {children}
    </TonConnectUIProvider>
  );
}