'use client';

import { useUserStore } from '@/store/useUserStore';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Navbar() {
  const { role, logout } = useUserStore();
  const router = useRouter();

  if (!role) return null;

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    // 👈 ضفنا sticky top-0 و backdrop-blur عشان تأثير الإزاز الشفاف
    <nav className="sticky top-0 z-50 bg-white/70 backdrop-blur-lg border-b border-slate-200/50 px-6 py-4 flex justify-between items-center transition-all">
      <div className="font-extrabold text-2xl tracking-tight text-teal-700 flex items-center gap-2">
        <Link href='/'>
            <span className="text-3xl drop-shadow-sm">⚕️</span> Smart<span className="text-slate-800">Clinic</span>
        </Link>
      </div>
      
      <div className="flex items-center gap-6">
        {role === 'patient' && (
          <div className="flex gap-6 text-sm font-semibold text-slate-600">
            <Link href="/chat" className="hover:text-teal-600 transition-colors">AI Assistant</Link>
            <Link href="/book" className="hover:text-teal-600 transition-colors">Book Appointment</Link>
            {/* 👈 ده اللينك الجديد بتاع الـ History */}
            <Link href="/history" className="hover:text-teal-600 transition-colors">My Appointments</Link>
          </div>
        )}

        <div className="flex items-center gap-4 border-l border-slate-200 pl-6">
          <span className="text-xs font-bold text-teal-800 bg-teal-50 px-4 py-1.5 rounded-full ring-1 ring-teal-100">
            {role === 'patient' ? '👤 Patient Portal' : '👨‍⚕️ Doctor Dashboard'}
          </span>
          <button 
            onClick={handleLogout} 
            className="text-sm text-slate-500 hover:text-red-600 font-bold transition-colors cursor-pointer"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}