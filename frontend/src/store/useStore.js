import { create } from 'zustand';

const useStore = create((set) => ({
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

  // UI State
  sidebarCollapsed: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),

  // Loading states
  loading: {},
  setLoading: (key, value) => set((s) => ({
    loading: { ...s.loading, [key]: value }
  })),

  // Notifications
  notifications: [],
  addNotification: (msg, type = 'info') => set((s) => ({
    notifications: [...s.notifications, { id: Date.now(), msg, type }]
  })),
  removeNotification: (id) => set((s) => ({
    notifications: s.notifications.filter((n) => n.id !== id)
  })),
}));

export default useStore;
