"use client";

import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { Suspense } from "react";
import { WalletLoginProvider } from "@/hooks/common/useWalletLogin";
import { QueryProviders } from "@/providers/QueryProviders";
import SolanaWalletProvider from "@/providers/SolanaWalletProvider";
import { TwitterAuthProvider } from "@/hooks";
import { CartProvider } from "@/contexts/CartContext";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <ProvidersWithoutSuspense>{children}</ProvidersWithoutSuspense>
    </Suspense>
  );
}

export function ProvidersWithoutSuspense({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <QueryProviders>
        <SolanaWalletProvider>
          <WalletLoginProvider>
            <CartProvider>
              <TwitterAuthProvider>{children}</TwitterAuthProvider>
            </CartProvider>
          </WalletLoginProvider>
        </SolanaWalletProvider>
      </QueryProviders>
    </>
  );
}
