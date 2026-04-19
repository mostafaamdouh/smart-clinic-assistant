'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';

// تعريف شكل الرسالة عشان الـ TypeScript
interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  imageUrl?: string | null; // 👈 ضفنا مسار الصورة هنا
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  
  // States الخاصة بالصورة
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  // Reference عشان نفتح الـ input المخفي
  const fileInputRef = useRef<HTMLInputElement>(null);

  // دالة اختيار الصورة وعمل Preview
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      // بنعمل رابط مؤقت عشان نعرض الصورة في المتصفح قبل الرفع
      setImagePreview(URL.createObjectURL(file)); 
    }
  };

  // دالة مسح الصورة قبل الإرسال
  const removeImage = () => {
    setSelectedFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = ''; // تصفير الـ input
  };

  // دالة سحرية لتحويل الصورة لـ Base64 عشان الباك إند
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };

  // دالة الإرسال
  const handleSendMessage = async () => {
    if (!inputText.trim() && !selectedFile) return; // لو مفيش نص ولا صورة متبعتش

    let base64Image = null;

    // لو اليوزر مختار صورة، حولها لـ Base64
    if (selectedFile) {
      base64Image = await fileToBase64(selectedFile);
    }

    // 1. إضافة الرسالة للشاشة فوراً (Optimistic UI)
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputText,
      imageUrl: imagePreview, // نعرض الـ Preview للمستخدم
    };
    
    setMessages((prev) => [...prev, newMessage]);
    
    // تصفير الخانات
    setInputText('');
    removeImage();

    // 2. إرسال الداتا للباك إند
    try {
      const res = await fetch('/api/chat', { // مسار الباك إند بتاعك
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: newMessage.text,
          image: base64Image, // 👈 الصورة مبعوتة كنص مشفر
        }),
      });

      const data = await res.json();
      
      // الرد بتاع الـ AI
      setMessages((prev) => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: data.reply,
      }]);
      
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-4 h-[80vh] flex flex-col mt-8">
      {/* 1. منطقة عرض الرسائل */}
      <div className="flex-1 overflow-y-auto bg-slate-50 rounded-2xl p-6 mb-4 border border-slate-100 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] rounded-2xl p-4 ${msg.sender === 'user' ? 'bg-teal-600 text-white rounded-br-none' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'}`}>
              
              {/* عرض الصورة لو موجودة جوه الرسالة */}
              {msg.imageUrl && (
                <div className="mb-3">
                  <img src={msg.imageUrl} alt="Uploaded" className="rounded-xl max-h-64 object-contain" />
                </div>
              )}
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
      </div>

      {/* 2. منطقة الإدخال */}
      <div className="relative bg-white rounded-2xl border border-slate-200 p-2 shadow-sm">
        
        {/* شريط الـ Preview (بيظهر بس لو فيه صورة تم اختيارها) */}
        {imagePreview && (
          <div className="p-3 border-b border-slate-100 flex items-center gap-4">
            <div className="relative w-16 h-16 rounded-lg overflow-hidden border border-slate-200">
              <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
              <button 
                onClick={removeImage}
                className="absolute top-1 right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold"
              >
                ×
              </button>
            </div>
            <span className="text-sm text-slate-500 font-medium">{selectedFile?.name}</span>
          </div>
        )}

        {/* حقل النص والزراير */}
        <div className="flex items-center gap-2 p-2">
          {/* الـ Input المخفي للصورة */}
          <input 
            type="file" 
            accept="image/*" 
            ref={fileInputRef} 
            onChange={handleImageSelect} 
            className="hidden" 
          />
          
          {/* زرار استدعاء الصورة */}
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="p-3 text-slate-400 hover:text-teal-600 hover:bg-teal-50 rounded-xl transition"
            title="Attach an image"
          >
            📷
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Describe your symptoms or ask a question..."
            className="flex-1 bg-transparent outline-none px-2 text-slate-700 placeholder-slate-400"
          />

          <button 
            onClick={handleSendMessage}
            disabled={!inputText.trim() && !selectedFile}
            className="bg-teal-600 hover:bg-teal-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-bold transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}