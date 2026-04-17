import { NextResponse } from 'next/server';
import { apiClient } from '@/lib/apiClient';

export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const message = body?.message?.trim();

    if (!message) {
      return NextResponse.json(
        { error: 'Missing message' },
        { status: 400 }
      );
    }

    const ragResult = await apiClient.retrieveRag(message, 3);

    const context =
      ragResult?.context ||
      'No relevant information found in the knowledge base.';

    const lowered = message.toLowerCase();
    let suggestedDoctors: string[] = [];

    if (
      lowered.includes('skin') ||
      lowered.includes('derma') ||
      lowered.includes('psoriasis') ||
      lowered.includes('eczema') ||
      lowered.includes('rash')
    ) {
      suggestedDoctors = ['sara'];
    } else if (
      lowered.includes('heart') ||
      lowered.includes('cardio') ||
      lowered.includes('blood pressure')
    ) {
      suggestedDoctors = ['ahmed'];
    } else if (
      lowered.includes('general') ||
      lowered.includes('fever') ||
      lowered.includes('cold')
    ) {
      suggestedDoctors = ['omar'];
    }

    return NextResponse.json({
      reply: context,
      suggestedDoctors,
      chunks: ragResult?.chunks || [],
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return NextResponse.json(
      { error: 'Failed to process chat request' },
      { status: 500 }
    );
  }
}