'use client';

import { useState, useEffect, useRef } from 'react'; // 👈 ضفنا useEffect و useRef
import { useUserStore } from '@/store/useUserStore';
import Link from 'next/link';

interface Message {
  role: 'bot' | 'user';
  content: string;
}

export default function ChatPage() {
  const { role, setSuggestedDoctors } = useUserStore();
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'bot', content: 'Hello! I am your AI Clinic Assistant. Please describe your symptoms or upload an image of your skin condition so I can help you.' }
  ]);

  // 👈 1. عملنا Reference عشان نمسك بيه آخر الشات
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 👈 2. دالة بتعمل سكرول ناعم لحد الـ Reference
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 👈 3. الـ useEffect ده بيشتغل أوتوماتيك كل ما الرسايل تزيد أو الـ AI يبدأ يكتب
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  if (role !== 'patient') return <div className="p-8 text-center">Access Denied. Please login as a patient.</div>;

  const handleSend = () => {
    if (!input.trim()) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      const aiResponse = "Based on your symptoms, I suggest seeing Dr. Ahmed (Dermatology) or Dr. Sara (General). I've updated the booking page for you.";
      
      setSuggestedDoctors(['d1', 'd2']); 
      setMessages((prev) => [...prev, { role: 'bot', content: aiResponse }]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-8 h-[80vh] flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] p-4 rounded-2xl ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-gray-100 text-gray-800 rounded-bl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-500 p-4 rounded-2xl rounded-bl-none animate-pulse">
              AI is typing...
            </div>
          </div>
        )}
        {/* 👈 4. ده العنصر الوهمي اللي دايماً موجود في آخر الشات وبنعمل سكرول ليه */}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t mt-auto flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Describe your symptoms here..."
          className="flex-1 border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          onClick={handleSend}
          disabled={!input.trim() || isTyping}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition disabled:opacity-50 cursor-pointer"
        >
          Send
        </button>
      </div>
      
      <div className="text-center pb-2">
         <Link href="/book" className="text-sm text-blue-600 hover:underline font-medium">
           Go to Booking Page →
         </Link>
      </div>
    </div>
  );
}