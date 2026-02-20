import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function PrimaryDisplayCard({
  image,
  title,
  description,
  button
}: {
  image: React.ReactNode;
  title: string;
  description: string;
  button: React.ReactNode;
}) {
  return (
    <Card className="bg-[#18181a] rounded-lg py-lg px-md w-full">
      <div className="flex flex-col items-center justify-center">
        {image}
        <CardHeader className="flex flex-col items-center justify-center px-0 gap-sm">
          <CardTitle className="text-title-xl">{title}</CardTitle>
          <CardDescription className="text-center text-white opacity-50 text-body-sm">{description}</CardDescription>
        </CardHeader>
        {button}
      </div>
    </Card>
  );
}

