import Image from "next/image";
import bgImage from "@/public/reward-center/hero-background.png";
import { fluidSize } from "@/lib/utils";
export default function BackgroundImage() {
  return (
    <>
      <Image
        src={bgImage}
        alt="Background"
        style={{
          width: fluidSize(1550, 2560),
          height: fluidSize(870, 1440),
        }}
        className="w-full h-screen flex flex-col items-center absolute top-0 left-0 right-0 object-cover"
        priority
        quality={100}
      />
    </>
  );
}

// export default function BackgroundImage() {
//   return (
//     <>
//       <div
//         className="w-full h-screen flex flex-col items-center bg-gradient-to-b from-[#DDA2FB] from-0% via-[#FCE1FF] via-45% to-[#F2F2F2] absolute top-0 left-0 right-0"
//         style={{
//           width: "100%",
//         }}
//       />
//       <Image
//         src="/reward-center/cloud-left.png"
//         alt="Cloud 1"
//         width={600}
//         height={600}
//         className="absolute left-0 top-40"
//         style={{
//           width: fluidSize(200, 600),
//           height: "auto",
//         }}
//         priority
//       />
//       <Image
//         src="/reward-center/cloud-top.png"
//         alt="Cloud 2"
//         width={600}
//         height={600}
//         className="absolute -top-[90px] left-40"
//         style={{
//           width: fluidSize(200, 600),
//           height: "auto",
//         }}
//         priority
//       />
//       <Image
//         src="/reward-center/cloud-right.png"
//         alt="Cloud 3"
//         width={600}
//         height={600}
//         className="absolute right-0"
//         style={{
//           width: fluidSize(200, 600),
//           height: "auto",
//         }}
//         priority
//       />
//     </>
//   );
// }
