import type { Metadata } from "next";
import "./globals.css";
import { Inter, Libre_Barcode_128, Lexend } from "next/font/google";
import { Providers } from "./Providers";

export const metadata: Metadata = {
  title: "Puffy",
  description: "Puffy",
};
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
});

const libreBarcode = Libre_Barcode_128({
  subsets: ["latin"],
  variable: "--font-libre-barcode",
  weight: ["400"],
  display: "swap",
});

const lexend = Lexend({
  subsets: ["latin"],
  variable: "--font-lexend",
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${libreBarcode.variable} ${lexend.variable} font-inter flex flex-col items-center text-black relative`}
      >
        {" "}
        <Providers>
          <div className="w-full flex flex-col justify-start">
            {/* <main className="w-full z-0 min-h-screen flex justify-center items-start bg-white"> */}
            <main className="w-full flex flex-col z-0 flex-1">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
