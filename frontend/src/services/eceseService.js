/**
 * ECESE Service
 * Education Content Extraction and Structuring Engine API calls
 */

import axios from 'axios';

const ECESE_API_URL = import.meta.env.VITE_ECESE_API_URL || 'http://localhost:5001/ecese';

// Create axios instance for ECESE
const eceseApi = axios.create({
  baseURL: ECESE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
eceseApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add user info to query params for role-based access
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  if (user.id) {
    config.params = {
      ...config.params,
      user_id: user.id,
      user_role: user.role
    };
  }
  
  return config;
});

const eceseService = {
  // ==================== Upload ====================
  
  uploadModule: async (textbookFile, teacherGuideFile, moduleName) => {
    const formData = new FormData();
    formData.append('textbook', textbookFile);
    formData.append('teacher_guide', teacherGuideFile);
    formData.append('module_name', moduleName);
    
    const response = await eceseApi.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getUploadStatus: async (uploadId) => {
    const response = await eceseApi.get(`/upload/${uploadId}`);
    return response.data;
  },

  extractSkeleton: async (uploadId) => {
    const response = await eceseApi.post(`/extract-skeleton/${uploadId}`);
    return response.data;
  },

  // ==================== Subjects ====================
  
  createSubject: async (subjectData) => {
    const response = await eceseApi.post('/subjects', subjectData);
    return response.data;
  },

  listSubjects: async () => {
    const response = await eceseApi.get('/subjects');
    return response.data;
  },

  // ==================== Courses ====================
  
  createCourse: async (courseData) => {
    const response = await eceseApi.post('/courses', courseData);
    return response.data;
  },

  listCourses: async (subjectId = null) => {
    const params = subjectId ? { subject_id: subjectId } : {};
    const response = await eceseApi.get('/courses', { params });
    return response.data;
  },

  // ==================== Documents ====================
  
  uploadDocument: async (file, courseId, documentType) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    const response = await eceseApi.post('/documents/upload', formData, {
      params: {
        course_id: courseId,
        document_type: documentType,
        user_id: user.id,
        user_role: user.role
      },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  listDocuments: async (courseId = null, documentType = null) => {
    const params = {};
    if (courseId) params.course_id = courseId;
    if (documentType) params.document_type = documentType;
    
    const response = await eceseApi.get('/documents', { params });
    return response.data;
  },

  // ==================== Extraction ====================
  
  triggerExtraction: async (courseId, textbookId, teacherGuideId) => {
    const response = await eceseApi.post('/extract', {
      course_id: courseId,
      textbook_document_id: textbookId,
      teacher_guide_document_id: teacherGuideId
    });
    return response.data;
  },

  // ==================== Review ====================
  
  getPendingContent: async (courseId = null) => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await eceseApi.get('/review/pending', { params });
    return response.data;
  },

  getContentForReview: async (contentId) => {
    const response = await eceseApi.get(`/review/${contentId}`);
    return response.data;
  },

  approveContent: async (contentId, notes = null) => {
    const response = await eceseApi.post(`/review/${contentId}/approve`, { notes });
    return response.data;
  },

  rejectContent: async (contentId, reason) => {
    const response = await eceseApi.post(`/review/${contentId}/reject`, { reason });
    return response.data;
  },

  editContent: async (contentId, edits) => {
    const response = await eceseApi.put(`/review/${contentId}/edit`, edits);
    return response.data;
  },

  // ==================== Student Content ====================
  
  getApprovedContent: async (courseId, topic = null) => {
    const params = { course_id: courseId };
    if (topic) params.topic = topic;
    
    const response = await eceseApi.get('/content/approved', { params });
    return response.data;
  },

  getModuleContent: async (moduleName) => {
    // Note: This uses the modules router, not ecese router
    const MODULES_API_URL = import.meta.env.VITE_ECESE_API_URL || 'http://localhost:5001';
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
    const response = await axios.get(`${MODULES_API_URL}/modules/${encodeURIComponent(moduleName)}/content`, {
      headers,
    });
    return response.data;
  },

  // ==================== Analytics ====================
  
  getScopeAccuracyReport: async (courseId) => {
    const response = await eceseApi.get('/analytics/scope-accuracy', {
      params: { course_id: courseId }
    });
    return response.data;
  },

  getSystemHealth: async () => {
    const response = await eceseApi.get('/analytics/system-health');
    return response.data;
  },

  getReviewStats: async (courseId = null) => {
    const params = courseId ? { course_id: courseId } : {};
    const response = await eceseApi.get('/analytics/review-stats', { params });
    return response.data;
  },
};

export default eceseService;

