import React from 'react';
import { Box, CircularProgress, InputAdornment, TextField, Typography } from '@mui/material';
import {
  ChevronRight,
  Description,
  ExpandMore,
  FolderOpen,
  FolderOutlined,
  Search
} from '@mui/icons-material';
import { WorkspaceEntry } from '../types/sovereign';

interface WorkspaceTreeProps {
  rootName: string;
  rootPath: string;
  directoryEntries: Record<string, WorkspaceEntry[]>;
  expandedDirectories: Record<string, boolean>;
  loadingDirectories: Record<string, boolean>;
  searchResults: WorkspaceEntry[];
  selectedFilePath: string;
  filter: string;
  onFilterChange: (value: string) => void;
  onToggleDirectory: (directoryPath: string) => void;
  onSelectFile: (filePath: string) => void;
}

const splitPath = (value: string) => value.split(/[\\/]+/).filter(Boolean);

const toDisplayPath = (rootPath: string, targetPath: string) => {
  const normalizedRoot = rootPath.replace(/[\\/]+$/, '');
  const normalizedTarget = targetPath.replace(/[\\/]+$/, '');

  if (normalizedTarget.toLowerCase().startsWith(normalizedRoot.toLowerCase())) {
    const relative = normalizedTarget.slice(normalizedRoot.length).replace(/^[\\/]+/, '');
    return relative || splitPath(normalizedRoot).slice(-1)[0] || normalizedRoot;
  }

  return targetPath;
};

const WorkspaceTree: React.FC<WorkspaceTreeProps> = ({
  rootName,
  rootPath,
  directoryEntries,
  expandedDirectories,
  loadingDirectories,
  searchResults,
  selectedFilePath,
  filter,
  onFilterChange,
  onToggleDirectory,
  onSelectFile
}) => {
  const normalizedFilter = filter.trim().toLowerCase();

  const subtreeMatches = (directoryPath: string): boolean => {
    if (!normalizedFilter) {
      return true;
    }

    const children = directoryEntries[directoryPath] ?? [];
    return children.some((entry) => {
      const nameMatch =
        entry.name.toLowerCase().includes(normalizedFilter) ||
        toDisplayPath(rootPath, entry.path).toLowerCase().includes(normalizedFilter);

      if (nameMatch) {
        return true;
      }

      if (entry.kind === 'directory') {
        return subtreeMatches(entry.path);
      }

      return false;
    });
  };

  const renderEntries = (directoryPath: string, depth: number): React.ReactNode => {
    const children = directoryEntries[directoryPath] ?? [];

    return children
      .filter((entry) => {
        if (!normalizedFilter) {
          return true;
        }

        const directMatch =
          entry.name.toLowerCase().includes(normalizedFilter) ||
          toDisplayPath(rootPath, entry.path).toLowerCase().includes(normalizedFilter);

        if (directMatch) {
          return true;
        }

        if (entry.kind === 'directory') {
          return subtreeMatches(entry.path);
        }

        return false;
      })
      .map((entry) => {
        const isDirectory = entry.kind === 'directory';
        const isExpanded = expandedDirectories[entry.path];
        const isLoading = loadingDirectories[entry.path];
        const isSelected = selectedFilePath === entry.path;

        return (
          <Box key={entry.path}>
            <Box
              onClick={() => {
                if (isDirectory) {
                  onToggleDirectory(entry.path);
                  return;
                }

                onSelectFile(entry.path);
              }}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.75,
                py: 0.6,
                pl: `${depth * 14}px`,
                pr: 1,
                borderRadius: 0,
                cursor: 'pointer',
                color: isSelected ? '#f5e6a6' : '#d7e3c5',
                bgcolor: isSelected ? 'rgba(244, 186, 63, 0.12)' : 'transparent',
                '&:hover': {
                  bgcolor: 'rgba(96, 117, 87, 0.15)'
                }
              }}
            >
              {isDirectory ? (
                isExpanded ? (
                  <ExpandMore sx={{ fontSize: 18, color: '#7dd3fc' }} />
                ) : (
                  <ChevronRight sx={{ fontSize: 18, color: '#7dd3fc' }} />
                )
              ) : (
                <Box sx={{ width: 18 }} />
              )}
              {isDirectory ? (
                isExpanded ? (
                  <FolderOpen sx={{ fontSize: 18, color: '#fbbf24' }} />
                ) : (
                  <FolderOutlined sx={{ fontSize: 18, color: '#fbbf24' }} />
                )
              ) : (
                <Description sx={{ fontSize: 18, color: '#cbd5e1' }} />
              )}
              <Typography variant="body2" sx={{ flex: 1, minWidth: 0 }} noWrap>
                {entry.name}
              </Typography>
              {isLoading && <CircularProgress size={12} sx={{ color: '#7dd3fc' }} />}
            </Box>
            {isDirectory && isExpanded && renderEntries(entry.path, depth + 1)}
          </Box>
        );
      });
  };

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 2,
        border: '2px solid rgba(80, 101, 71, 0.95)',
        background: 'linear-gradient(180deg, #1a2018 0%, #11150f 100%)',
        boxShadow: '5px 5px 0 rgba(10, 13, 9, 0.92)'
      }}
    >
      <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 2.1, fontWeight: 700 }}>
        Explorer
      </Typography>
      <Typography variant="h6" sx={{ mt: 0.25, fontWeight: 800, color: '#f5e6a6', fontFamily: 'var(--font-code)' }}>
        {rootName}
      </Typography>
      <Typography variant="caption" sx={{ color: '#a5b39a', mb: 1.75 }}>
        {rootPath}
      </Typography>

      <TextField
        value={filter}
        onChange={(event) => onFilterChange(event.target.value)}
        placeholder="Filter loaded files and folders"
        size="small"
        fullWidth
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Search sx={{ fontSize: 18, color: '#7dd3fc' }} />
            </InputAdornment>
          )
        }}
        sx={{
          mb: 1.5,
          '& .MuiOutlinedInput-root': {
            bgcolor: '#1f261c',
            color: '#f3f7df',
            borderRadius: 0,
            '& fieldset': {
              borderWidth: 2,
              borderColor: 'rgba(96, 117, 87, 0.9)'
            }
          }
        }}
      />

      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          overflow: 'auto',
          pr: 0.5
        }}
      >
        {normalizedFilter && searchResults.length > 0 && (
          <Box sx={{ mb: 1.5 }}>
            <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mb: 0.75 }}>
              Quick open across workspace
            </Typography>
            {searchResults.slice(0, 8).map((entry) => (
              <Box
                key={`search-${entry.path}`}
                onClick={() => onSelectFile(entry.path)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.75,
                  py: 0.65,
                  px: 1,
                  mb: 0.5,
                  borderRadius: 0,
                  cursor: 'pointer',
                  bgcolor:
                    selectedFilePath === entry.path ? 'rgba(244, 186, 63, 0.12)' : '#1f261c',
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)',
                  '&:hover': {
                    bgcolor: 'rgba(96, 117, 87, 0.15)'
                  }
                }}
              >
                <Description sx={{ fontSize: 18, color: '#cbd5e1' }} />
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="body2" noWrap>
                    {entry.name}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#94a3b8' }} noWrap>
                    {toDisplayPath(rootPath, entry.path)}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Box>
        )}

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.75,
            py: 0.7,
            px: 1,
            mb: 0.5,
            border: '2px solid rgba(96, 117, 87, 0.9)',
            bgcolor: '#233021',
            color: '#f3f7df',
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          <FolderOpen sx={{ fontSize: 18, color: '#fbbf24' }} />
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {rootName}
          </Typography>
        </Box>
        {renderEntries(rootPath, 1)}
      </Box>
    </Box>
  );
};

export default WorkspaceTree;
