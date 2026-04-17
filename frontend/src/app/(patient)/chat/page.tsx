'use client';

import { useState, useEffect, useRef } from 'react';
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
    {
      role: 'bot',
      content:
        'Hello! I am your AI Clinic Assistant. Please describe your symptoms or ask about doctors, treatments, or patient history.',
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  if (role !== 'patient') {
    return (
      <div className="p-8 text-center">
        Access Denied. Please login as a patient.
      </div>
    );
  }

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMessage = input.trim();

    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.error || 'Failed to get AI response');
      }

      if (Array.isArray(data?.suggestedDoctors)) {
        setSuggestedDoctors(data.suggestedDoctors);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content:
            data?.reply ||
            'Sorry, I could not generate a response right now.',
        },
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          content:
            'Sorry, something went wrong while contacting the assistant.',
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-8 h-[80vh] flex flex-col bg-white rounded-2xl shadow-sm border border-gray-100">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] p-4 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-800 rounded-bl-none'
              }`}
            >
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
        <Link
          href="/book"
          className="text-sm text-blue-600 hover:underline font-medium"
        >
          Go to Booking Page →
        </Link>
      </div>
    </div>
  );
}