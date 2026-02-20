import messageIcon from "@/public/layout/puffy-icon.png";
import Image from "next/image";

export default function MessageIcon() {
  return (
    <div className="w-4 h-4 mr-2">
      <Image
        src={messageIcon}
        alt="Message"
        width={16}
        height={16}
      />
    </div>
  );
}