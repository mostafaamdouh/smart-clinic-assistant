import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { slotId, patientId } = body;

    if (!slotId || !patientId) {
      return NextResponse.json({ error: 'Missing slotId or patientId' }, { status: 400 });
    }

    // الـ Client هو اللي بيتصرف وبيرمي الريكويست في المكان الصح حسب الـ Environment
    const result = await apiClient.reserveSlot(slotId, patientId);

    // تأخير وهمي لزرار الحجز "فقط" في وضع الـ Mock
    if (process.env.NEXT_PUBLIC_API_MODE === 'mock') {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    // لو الـ Client رجع إيرور (مثلاً الميعاد محجوز)
    if (result.error) {
      return NextResponse.json({ error: result.error }, { status: 400 });
    }

    return NextResponse.json(result);

  } catch (error) {
    console.error("Error reserving slot:", error);
    return NextResponse.json({ error: 'Invalid request or Server Error' }, { status: 500 });
  }
}