/**
 * Teacher Upload Page Component
 * Allows teachers to upload textbook and teacher guide PDFs for content extraction
 */

import { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Description as DescriptionIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import Layout from '../layout/Layout';
import eceseService from '../../services/eceseService';

const steps = ['Upload Files', 'Processing', 'Extract Structure', 'Complete'];

const TeacherUploadPage = () => {
  const { isTeacher, isAdmin } = useAuth();
  const [moduleName, setModuleName] = useState('');
  const [textbookFile, setTextbookFile] = useState(null);
  const [teacherGuideFile, setTeacherGuideFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState('');
  const [activeStep, setActiveStep] = useState(0);
  const [uploadId, setUploadId] = useState(null);
  const [skeleton, setSkeleton] = useState(null);

  // Check if user is teacher or admin
  if (!isTeacher && !isAdmin) {
    return (
      <Layout>
        <Container maxWidth="md" sx={{ mt: 4 }}>
          <Alert severity="error">
            Access Denied. This page is only available for teachers and administrators.
          </Alert>
        </Container>
      </Layout>
    );
  }

  const handleTextbookChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Textbook must be a PDF file');
        return;
      }
      setTextbookFile(file);
      setError('');
    }
  };

  const handleTeacherGuideChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Teacher guide must be a PDF file');
        return;
      }
      setTeacherGuideFile(file);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!moduleName.trim()) {
      setError('Module name is required');
      return;
    }
    if (!textbookFile) {
      setError('Please select a textbook PDF');
      return;
    }
    if (!teacherGuideFile) {
      setError('Please select a teacher guide PDF');
      return;
    }

    setUploading(true);
    setError('');
    setActiveStep(1);

    try {
      const response = await eceseService.uploadModule(
        textbookFile,
        teacherGuideFile,
        moduleName.trim()
      );

      if (response.success) {
        setUploadId(response.upload_id);
        setUploadStatus({
          success: true,
          message: response.message,
          uploadId: response.upload_id,
          moduleName: response.module_name,
          textbookFilename: response.textbook_filename,
          teacherGuideFilename: response.teacher_guide_filename,
        });
        setActiveStep(2);
        
        // Automatically extract skeleton
        await extractSkeleton(response.upload_id);
      } else {
        throw new Error(response.message || 'Upload failed');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload files');
      setActiveStep(0);
      setUploading(false);
    }
  };

  const extractSkeleton = async (id) => {
    try {
      setActiveStep(2);
      const response = await eceseService.extractSkeleton(id);
      
      if (response.success && response.skeleton) {
        setSkeleton(response.skeleton);
        setActiveStep(3);
        setUploading(false);
      } else {
        throw new Error('Failed to extract skeleton');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to extract skeleton');
      setActiveStep(1);
      setUploading(false);
    }
  };

  const handleReset = () => {
    setModuleName('');
    setTextbookFile(null);
    setTeacherGuideFile(null);
    setUploadStatus(null);
    setError('');
    setActiveStep(0);
    setUploadId(null);
    setSkeleton(null);
    setUploading(false);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Upload Module Content
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Upload textbook and teacher guide PDFs to extract and structure educational content.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {activeStep === 0 && (
            <Box>
              <TextField
                fullWidth
                label="Module Name"
                value={moduleName}
                onChange={(e) => setModuleName(e.target.value)}
                placeholder="e.g., History Grade 10, Mathematics"
                sx={{ mb: 3 }}
                required
              />

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Textbook PDF
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  sx={{ mb: 1 }}
                  fullWidth
                >
                  {textbookFile ? textbookFile.name : 'Select Textbook PDF'}
                  <input
                    type="file"
                    hidden
                    accept="application/pdf"
                    onChange={handleTextbookChange}
                  />
                </Button>
                {textbookFile && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <DescriptionIcon color="primary" />
                    <Typography variant="body2" color="text.secondary">
                      {textbookFile.name} ({formatFileSize(textbookFile.size)})
                    </Typography>
                  </Box>
                )}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Teacher Guide PDF
                </Typography>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUploadIcon />}
                  sx={{ mb: 1 }}
                  fullWidth
                >
                  {teacherGuideFile ? teacherGuideFile.name : 'Select Teacher Guide PDF'}
                  <input
                    type="file"
                    hidden
                    accept="application/pdf"
                    onChange={handleTeacherGuideChange}
                  />
                </Button>
                {teacherGuideFile && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                    <DescriptionIcon color="primary" />
                    <Typography variant="body2" color="text.secondary">
                      {teacherGuideFile.name} ({formatFileSize(teacherGuideFile.size)})
                    </Typography>
                  </Box>
                )}
              </Box>

              <Button
                variant="contained"
                size="large"
                onClick={handleUpload}
                disabled={!moduleName || !textbookFile || !teacherGuideFile}
                fullWidth
                sx={{ py: 1.5 }}
              >
                Upload and Process
              </Button>
            </Box>
          )}

          {activeStep >= 1 && uploading && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CircularProgress size={60} sx={{ mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                {activeStep === 1 && 'Uploading files...'}
                {activeStep === 2 && 'Extracting curriculum structure...'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please wait while we process your files
              </Typography>
            </Box>
          )}

          {uploadStatus && activeStep >= 2 && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Upload Successful!
                </Typography>
                <Typography variant="body2">
                  {uploadStatus.message}
                </Typography>
              </Alert>

              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Upload Details
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Upload ID
                      </Typography>
                      <Chip label={uploadStatus.uploadId} size="small" />
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Module Name
                      </Typography>
                      <Typography variant="body1">{uploadStatus.moduleName}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Textbook
                      </Typography>
                      <Typography variant="body1">{uploadStatus.textbookFilename}</Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Teacher Guide
                      </Typography>
                      <Typography variant="body1">{uploadStatus.teacherGuideFilename}</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          )}

          {skeleton && activeStep === 3 && (
            <Box>
              <Alert severity="success" sx={{ mb: 3 }} icon={<CheckCircleIcon />}>
                <Typography variant="subtitle2" gutterBottom>
                  Structure Extracted Successfully!
                </Typography>
                <Typography variant="body2">
                  The curriculum skeleton has been extracted from the teacher guide.
                </Typography>
              </Alert>

              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Extracted Curriculum Structure
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    {Object.entries(skeleton).map(([unit, lessons]) => (
                      <Box key={unit} sx={{ mb: 2 }}>
                        <Typography variant="subtitle1" color="primary" gutterBottom>
                          {unit}
                        </Typography>
                        <Box sx={{ pl: 2 }}>
                          {Array.isArray(lessons) ? (
                            lessons.map((lesson, idx) => (
                              <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                                • {lesson}
                              </Typography>
                            ))
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              {JSON.stringify(lessons)}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>

              <Button
                variant="contained"
                onClick={handleReset}
                sx={{ mt: 3 }}
                fullWidth
              >
                Upload Another Module
              </Button>
            </Box>
          )}
        </Paper>
      </Container>
    </Layout>
  );
};

export default TeacherUploadPage;


