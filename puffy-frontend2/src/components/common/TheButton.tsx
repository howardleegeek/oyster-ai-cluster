import { Button } from "@/components/ui/button";

export default function TheButton({ children }: { children: React.ReactNode }) {
  return (
    <Button variant="default">
      {children}
    </Button>
  );
}
