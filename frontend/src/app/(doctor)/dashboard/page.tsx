'use client';

import { useEffect, useState } from 'react';
import { useUserStore } from '@/store/useUserStore';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';

const pendingDiagnoses = [
  { id: 'd1', patientName: 'Ali Mahmoud', image: '🔬', prediction: 'Melanoma', confidence: '89%' }
];

export default function DashboardPage() {
  const { role, userId } = useUserStore();
  const router = useRouter();

  // States للداتا الحقيقية
  const [appointments, setAppointments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // حماية الصفحة
  useEffect(() => {
    if (role !== 'doctor') {
      router.push('/');
    }
  }, [role, router]);

  // جلب المواعيد الحقيقية للدكتور ده
  useEffect(() => {
    const fetchDoctorData = async () => {
      try {
        const res = await fetch('/api/slots', { cache: 'no-store' });
        const allSlots = await res.json();
        
        // بنجيب المواعيد الـ Locked تبع الدكتور ده
        const myAppointments = allSlots.filter(
          (slot: any) => slot.doctorId === userId && slot.status === 'locked'
        );
        
        setAppointments(myAppointments);
      } catch (error) {
        console.error("Error fetching doctor data:", error);
      } finally {
        setLoading(false);
      }
    };

    if (role === 'doctor' && userId) {
      fetchDoctorData();
    }
  }, [role, userId]);

  if (role !== 'doctor') return null;

  // 👇 الدالة الجديدة اللي بتنهي الكشف
  const handleMarkAsDone = async (slotId: string) => {
    try {
      const res = await fetch('/api/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ slotId }),
      });

      if (res.ok) {
        toast.success('Appointment marked as Done! ✅');
        // بنشيل الميعاد من الشاشة فوراً
        setAppointments(prev => prev.filter(apt => apt.id !== slotId));
      } else {
        toast.error('Failed to update status.');
      }
    } catch (error) {
      console.error('Error completing appointment:', error);
      toast.error('Something went wrong!');
    }
  };

  const handleConfirm = () => toast.success('Diagnosis Confirmed! Model retraining triggered.');
  const handleCorrect = () => {
    const correctLabel = prompt('❌ Enter the correct diagnosis label for the model to learn:');
    if (correctLabel) toast.success(`Diagnosis Corrected to "${correctLabel}". Retraining triggered!`);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 mt-8 space-y-8">
      <h1 className="text-3xl font-bold text-gray-800">Doctor Dashboard</h1>

      {/* جدول المواعيد */}
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Today's Real-time Appointments</h2>
        
        {loading ? (
          <div className="p-8 text-center text-gray-500 animate-pulse">Loading appointments...</div>
        ) : appointments.length === 0 ? (
          <div className="p-8 text-center text-gray-500 bg-gray-50 rounded-xl">
            No pending appointments at the moment.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-gray-600 border-b">
                  <th className="p-4">Time</th>
                  <th className="p-4">Patient ID</th>
                  <th className="p-4">Status</th>
                  <th className="p-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.map((apt) => {
                  const aptDate = new Date(apt.date);
                  return (
                    <tr key={apt.id} className="border-b hover:bg-gray-50 transition">
                      <td className="p-4 font-medium text-gray-900">
                        {aptDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td className="p-4 text-gray-700 font-bold">{apt.patientId}</td>
                      <td className="p-4">
                        <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-700">
                          {apt.status}
                        </span>
                      </td>
                      <td className="p-4 flex items-center gap-3">
                        <Link href={`/api/patient/${apt.patientId}/history`} className="text-blue-600 hover:underline text-sm font-medium">
                          History
                        </Link>
                        <span className="text-gray-300">|</span>
                        {/* 👇 الزرار الجديد */}
                        <button 
                          onClick={() => handleMarkAsDone(apt.id)}
                          className="text-emerald-600 hover:text-emerald-700 text-sm font-bold bg-emerald-50 px-3 py-1.5 rounded-lg transition-colors"
                        >
                          ✔️ Mark Done
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* الجزء التاني: مراجعة تشخيصات الـ AI (زي ما هو) */}
      <section className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Pending Diagnoses (CV Model)</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {pendingDiagnoses.map((diag) => (
            <div key={diag.id} className="border p-4 rounded-xl flex gap-4 items-center bg-gray-50">
              <div className="w-16 h-16 bg-white border rounded-lg flex items-center justify-center text-3xl shadow-sm">{diag.image}</div>
              <div className="flex-1">
                <p className="font-bold text-gray-800">{diag.patientName}</p>
                <p className="text-sm text-gray-600">
                  AI Prediction: <span className="font-bold text-red-500">{diag.prediction}</span> ({diag.confidence})
                </p>
                <div className="flex gap-2 mt-3">
                  <button onClick={handleConfirm} className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition">Confirm</button>
                  <button onClick={handleCorrect} className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition">Correct</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}