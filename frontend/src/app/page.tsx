'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUserStore } from '@/store/useUserStore';
import toast from 'react-hot-toast';

export default function HomePage() {
  const router = useRouter();
  const { login } = useUserStore();

  // State للتحكم في الـ Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRole, setSelectedRole] = useState<'patient' | 'doctor' | null>(null);
  
  // State للفورم نفسه
  const [isLoginMode, setIsLoginMode] = useState(true); // عشان نبدل بين Login و Sign up
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // دالة فتح الـ Modal
  const handleOpenModal = (role: 'patient' | 'doctor') => {
    setSelectedRole(role);
    setIsModalOpen(true);
  };

  // دالة قفل الـ Modal
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedRole(null);
    setEmail('');
    setPassword('');
  };

  // دالة محاكاة تسجيل الدخول
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); // عشان الصفحة متعملش Refresh
    
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsLoading(true);

    // بنعمل تأخير وهمي كأننا بنكلم الباك إند
    setTimeout(() => {
      setIsLoading(false);
      
      if (isLoginMode) {
        toast.success('Logged in successfully!');
      } else {
        toast.success('Account created successfully!');
      }

      // بنسجل الدخول في الـ Zustand Store باليوزرات الوهمية بتاعتنا
      if (selectedRole === 'patient') {
        login('patient', 'p1'); // Ali Mahmoud
        router.push('/chat');
      } else if (selectedRole === 'doctor') {
        login('doctor', 'd1'); // Dr. Ahmed
        router.push('/dashboard');
      }
    }, 1500);
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center relative px-4">
      {/* ----------------- الشاشة الأساسية ----------------- */}
      <div className="bg-white/60 backdrop-blur-xl p-10 rounded-3xl shadow-xl border border-slate-200/50 max-w-lg w-full text-center relative z-10">
        <div className="text-6xl mb-6">🏥</div>
        <h1 className="text-4xl font-extrabold text-teal-800 mb-3 tracking-tight">Smart Clinic</h1>
        <p className="text-slate-500 mb-10 text-lg">Your AI-powered healthcare companion. Choose your role to get started.</p>

        <div className="flex flex-col gap-4">
          <button
            onClick={() => handleOpenModal('patient')}
            className="w-full py-4 px-6 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-lg shadow-md shadow-teal-200 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 cursor-pointer"
          >
            👤 I am a Patient
          </button>
          
          <button
            onClick={() => handleOpenModal('doctor')}
            className="w-full py-4 px-6 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold text-lg shadow-md shadow-slate-200 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 cursor-pointer"
          >
            👨‍⚕️ I am a Doctor
          </button>
        </div>
      </div>

      {/* ----------------- الـ Popup (Modal) ----------------- */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* الخلفية الشفافة اللي بتعمل Blur */}
          <div 
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
            onClick={handleCloseModal}
          ></div>

          {/* الفورم نفسه */}
          <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl relative z-10 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="p-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-slate-800">
                  {selectedRole === 'patient' ? 'Patient Portal' : 'Doctor Access'}
                </h2>
                <button 
                  onClick={handleCloseModal}
                  className="text-slate-400 hover:text-slate-600 text-2xl font-bold cursor-pointer"
                >
                  &times;
                </button>
              </div>

              <p className="text-slate-500 mb-6">
                {isLoginMode ? 'Welcome back! Please enter your details.' : 'Create a new account to get started.'}
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Email Address</label>
                  <input 
                    type="email" 
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="doctor@clinic.com"
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Password</label>
                  <input 
                    type="password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all"
                    required
                  />
                </div>

                <button 
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 mt-4 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold shadow-md shadow-teal-200 transition-all cursor-pointer disabled:opacity-70 flex items-center justify-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                      Authenticating...
                    </>
                  ) : (
                    isLoginMode ? 'Sign In' : 'Create Account'
                  )}
                </button>
              </form>

              <div className="mt-6 text-center text-sm text-slate-500">
                {isLoginMode ? "Don't have an account? " : "Already have an account? "}
                <button 
                  onClick={() => setIsLoginMode(!isLoginMode)}
                  className="text-teal-600 font-bold hover:underline cursor-pointer"
                >
                  {isLoginMode ? 'Sign Up' : 'Log In'}
                </button>
              </div>
            </div>
            
            {/* شريط تحذيري تحت بيعرف اليوزر إن دي نسخة Demo */}
            <div className="bg-slate-50 border-t border-slate-100 p-4 text-center text-xs text-slate-400">
              This is a demo environment. Any email/password combination will work.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}