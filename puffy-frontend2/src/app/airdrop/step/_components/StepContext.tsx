"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { usePathname } from "next/navigation";

// Route to step mapping - exported for use in other components
export const ROUTE_STEP_MAP: Record<string, { step: number }> = {
  // Step 1: Check Eligibility
  "/airdrop/step/check-eligibility": { step: 1 },

  // Step 2: Chain Selection
  "/airdrop/step/check-eligibility/eth": { step: 2 },
  "/airdrop/step/check-eligibility/solana": { step: 2 },
  "/airdrop/step/check-eligibility/ton": { step: 2 },
  "/airdrop/step/check-eligibility/invitation": { step: 2 },

  // Step 3: Verify Eligibility / Non-eligible pages
  "/airdrop/step/check-eligibility/solana/communities": { step: 3 },
  "/airdrop/step/check-eligibility/ton/communities": { step: 3 },
  "/airdrop/step/check-eligibility/eth/communities": { step: 3 },
  "/airdrop/step/check-eligibility/invitation/communities": { step: 3 },
  "/airdrop/step/check-eligibility/eth/non-eligible": { step: 3 },
  "/airdrop/step/check-eligibility/solana/non-eligible": { step: 3 },
  "/airdrop/step/check-eligibility/ton/non-eligible": { step: 3 },
  "/airdrop/step/check-eligibility/invitation/non-eligible": { step: 3 },

  // Step 4: Connect Wallet
  "/airdrop/step/claim/connect-wallet": { step: 4 },

  // Step 5: Email
  "/airdrop/step/claim/email": { step: 5 },

  // Step 6: Choose NFT
  "/airdrop/step/claim/choose": { step: 6 },

  // Step 7: Mint NFT
  "/airdrop/step/claim/mint": { step: 7 },

  // Step 8: Success
  "/airdrop/step/claim/success": { step: 8 },
};

interface StepContextType {
  currentStep: number;
  setCurrentStep: (step: number) => void;
  numberOfSteps: number;
}

const StepContext = createContext<StepContextType | undefined>(undefined);

export const useSteps = () => {
  const context = useContext(StepContext);
  if (!context) {
    throw new Error("useSteps must be used within a StepProvider");
  }
  return context;
};

// Hook to get current route step information
export const useCurrentStep = () => {
  const pathname = usePathname();
  return ROUTE_STEP_MAP[pathname];
};

interface StepProviderProps {
  children: ReactNode;
  numberOfSteps?: number;
  initialStep?: number;
}

export function StepProvider({
  children,
  numberOfSteps = 3,
  initialStep = 1,
}: StepProviderProps) {
  const [currentStep, setCurrentStep] = useState(initialStep);

  const handleStepChange = (step: number) => {
    setCurrentStep(step);
  };

  return (
    <StepContext.Provider
      value={{
        currentStep,
        setCurrentStep: handleStepChange,
        numberOfSteps,
      }}
    >
      {children}
    </StepContext.Provider>
  );
}
