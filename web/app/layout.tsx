import type { Metadata } from "next";
import { Inter, Cinzel, Creepster, Nosifer, MedievalSharp, Metal_Mania, Crimson_Text, Lora, EB_Garamond } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const cinzel = Cinzel({ subsets: ["latin"], variable: "--font-cinzel" });
const creepster = Creepster({ weight: "400", subsets: ["latin"], variable: "--font-creepster" });
const nosifer = Nosifer({ weight: "400", subsets: ["latin"], variable: "--font-nosifer" });
const medievalSharp = MedievalSharp({ weight: "400", subsets: ["latin"], variable: "--font-medievalsharp" });
const metalMania = Metal_Mania({ weight: "400", subsets: ["latin"], variable: "--font-metal-mania" });
const crimsonText = Crimson_Text({ weight: ["400", "600"], subsets: ["latin"], variable: "--font-crimson" });
const lora = Lora({ subsets: ["latin"], variable: "--font-lora" });
const ebGaramond = EB_Garamond({ subsets: ["latin"], variable: "--font-eb-garamond" });

export const metadata: Metadata = {
  title: "CoC Solo · LLM KP",
  description: "Lovecraftian solo adventure with LLM Keeper",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" className={`${inter.variable} ${cinzel.variable} ${creepster.variable} ${nosifer.variable} ${medievalSharp.variable} ${metalMania.variable} ${crimsonText.variable} ${lora.variable} ${ebGaramond.variable}`}>
      <body className="antialiased bg-background text-foreground">{children}</body>
    </html>
  );
}

