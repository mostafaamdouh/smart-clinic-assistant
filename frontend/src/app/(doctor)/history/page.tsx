'use client';

import { useEffect, useState } from 'react';
import { useUserStore } from '@/store/useUserStore';
import Link from 'next/link';

// تعريف الـ Types
interface Slot {
  id: string;
  doctorId: string;
  date: string;
  status: string;
  patientId?: string | null;
}

export default function HistoryPage() {
  const { userId, role } = useUserStore();
  
  // 1. تعريف كل الـ States فوق خالص
  const [mySlots, setMySlots] = useState<Slot[]>([]);
  const [doctorsList, setDoctorsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // 2. جلب الداتا (المواعيد + الدكاترة) مع بعض
  useEffect(() => {
    const fetchMyHistory = async () => {
      try {
        const [slotsRes, doctorsRes] = await Promise.all([
          fetch('/api/slots', { cache: 'no-store' }), // 👈 التعديل هنا
          fetch('/api/doctors', { cache: 'no-store' }) // 👈 والتعديل هنا
        ]);
        
        const allSlots = await slotsRes.json();
        const allDoctors = await doctorsRes.json();
        
        setDoctorsList(allDoctors); // بنحفظ الدكاترة هنا

        // بنفلتر المواعيد بتاعت المريض ده بس
        const bookedByMe = allSlots.filter(
          (slot: any) => slot.patientId  === userId && slot.status === 'locked'
        );
        
        setMySlots(bookedByMe);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchMyHistory();
    }
  }, [userId]);

  // 3. الدالة اللي بتجيب اسم الدكتور من الـ State الجديدة
  const getDoctorName = (docId: string) => {
    const doc = doctorsList.find(d => d.id === docId);
    return doc ? doc.name : 'Unknown Doctor';
  };

  // 4. الحماية (لو مش مريض يطرد)
  if (role !== 'patient') return <div className="p-10 text-center text-slate-500">Access Denied.</div>;

  // 5. الـ UI بتاع الصفحة
  return (
    <div className="max-w-4xl mx-auto p-6 mt-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-extrabold text-teal-800 tracking-tight mb-2">My Appointments</h1>
          <p className="text-slate-500">Manage your upcoming clinic visits.</p>
        </div>
        <Link 
          href="/book" 
          className="bg-teal-50 text-teal-700 hover:bg-teal-600 hover:text-white px-5 py-2.5 rounded-xl font-bold transition-all shadow-sm"
        >
          + Book New
        </Link>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-24 bg-white rounded-2xl border border-slate-100 shadow-sm animate-pulse flex items-center p-6 gap-6">
              <div className="h-12 w-12 bg-slate-200 rounded-full"></div>
              <div className="flex-1 space-y-3">
                <div className="h-4 bg-slate-200 rounded w-1/4"></div>
                <div className="h-3 bg-slate-200 rounded w-1/3"></div>
              </div>
            </div>
          ))}
        </div>
      ) : mySlots.length === 0 ? (
        <div className="bg-white p-12 rounded-3xl shadow-sm border border-slate-100 text-center">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-bold text-slate-700 mb-2">No upcoming appointments</h3>
          <p className="text-slate-500 mb-6">You haven't booked any visits with our doctors yet.</p>
          <Link href="/book" className="text-teal-600 font-bold hover:underline">
            Go to booking page →
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {mySlots.map((slot) => {
            const slotDate = new Date(slot.date);
            return (
              <div key={slot.id} className="bg-white p-6 rounded-2xl shadow-sm hover:shadow-md border border-slate-100 transition-all flex items-center justify-between group">
                <div className="flex items-center gap-5">
                  <div className="bg-teal-50 text-teal-600 h-14 w-14 rounded-full flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                    👨‍⚕️
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-800">{getDoctorName(slot.doctorId)}</h3>
                    <p className="text-sm text-slate-500 font-medium">
                      {slotDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-2xl font-extrabold text-teal-700">
                    {slotDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <span className="inline-block mt-1 px-3 py-1 bg-green-50 text-green-700 text-xs font-bold rounded-full">
                    Confirmed
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}