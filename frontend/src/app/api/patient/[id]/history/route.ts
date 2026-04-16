import { NextResponse } from 'next/server';
import { mockPatients } from '@/lib/mockDb';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> } // 👈 التعديل الأول: عرفناها كـ Promise
) {
  // 👈 التعديل التاني: عملنا await عشان نفك الـ Promise وناخد الـ id
    const resolvedParams = await params;
    const patientId = resolvedParams.id;
  // بنجيب الـ ID من الـ URL ونضور على المريض في الداتا الوهمية
  const patient = mockPatients.find((p) => p.id === patientId);

  if (!patient) {
    return NextResponse.json({ error: 'Patient not found' }, { status: 404 });
  }

  return NextResponse.json(patient);
}