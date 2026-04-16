'use client';

import { useState, useEffect } from 'react';
import { useUserStore } from '@/store/useUserStore';
import { useRouter } from 'next/navigation';
import { AppointmentSlot } from '@/lib/types';
import toast from 'react-hot-toast';

export default function BookPage() {
  const { role, userId, suggestedDoctorIds } = useUserStore();
  const router = useRouter();
  
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [loading, setLoading] = useState(true);
  const [bookingId, setBookingId] = useState<string | null>(null);
  
  const [selectedDoctor, setSelectedDoctor] = useState<string | null>(null);

  const [doctors, setDoctors] = useState<any[]>([]);
  const [loadingDoctors, setLoadingDoctors] = useState(true);

  // حماية المسار
  useEffect(() => {
    if (role !== 'patient') {
      router.push('/');
    }
  }, [role, router]);

  // جلب الدكاترة من الـ API
  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const res = await fetch('/api/doctors');
        const data = await res.json();
        setDoctors(data);
      } catch (error) {
        console.error("Error fetching doctors:", error);
      } finally {
        setLoadingDoctors(false);
      }
    };
    fetchDoctors();
  }, []);

  // جلب المواعيد من الـ API
  useEffect(() => {
    const fetchSlots = async () => {
      try {
        const res = await fetch('/api/slots');
        const data = await res.json();
        setSlots(data);
      } catch (error) {
        console.error('Error fetching slots:', error);
      } finally {
        setLoading(false);
      }
    };

    if (role === 'patient') {
      fetchSlots();
    }
  }, [role]);

  if (role !== 'patient') return null;

  const handleBook = async (slotId: string) => {
    setBookingId(slotId);
    try {
      const res = await fetch('/api/reserve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slotId, patientId: userId }),
      });

      if (res.ok) {
        toast.success('Appointment booked successfully!');
        setSlots((prev) => 
          prev.map((slot) => 
            slot.id === slotId ? { ...slot, status: 'locked', patientId: userId } : slot
          )
        );
      } else {
        toast.error('Failed to book. Maybe someone else took it?');
      }
    } catch (error) {
      console.error('Booking error:', error);
      toast.error('Something went wrong!');
    } finally {
      setBookingId(null);
    }
  };

  // 👈 التعديل هنا: استخدمنا الـ State اللي اسمها doctors بدل mockDoctors
  const doctorsToShow = doctors.filter(doc => 
    suggestedDoctorIds && suggestedDoctorIds.length > 0 ? suggestedDoctorIds.includes(doc.id) : true
  );

  const availableSlots = slots.filter((slot) => slot.status === 'available');

  return (
    <div className="max-w-4xl mx-auto p-6 mt-8">
      {!selectedDoctor ? (
        <>
          <h1 className="text-3xl font-extrabold text-teal-800 tracking-tight mb-2">Book an Appointment</h1>
          <p className="text-slate-500 mb-6">Choose a specialist to see their available time slots.</p>
          
          {suggestedDoctorIds && suggestedDoctorIds.length > 0 && (
            <div className="mb-6 inline-block bg-teal-50 text-teal-700 px-4 py-2 rounded-lg text-sm font-bold shadow-sm">
              ✨ Recommended by your AI Assistant
            </div>
          )}

          {/* 👈 ضفنا لودينج خفيف للدكاترة عشان لو الـ API اتأخر */}
          {loadingDoctors ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-white border border-slate-100 rounded-2xl animate-pulse"></div>
              ))}
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {doctorsToShow.map(doc => (
                <div 
                  key={doc.id} 
                  onClick={() => {
                    setSelectedDoctor(doc.id);
                    setLoading(true); 
                    setTimeout(() => setLoading(false), 1500); 
                  }}
                  className="p-6 bg-white border border-slate-200 rounded-2xl cursor-pointer hover:border-teal-500 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col items-center text-center group"
                >
                  <div className="text-5xl mb-4 bg-slate-50 w-20 h-20 flex items-center justify-center rounded-full group-hover:scale-110 transition-transform">
                    👨‍⚕️
                  </div>
                  <h3 className="text-xl font-bold text-slate-800">{doc.name}</h3>
                  <p className="text-slate-500 font-medium mb-6">{doc.specialization}</p>
                  <button className="w-full py-2.5 bg-slate-50 group-hover:bg-teal-50 text-teal-600 rounded-lg font-bold transition-colors cursor-pointer">
                    View Slots →
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <>
          <button 
            onClick={() => setSelectedDoctor(null)} 
            className="mb-6 text-sm text-slate-500 hover:text-slate-800 font-bold flex items-center gap-2 cursor-pointer transition-colors"
          >
            ← Back to Doctors
          </button>
          
          <h1 className="text-3xl font-extrabold text-teal-800 tracking-tight mb-2">Available Slots</h1>
          {/* 👈 التعديل هنا: استخدمنا doctors.find */}
          <p className="text-slate-500 mb-8">Select a time that works for you with <b className="text-slate-700">{doctors.find(d => d.id === selectedDoctor)?.name}</b>.</p>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((skeleton) => (
                <div key={skeleton} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 animate-pulse">
                  <div className="h-4 bg-slate-200 rounded w-1/3 mb-3"></div>
                  <div className="h-8 bg-slate-200 rounded w-1/2 mb-8"></div>
                  <div className="h-10 bg-slate-200 rounded-xl w-full"></div>
                </div>
              ))}
            </div>
          ) : availableSlots.filter(slot => slot.doctorId === selectedDoctor).length === 0 ? (
            <div className="bg-white p-12 rounded-3xl shadow-sm border border-slate-100 text-center">
              <div className="text-5xl mb-4">🗓️</div>
              <p className="text-slate-600 font-medium">No available slots for this doctor at the moment.</p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {availableSlots
                .filter(slot => slot.doctorId === selectedDoctor)
                .map((slot) => {
                const slotDate = new Date(slot.date);
                return (
                  <div key={slot.id} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:border-teal-400 hover:shadow-md transition-all">
                    <div className="text-sm text-slate-500 mb-1 font-medium">
                      {slotDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                    </div>
                    <div className="text-2xl font-extrabold text-slate-800 mb-6">
                      {slotDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                    
                    <button
                      onClick={() => handleBook(slot.id)}
                      disabled={bookingId === slot.id}
                      className="w-full py-2.5 px-4 bg-teal-50 text-teal-700 hover:bg-teal-600 hover:text-white rounded-xl font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2 cursor-pointer shadow-sm hover:shadow-teal-200"
                    >
                      {bookingId === slot.id ? 'Booking...' : 'Book This Slot'}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}