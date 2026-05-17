import type { Metadata } from "next";
import "./globals.css";
import { BackgroundWakeup } from "@/components/BackgroundWakeup";

export const metadata: Metadata = {
  title: "ATA - Autonomous Talent Acquisition",
  description: "AI-powered hiring automation system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
          <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <a href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent hover:opacity-80 transition-opacity">
                  ATA
                </a>
                <p className="text-sm text-slate-600">Autonomous Talent Acquisition</p>
              </div>
            </div>
          </header>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
        <BackgroundWakeup />
      </body>
    </html>
  );
}
