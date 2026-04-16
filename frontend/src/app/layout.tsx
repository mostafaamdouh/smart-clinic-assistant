import type { Metadata } from "next";
import { Outfit } from "next/font/google"; // 👈 استدعينا فونت Outfit
import "./global.css";
import Navbar from "@/components/Navbar";
import { Toaster } from "react-hot-toast";

// 👈 طبقنا الفونت
const outfit = Outfit({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Smart Clinic Assistant",
  description: "Advanced Medical AI Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/* 👈 ضفنا خلفية متدرجة من الأبيض للرمادي المزرق الفاتح جداً، وخلينا لون النص الأساسي Slate */}
      <body className={`${outfit.className} bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-white via-slate-50 to-slate-100 text-slate-800 min-h-screen flex flex-col antialiased selection:bg-teal-200 selection:text-teal-900`}>
        <Navbar />
        <main className="flex-1 w-full relative">
          {children}
        </main>
        <Toaster 
          position="top-center" 
          toastOptions={{
            style: {
              borderRadius: '12px',
              background: '#334155',
              color: '#fff',
            },
          }} 
        /> 
      </body>
    </html>
  );
}