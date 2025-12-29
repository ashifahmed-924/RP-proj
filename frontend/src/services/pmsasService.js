/**
 * PMSAS Service
 * Handles all Progress Monitoring and Streak Analytics API calls
 */

import api from '../config/api';

const pmsasService = {
  // Log an activity
  logActivity: async (activityData) => {
    const response = await api.post('/pmsas/activity', activityData);
    return response.data;
  },

  // Get current user's streak
  getStreak: async () => {
    const response = await api.get('/pmsas/streak');
    return response.data;
  },

  // Get all available badges
  getAllBadges: async (category = null) => {
    const params = category ? { category } : {};
    const response = await api.get('/pmsas/badges', { params });
    return response.data;
  },

  // Get user's earned badges
  getMyBadges: async () => {
    const response = await api.get('/pmsas/badges/me');
    return response.data;
  },

  // Get leaderboard
  getLeaderboard: async (type = 'streak', limit = 10) => {
    const response = await api.get('/pmsas/leaderboard', {
      params: { type, limit }
    });
    return response.data;
  },

  // Get user's points and level
  getPoints: async () => {
    const response = await api.get('/pmsas/points');
    return response.data;
  },

  // Get user's analytics
  getMyAnalytics: async () => {
    const response = await api.get('/pmsas/analytics/me');
    return response.data;
  },

  // Get progress summary
  getSummary: async () => {
    const response = await api.get('/pmsas/summary');
    return response.data;
  },

  // Teacher: Get dashboard
  getTeacherDashboard: async (classId = null) => {
    const params = classId ? { class_id: classId } : {};
    const response = await api.get('/pmsas/dashboard/teacher', { params });
    return response.data;
  },

  // Teacher: Get at-risk students
  getAtRiskStudents: async () => {
    const response = await api.get('/pmsas/dashboard/at-risk');
    return response.data;
  },
};

export default pmsasService;
