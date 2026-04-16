import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

// 👈 السطر ده هو اللي هيحل المشكلة ويمنع الكاش نهائياً
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    // 1. بنسيب الـ apiClient يجيب الداتا سواء من الـ Mock أو الباك إند الحقيقي
    const slots = await apiClient.getSlots();

    // 2. بنعمل التأخير الوهمي (عشان الـ Skeleton يبان) "فقط" لو إحنا في وضع الـ Mock
    if (process.env.NEXT_PUBLIC_API_MODE === 'mock') {
      await new Promise((resolve) => setTimeout(resolve, 1500)); // قللتها لـ 1.5 ثانية عشان 3 ثواني هتبضن اليوزر 😂
    }

    // 3. بنرجع الداتا للفرونت إند
    return NextResponse.json(slots);
    
  } catch (error) {
    console.error("Error fetching slots:", error);
    return NextResponse.json({ error: 'Failed to fetch slots' }, { status: 500 });
  }
}