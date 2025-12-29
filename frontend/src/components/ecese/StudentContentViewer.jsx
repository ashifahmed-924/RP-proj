/**
 * Student Content Viewer Component
 * Displays structured content in a tree view (Module -> Unit -> Topic)
 * with Markdown rendering in the right pane
 */

import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  Divider,
  Chip,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  SimpleTreeView,
  TreeItem,
} from '@mui/x-tree-view';
import {
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
} from '@mui/icons-material';
import {
  MenuBook as MenuBookIcon,
  Folder as FolderIcon,
  Article as ArticleIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuth } from '../../context/AuthContext';
import Layout from '../layout/Layout';
import eceseService from '../../services/eceseService';

const StudentContentViewer = () => {
  const { moduleName } = useParams();
  const navigate = useNavigate();
  const { isStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [content, setContent] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [expanded, setExpanded] = useState([]);
  const [selected, setSelected] = useState('');

  useEffect(() => {
    if (moduleName) {
      loadContent();
    }
  }, [moduleName]);

  const loadContent = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await eceseService.getModuleContent(moduleName);
      if (response.success) {
        setContent(response);
        // Auto-expand all units
        const units = new Set(response.contents.map(c => c.unit_name));
        setExpanded([...units]);
        // Select first topic if available
        if (response.contents.length > 0) {
          const firstTopic = response.contents[0];
          setSelectedTopic(firstTopic);
          setSelected(firstTopic.id);
        }
      } else {
        setError('Failed to load content');
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load module content');
    } finally {
      setLoading(false);
    }
  };

  // Organize content into tree structure: Module -> Unit -> Topic
  const treeStructure = useMemo(() => {
    if (!content || !content.contents) return null;

    const structure = {
      moduleName: content.module_name,
      units: {},
    };

    content.contents.forEach((item) => {
      const unitName = item.unit_name || 'General';
      const topicName = item.topic_name;

      if (!structure.units[unitName]) {
        structure.units[unitName] = [];
      }

      structure.units[unitName].push({
        id: item.id,
        topicName,
        markdown: item.structured_markdown,
        metadata: {
          status: item.status,
          created_at: item.created_at,
          wordCount: item.metadata?.word_count || 0,
        },
      });
    });

    return structure;
  }, [content]);

  const handleTopicSelect = (topicId, topicData) => {
    setSelected(topicId);
    setSelectedTopic(topicData);
  };

  const handleToggle = (event, nodeIds) => {
    setExpanded(nodeIds);
  };

  if (!isStudent) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error">
            Access Denied. This page is only available for students.
          </Alert>
        </Container>
      </Layout>
    );
  }

  if (loading) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ mt: 4, textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Loading content...
          </Typography>
        </Container>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Container>
      </Layout>
    );
  }

  if (!content || !treeStructure) {
    return (
      <Layout>
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Alert severity="info">
            No content available for this module.
          </Alert>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Breadcrumbs sx={{ mb: 1 }}>
            <Link
              color="inherit"
              href="#"
              onClick={(e) => {
                e.preventDefault();
                navigate('/dashboard');
              }}
              sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
            >
              Dashboard
            </Link>
            <Typography color="text.primary">{treeStructure.moduleName}</Typography>
          </Breadcrumbs>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <MenuBookIcon color="primary" sx={{ fontSize: 32 }} />
            <Box>
              <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
                {treeStructure.moduleName}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {content.count} topic{content.count !== 1 ? 's' : ''} available
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Main Content Area - Split View */}
        <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 250px)', minHeight: 600 }}>
          {/* Left Pane - Tree View */}
          <Paper
            elevation={2}
            sx={{
              width: 350,
              minWidth: 300,
              p: 2,
              overflow: 'auto',
              borderRight: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FolderIcon color="primary" />
              Curriculum Structure
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <SimpleTreeView
              expandedItems={expanded}
              selectedItems={selected}
              onExpandedItemsChange={(event, nodeIds) => setExpanded(nodeIds)}
              onSelectedItemsChange={(event, nodeIds) => {
                const nodeId = Array.isArray(nodeIds) ? nodeIds[0] : nodeIds;
                if (nodeId && nodeId !== selected) {
                  // Find the topic data for this nodeId
                  for (const [unitName, topics] of Object.entries(treeStructure.units)) {
                    const topic = topics.find(t => t.id === nodeId);
                    if (topic) {
                      handleTopicSelect(nodeId, topic);
                      break;
                    }
                  }
                }
              }}
              sx={{ flexGrow: 1, overflowY: 'auto' }}
            >
              {Object.entries(treeStructure.units).map(([unitName, topics]) => (
                <TreeItem
                  key={unitName}
                  nodeId={unitName}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: 0.5 }}>
                      <FolderIcon sx={{ fontSize: 18, color: 'primary.main' }} />
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {unitName}
                      </Typography>
                      <Chip
                        label={topics.length}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                  }
                >
                  {topics.map((topic) => (
                    <TreeItem
                      key={topic.id}
                      nodeId={topic.id}
                      label={
                        <Box
                          sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            py: 0.5,
                            cursor: 'pointer',
                            '&:hover': {
                              backgroundColor: 'action.hover',
                              borderRadius: 1,
                            },
                          }}
                        >
                          <ArticleIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                          <Typography variant="body2" sx={{ flex: 1 }}>
                            {topic.topicName}
                          </Typography>
                        </Box>
                      }
                    />
                  ))}
                </TreeItem>
              ))}
            </SimpleTreeView>
          </Paper>

          {/* Right Pane - Markdown Content */}
          <Paper
            elevation={2}
            sx={{
              flex: 1,
              p: 4,
              overflow: 'auto',
              backgroundColor: 'background.default',
            }}
          >
            {selectedTopic ? (
              <Box>
                {/* Topic Header */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
                    {selectedTopic.topicName}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                    <Chip
                      label={selectedTopic.metadata.status}
                      size="small"
                      color="success"
                    />
                    {selectedTopic.metadata.wordCount > 0 && (
                      <Chip
                        label={`${selectedTopic.metadata.wordCount} words`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  <Divider />
                </Box>

                {/* Markdown Content */}
                <Box
                  sx={{
                    '& h1, & h2, & h3, & h4, & h5, & h6': {
                      mt: 3,
                      mb: 2,
                      fontWeight: 600,
                      color: 'text.primary',
                    },
                    '& h1': { fontSize: '2rem', borderBottom: '2px solid', borderColor: 'divider', pb: 1 },
                    '& h2': { fontSize: '1.75rem' },
                    '& h3': { fontSize: '1.5rem' },
                    '& p': {
                      mb: 2,
                      lineHeight: 1.8,
                      color: 'text.primary',
                    },
                    '& ul, & ol': {
                      mb: 2,
                      pl: 3,
                    },
                    '& li': {
                      mb: 1,
                      lineHeight: 1.8,
                    },
                    '& code': {
                      backgroundColor: 'action.selected',
                      padding: '2px 6px',
                      borderRadius: 1,
                      fontFamily: 'monospace',
                      fontSize: '0.9em',
                    },
                    '& pre': {
                      backgroundColor: 'action.selected',
                      padding: 2,
                      borderRadius: 2,
                      overflow: 'auto',
                      mb: 2,
                      '& code': {
                        backgroundColor: 'transparent',
                        padding: 0,
                      },
                    },
                    '& blockquote': {
                      borderLeft: '4px solid',
                      borderColor: 'primary.main',
                      pl: 2,
                      ml: 0,
                      fontStyle: 'italic',
                      color: 'text.secondary',
                      mb: 2,
                    },
                    '& table': {
                      width: '100%',
                      borderCollapse: 'collapse',
                      mb: 2,
                    },
                    '& th, & td': {
                      border: '1px solid',
                      borderColor: 'divider',
                      padding: 1,
                      textAlign: 'left',
                    },
                    '& th': {
                      backgroundColor: 'action.selected',
                      fontWeight: 600,
                    },
                    '& a': {
                      color: 'primary.main',
                      textDecoration: 'none',
                      '&:hover': {
                        textDecoration: 'underline',
                      },
                    },
                  }}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {selectedTopic.markdown}
                  </ReactMarkdown>
                </Box>
              </Box>
            ) : (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  color: 'text.secondary',
                }}
              >
                <ArticleIcon sx={{ fontSize: 64, mb: 2, opacity: 0.5 }} />
                <Typography variant="h6" gutterBottom>
                  Select a topic to view content
                </Typography>
                <Typography variant="body2">
                  Choose a topic from the curriculum structure on the left
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      </Container>
    </Layout>
  );
};

export default StudentContentViewer;

