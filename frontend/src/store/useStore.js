import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
  persist(
    (set) => ({
      // Profile
      profile: null,
      setProfile: (profile) => set({ profile }),

      // Jobs 
      jobs: [],
      totalJobs: 0,
      setJobs: (jobs, total) => set({ jobs, totalJobs: total }),

      // Tracker
      tracker: { summary: {}, applications: [] },
      setTracker: (tracker) => set({ tracker }),

      // UI State (not persisted — excluded below)
      sidebarCollapsed: false,
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

      // Loading states (not persisted)
      loading: {},
      setLoading: (key, value) => set((s) => ({
        loading: { ...s.loading, [key]: value }
      })),

      // Notifications (not persisted)
      notifications: [],
      addNotification: (msg, type = 'info') => set((s) => ({
        notifications: [...s.notifications, { id: Date.now(), msg, type }]
      })),
      removeNotification: (id) => set((s) => ({
        notifications: s.notifications.filter((n) => n.id !== id)
      })),
    }),
    {
      name: 'job-copilot-store',
      // Only persist profile, jobs, totalJobs, tracker — skip transient UI state
      partialize: (state) => ({
        profile: state.profile,
        jobs: state.jobs,
        totalJobs: state.totalJobs,
        tracker: state.tracker,
      }),
    }
  )
);

export default useStore;
