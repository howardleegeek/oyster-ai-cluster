interface StepsProps {
  numberOfSteps: number;
  currentStep: number;
  setCurrentStep: (step: number) => void;
}

export default function Steps({
  numberOfSteps,
  currentStep,
  setCurrentStep,
}: StepsProps) {
  return (
    <div className="w-full flex flex-row items-center justify-between md:gap-3 gap-1">
      {Array.from({ length: numberOfSteps }, (_, index) => (
        <Step
          key={index}
          isActive={index + 1 <= currentStep}
          onClick={() => setCurrentStep(index + 1)}
        />
      ))}
    </div>
  );
}

function Step({
  isActive,
  onClick,
}: {
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className="cursor-pointer md:h-[6px] h-[4px]"
      style={{
        width: "100%",
        background: isActive ? "#1A1A1A" : "#D9D9D9",
        borderRadius: 20,
      }}
    ></div>
  );
}
