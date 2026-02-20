import { Card, CardDescription } from "@/components/ui/card";

export default function IconCard({ image, description }: { image: React.ReactNode; description: string }) {
  return (
    <Card className="bg-[#18181a] rounded-lg py-xs px-xs w-full">
      <div className="flex flex-col gap-2xs justify-start items-start">
        {image}
        <CardDescription className="text-left text-white opacity-50 text-body-sm whitespace-pre-line">
          {description}
        </CardDescription>
      </div>
    </Card>
  );
}
