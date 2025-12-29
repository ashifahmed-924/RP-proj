/**
 * Account Service
 * Handles all account-related API calls
 */

import api from '../config/api';

const accountService = {
  // Get all users (admin only)
  getAllUsers: async (params = {}) => {
    const response = await api.get('/accounts/users', { params });
    return response.data;
  },

  // Get user by ID (admin only)
  getUserById: async (userId) => {
    const response = await api.get(`/accounts/users/${userId}`);
    return response.data;
  },

  // Update user role (admin only)
  updateUserRole: async (userId, role) => {
    const response = await api.put(`/accounts/users/${userId}/role`, { role });
    return response.data;
  },

  // Activate user account (admin only)
  activateUser: async (userId) => {
    const response = await api.post(`/accounts/users/${userId}/activate`);
    return response.data;
  },

  // Deactivate user account (admin only)
  deactivateUser: async (userId) => {
    const response = await api.post(`/accounts/users/${userId}/deactivate`);
    return response.data;
  },

  // Delete user account (admin only)
  deleteUser: async (userId) => {
    const response = await api.delete(`/accounts/users/${userId}`);
    return response.data;
  },

  // Deactivate own account
  deactivateOwnAccount: async () => {
    const response = await api.post('/accounts/me/deactivate');
    return response.data;
  },
};

export default accountService;






