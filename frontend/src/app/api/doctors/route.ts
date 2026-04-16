import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

// 👈 السطر ده هو اللي هيحل المشكلة ويمنع الكاش نهائياً
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const doctors = await apiClient.getDoctors();
    
    // مش هنحط delay هنا عشان الدكاترة المفروض تظهر بسرعة
    return NextResponse.json(doctors);
    
  } catch (error) {
    console.error("Error fetching doctors:", error);
    return NextResponse.json({ error: 'Failed to fetch doctors' }, { status: 500 });
  }
}