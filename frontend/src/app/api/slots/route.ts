import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const slots = await apiClient.getSlots();

    if (process.env.NEXT_PUBLIC_API_MODE === 'mock') {
      await new Promise((resolve) => setTimeout(resolve, 800));
    }

    return NextResponse.json(slots);
  } catch (error) {
    console.error('Error fetching slots:', error);
    return NextResponse.json(
      { error: 'Failed to fetch slots' },
      { status: 500 }
    );
  }
}