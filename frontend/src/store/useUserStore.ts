import { create } from 'zustand';
import { UserRole } from '@/lib/types';

interface UserState {
  role: UserRole | null;
  userId: string | null; // عشان نعرف مين اللي عامل لوجين (مثلا 'p1' للمريض، 'd1' للدكتور)
  login: (role: UserRole, userId: string) => void;
  logout: () => void;
  suggestedDoctorIds: string[]; // لستة الـ IDs بتاعة الدكاترة المقترحين
  setSuggestedDoctors: (ids: string[]) => void;
  clearSuggestions: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  role: null,
  userId: null,
  login: (role, userId) => set({ role, userId }),
  logout: () => set({ role: null, userId: null }),
  suggestedDoctorIds: [],
  setSuggestedDoctors: (ids) => set({ suggestedDoctorIds: ids }),
  clearSuggestions: () => set({ suggestedDoctorIds: [] }),
}));