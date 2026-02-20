"use client";

import { fluidSize } from "@/lib/utils";
import {
  ArrowLeftOutlined,
  CloseOutlined,
  CheckOutlined,
} from "@ant-design/icons";
import Steps from "./_components/Steps";
import { ReactNode, useEffect } from "react";
import {
  StepProvider,
  useSteps,
  ROUTE_STEP_MAP,
} from "./_components/StepContext";
import { useRouter, usePathname } from "next/navigation";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <StepProvider numberOfSteps={8} initialStep={1}>
      <LayoutContent>{children}</LayoutContent>
    </StepProvider>
  );
}

function LayoutContent({ children }: { children: ReactNode }) {
  const { currentStep, setCurrentStep, numberOfSteps } = useSteps();
  const router = useRouter();
  const pathname = usePathname();

  // Check if current page is success page
  const isSuccessPage = pathname.includes("/claim/success");

  // Update step based on current route
  useEffect(() => {
    const routeInfo = ROUTE_STEP_MAP[pathname];
    if (routeInfo) {
      setCurrentStep(routeInfo.step);
    }
  }, [pathname, setCurrentStep]);

  // Handle back navigation
  const handleBack = () => {
    router.back();
  };

  // Handle close/confirm navigation
  const handleClose = () => {
    if (isSuccessPage) {
      router.push("/profile/my-points");
    } else {
      router.push("/airdrop");
    }
  };

  return (
    <div className="w-full h-full flex flex-col flex-1">
      {/* Header with navigation and steps */}
      <div
        className="w-full text-black/50"
        style={{ fontSize: fluidSize(12, 16) }}
      >
        {/* Desktop layout: back - steps - close */}
        <div className="hidden md:flex flex-row items-center justify-between mb-2">
          {/* back - hidden on success page */}
          {isSuccessPage ? (
            <div className="w-12 h-12 mr-10" />
          ) : (
            <div
              className="flex flex-row items-center gap-2 px-8 h-12 cursor-pointer bg-white/90 rounded-[60px] mr-10 active:scale-95 transition-all duration-300"
              onClick={handleBack}
            >
              <ArrowLeftOutlined />
              Back
            </div>
          )}

          {/* steps */}
          <div className="w-full max-w-[650px] flex items-center justify-center">
            <Steps
              numberOfSteps={numberOfSteps}
              currentStep={currentStep}
              setCurrentStep={setCurrentStep}
            />
          </div>

          {/* close/confirm button */}
          <div
            className="h-12 w-12 cursor-pointer bg-white/90 rounded-full aspect-square flex items-center justify-center ml-10 active:scale-95 transition-all duration-300"
            onClick={handleClose}
          >
            {isSuccessPage ? <CheckOutlined /> : <CloseOutlined />}
          </div>
        </div>

        {/* Mobile layout: two rows */}
        <div className="md:hidden flex flex-col gap-6 pb-12">
          {/* First row: back and close */}
          <div
            className={`flex flex-row items-center ${isSuccessPage ? "justify-end" : "justify-between"}`}
          >
            {/* back - hidden on success page */}
            {!isSuccessPage && (
              <div
                className="flex flex-row items-center gap-2 px-5 h-8 cursor-pointer bg-white/90 rounded-[60px] active:scale-95 transition-all duration-300"
                onClick={handleBack}
              >
                <ArrowLeftOutlined />
                Back
              </div>
            )}

            {/* close/confirm button */}
            <div
              className="h-8 w-8 cursor-pointer bg-white/90 rounded-full aspect-square flex items-center justify-center active:scale-95 transition-all duration-300"
              onClick={handleClose}
            >
              {isSuccessPage ? <CheckOutlined /> : <CloseOutlined />}
            </div>
          </div>

          {/* Second row: steps full width */}
          <div className="w-full">
            <Steps
              numberOfSteps={numberOfSteps}
              currentStep={currentStep}
              setCurrentStep={setCurrentStep}
            />
          </div>
        </div>
      </div>

      {/* Children content */}
      <div className="w-full flex flex-col items-center justify-center flex-1">
        {children}
      </div>
    </div>
  );
}
