import React, { useEffect, useRef, useState } from 'react';
import { Box, Button, Chip, Stack, TextField, Typography } from '@mui/material';
import { PlayArrow, RestartAlt } from '@mui/icons-material';
import { TerminalSessionInfo } from '../types/sovereign';

interface UtfTerminalProps {
  session: TerminalSessionInfo | null;
  output: string;
  onRunCommand: (command: string) => Promise<void>;
  onClear: () => void;
  onRestart: () => Promise<void>;
}

const UtfTerminal: React.FC<UtfTerminalProps> = ({
  session,
  output,
  onRunCommand,
  onClear,
  onRestart
}) => {
  const [command, setCommand] = useState('');
  const outputRef = useRef<HTMLDivElement | null>(null);
  const cargoCommand = '& "$env:USERPROFILE\\.cargo\\bin\\cargo.exe"';
  const terminalPresets = [
    'git status --short --branch',
    'npm --prefix desktop run build',
    `${cargoCommand} -V`,
    `${cargoCommand} test --manifest-path engines\\waterfall_native\\Cargo.toml`,
    'Get-ChildItem',
    'python --version'
  ];

  useEffect(() => {
    outputRef.current?.scrollTo({
      top: outputRef.current.scrollHeight
    });
  }, [output]);

  const handleRun = async () => {
    if (!command.trim()) {
      return;
    }

    const nextCommand = command;
    setCommand('');
    await onRunCommand(nextCommand);
  };

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 2,
        border: '2px solid rgba(80, 101, 71, 0.95)',
        background: 'linear-gradient(180deg, #161c14 0%, #0f130d 100%)',
        boxShadow: '5px 5px 0 rgba(10, 13, 9, 0.92)'
      }}
    >
      <Stack direction="row" justifyContent="space-between" spacing={2} alignItems="center">
        <Box>
          <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 2.1, fontWeight: 700 }}>
            UTF Terminal
          </Typography>
          <Typography variant="h6" sx={{ mt: 0.25, fontWeight: 800, color: '#f5e6a6', fontFamily: 'var(--font-code)' }}>
            Local Session
          </Typography>
          <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block', mt: 0.25 }}>
            {session ? `${session.shell} at ${session.cwd}` : 'Booting offline terminal session...'}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1} alignItems="center">
          <Chip
            label={session ? 'Live' : 'Offline'}
            size="small"
            sx={{ color: session ? '#86efac' : '#fca5a5' }}
          />
          <Button
            onClick={() => {
              void onRestart();
            }}
            size="small"
            startIcon={<RestartAlt />}
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            Restart
          </Button>
          <Button
            onClick={onClear}
            size="small"
            sx={{ color: '#f3f7df', borderRadius: 0 }}
          >
            Clear
          </Button>
        </Stack>
      </Stack>

      <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 1.2 }}>
        {terminalPresets.map((preset) => (
          <Button
            key={preset}
            size="small"
            onClick={() => {
              if (session) {
                void onRunCommand(preset);
              }
            }}
            disabled={!session}
            sx={{
              color: '#d7e3c5',
              border: '1px solid rgba(96, 117, 87, 0.9)',
              bgcolor: '#1f261c',
              borderRadius: 0,
              fontFamily: 'var(--font-code)',
              fontSize: 11
            }}
          >
            {preset}
          </Button>
        ))}
      </Stack>

      <Box
        ref={outputRef}
        sx={{
          flex: 1,
          minHeight: 0,
          mt: 1.2,
          px: 1.5,
          py: 1.25,
          overflow: 'auto',
          bgcolor: '#090c08',
          border: '2px solid rgba(96, 117, 87, 0.9)',
          fontFamily: 'var(--font-code)',
          fontSize: 13,
          lineHeight: 1.55,
          whiteSpace: 'pre-wrap',
          color: '#d7f4ff',
          boxShadow: 'inset 0 0 0 2px rgba(10, 13, 9, 0.9)'
        }}
      >
        {output || '[utf-terminal] waiting for session output...'}
      </Box>

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.25} sx={{ mt: 1.5 }}>
        <TextField
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              void handleRun();
            }
          }}
          placeholder="Run a local PowerShell or Cargo command"
          fullWidth
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: '#1f261c',
              color: '#f3f7df',
              fontFamily: 'var(--font-code)',
              borderRadius: 0,
              '& fieldset': {
                borderWidth: 2,
                borderColor: 'rgba(96, 117, 87, 0.9)'
              }
            }
          }}
        />
        <Button
          onClick={() => {
            void handleRun();
          }}
          variant="contained"
          endIcon={<PlayArrow />}
          disabled={!session}
          sx={{
            minWidth: 168,
            background: 'linear-gradient(135deg, #f4ba3f 0%, #59b1a6 100%)',
            color: '#10150f',
            borderRadius: 0,
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          Run Local
        </Button>
      </Stack>
    </Box>
  );
};

export default UtfTerminal;
