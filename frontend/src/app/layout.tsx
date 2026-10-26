
import Providers from "./providers";
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BazarYa | Tu bazar en línea",
  description:
      "Dale una segunda vida a lo que ya no usás. Explorá productos y contactá directamente a sus vendedores.",
};

export default function RootLayout({
                                     children,
                                   }: LayoutProps<"/">) {
  return (
      <html
          lang="es"
          className={`${geistSans.variable} ${geistMono.variable}`}
      >
      <body>
      <Providers>{children}</Providers>
      </body>
      </html>
  );
}
