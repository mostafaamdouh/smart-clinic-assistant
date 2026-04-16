'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useUserStore } from '@/store/useUserStore';
import Link from 'next/link';
import { Patient } from '@/lib/types';

export default function PatientHistoryPage() {
  const { role } = useUserStore();
  const router = useRouter();
  const params = useParams(); // دي الـ Hook اللي بتجيب الـ ID من الرابط
  const patientId = params.id as string;

  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role !== 'doctor') {
      router.push('/');
      return;
    }

    const fetchHistory = async () => {
      try {
        const res = await fetch(`/api/patient/${patientId}/history`);
        if (res.ok) {
          const data = await res.json();
          setPatient(data);
        }
      } catch (error) {
        console.error('Error fetching history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [role, patientId, router]);

  if (role !== 'doctor') return null;

  return (
    <div className="max-w-3xl mx-auto p-6 mt-8">
      <div className="mb-6">
        <Link href="/dashboard" className="text-blue-600 hover:underline font-medium flex items-center gap-2">
          ← Back to Dashboard
        </Link>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
        {loading ? (
          <div className="animate-pulse text-gray-500">Loading patient records...</div>
        ) : !patient ? (
          <div className="text-red-500 font-medium">Patient records not found.</div>
        ) : (
          <>
            <div className="border-b pb-4 mb-6">
              <h1 className="text-3xl font-bold text-gray-800">{patient.name}</h1>
              <p className="text-gray-500 mt-1">Patient ID: {patient.id}</p>
            </div>

            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">Medical History</h2>
              {patient.history.length === 0 ? (
                <p className="text-gray-500">No medical history recorded.</p>
              ) : (
                <ul className="space-y-3">
                  {patient.history.map((record, idx) => (
                    <li key={idx} className="flex gap-3 items-start bg-gray-50 p-4 rounded-lg border border-gray-100">
                      <span className="text-xl">📄</span>
                      <span className="text-gray-700 font-medium">{record}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}