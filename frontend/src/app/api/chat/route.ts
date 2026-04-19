import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { message, image } = body;

    // 1. قائمة التخصصات الطبية للفرز العشوائي
    const specialties = [
      'باطنة (Internal Medicine)',
      'قلب وأوعية دموية (Cardiology)',
      'جلدية (Dermatology)',
      'عظام (Orthopedics)',
      'أنف وأذن وحنجرة (ENT)',
      'مخ وأعصاب (Neurology)'
    ];

    // 2. اختيار تخصص عشوائي
    const randomSpecialty = specialties[Math.floor(Math.random() * specialties.length)];

    // 3. بناء الرد الذكي
    let aiReply = `بناءً على كلامك والأعراض اللي وصفتها، التشخيص المبدئي بيشير إنك محتاج تعرض حالتك على دكتور متخصص في الـ **${randomSpecialty}**. `;

    // لو باعت صورة، نطمنه إنها وصلت
    if (image) {
      aiReply += "كمان أنا استلمت الصورة اللي بعتها، وموديل الرؤية الحاسوبية (CV Model) بتاعنا بيحللها دلوقتي وهيبعت التقرير للدكتور مع ملفك. 🔬 ";
    }

    aiReply += "أنا اخترتلك أفضل الدكاترة المناسبين لحالتك في التخصص ده، وتقدر تحجز معاهم الميعاد اللي يناسبك دلوقتي.";

    // 4. تأخير وهمي (ثانية ونص) عشان المريض يحس إن الـ AI بيقرأ وبيحلل بجد
    await new Promise((resolve) => setTimeout(resolve, 1500));

    return NextResponse.json({ reply: aiReply });

  } catch (error) {
    console.error("Chat API Error:", error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}