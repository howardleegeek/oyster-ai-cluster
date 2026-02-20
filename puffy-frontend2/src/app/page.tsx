import HomeHero from "./home/_components/Hero";
import Icons from "./home/_components/Icons";
import { fluidSize } from "@/lib/utils";
import Advantages from "./home/_components/Advantages";
import HowItWorks from "./home/_components/HowItWorks";
import Experience from "./home/_components/Ecxperience";
import Introduction from "./home/_components/Introduction";
import Timeline from "./home/_components/Timeline";
import Footer from "@/components/layout/Footer";
import Header from "@/components/layout/Header";

export default function Home() {
  return (
    <div className="w-full">
      <header
        className="w-full z-50 relative"
        style={{ padding: fluidSize(16, 24) }}
      >
        <Header />
      </header>
      <div className="z-40">
        <HomeHero />
      </div>
      <div className="w-full mx-auto bg-[#FFFFFF]">
        <div
          style={{
            paddingLeft: fluidSize(12, 40),
            paddingRight: fluidSize(12, 40),
          }}
          className="max-w-[1440px] mx-auto bg-[#FFFFFF]"
        >
          <Divider size="normal" />
          <Icons />
          <Divider size="normal" />
          <Introduction />
          <Divider size="large" />
          <Advantages />
          <Divider size="large" />
          <div
            className="text-center"
            style={{ fontSize: fluidSize(28, 56), fontWeight: 700 }}
          >
            HOW IT WORKS
          </div>
          <Divider size="large" />
          <HowItWorks />
          <Divider size="large" />
          <div
            className="text-center leading-none"
            style={{ fontSize: fluidSize(28, 56), fontWeight: 700 }}
          >
            THE ULTIMATE AI-POWERED<br></br> VAPING EXPERIENCE
            <div style={{ height: fluidSize(12, 24) }} />
            <div
              className="text-center leading-none"
              style={{ fontSize: fluidSize(14, 20), fontWeight: 400 }}
            >
              Puffy1 is engineered to harmonize hardware and software,
              seamlessly blending Web3<br></br> technology with your vaping
              experience.
            </div>
          </div>
          <Divider size="large" />
          <Experience />
          <Divider size="large" />
          <Timeline />
          <Divider size="normal" />
        </div>
      </div>
      <footer
        className="w-full z-10 bg-white"
        style={{ padding: fluidSize(16, 24) }}
      >
        <Footer />
      </footer>
    </div>
  );
}

function Divider({ size = "normal" }: { size?: "normal" | "large" }) {
  return (
    <div
      style={{
        height: size == "normal" ? fluidSize(12, 40) : fluidSize(32, 80),
      }}
    />
  );
}
