import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

export async function POST(req: Request) {
  try {
    const { slotId } = await req.json();
    
    if (!slotId) {
      return NextResponse.json({ error: 'Missing slotId' }, { status: 400 });
    }

    const result = await apiClient.completeSlot(slotId);
    return NextResponse.json(result);

  } catch (error) {
    console.error("Error completing slot:", error);
    return NextResponse.json({ error: 'Server Error' }, { status: 500 });
  }
}