import React from 'react';
import { Box, Button, Chip, Divider, Stack, TextField, Typography } from '@mui/material';
import { Send, SyncAlt, Update } from '@mui/icons-material';
import { LegionMessage, WorkOrder, WorkOrderPlan } from '../types/sovereign';

interface LegionPanelProps {
  messages: LegionMessage[];
  draft: string;
  selectedFileLabel: string;
  activeFloorName: string;
  plan: WorkOrderPlan;
  workOrders: WorkOrder[];
  onDraftChange: (value: string) => void;
  onSend: () => void;
  onQuickDispatch: (template: string) => void;
  onAdvanceWorkOrder: (workOrderId: string) => void;
}

const quickDispatchTemplates = [
  'Run a bug sweep and isolate drift sources.',
  'Coordinate a mash-up refactor across active floors.',
  'Perform a local security drill and hardening pass.',
  'Review build pipeline health and deployment scripts.'
];

const LegionPanel: React.FC<LegionPanelProps> = ({
  messages,
  draft,
  selectedFileLabel,
  activeFloorName,
  plan,
  workOrders,
  onDraftChange,
  onSend,
  onQuickDispatch,
  onAdvanceWorkOrder
}) => {
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
      <Typography
        variant="overline"
        sx={{ color: '#f4ba3f', letterSpacing: 2.1, fontWeight: 700 }}
      >
        Legion Relay
      </Typography>
      <Typography
        variant="h6"
        sx={{ mt: 0.25, fontWeight: 800, fontFamily: 'var(--font-code)', color: '#f5e6a6' }}
      >
        Work Order Dispatch
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.75, color: '#c7d0b1' }}>
        Orders stay local. The CEO floor routes crews, and the tower reflects the latest shift plan
        even when the network is gone.
      </Typography>

      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.5 }}>
        <Chip label={`Lead: ${plan.primaryFloor}`} size="small" sx={{ color: '#7dd3fc' }} />
        <Chip label={`Focus: ${activeFloorName}`} size="small" sx={{ color: '#f5e6a6' }} />
        <Chip label={`District: ${plan.district}`} size="small" sx={{ color: '#86efac' }} />
      </Stack>

      <Box
        sx={{
          mt: 1.5,
          px: 1.2,
          py: 1,
          border: '2px solid rgba(96, 117, 87, 0.9)',
          bgcolor: '#1f261c',
          boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
        }}
      >
        <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block' }}>
          Current context
        </Typography>
        <Typography variant="body2" sx={{ color: '#f3f7df' }} noWrap>
          {selectedFileLabel}
        </Typography>
      </Box>

      <Box sx={{ mt: 1.5 }}>
        <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block', mb: 0.8 }}>
          QUICK DISPATCH TEMPLATES
        </Typography>
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap">
          {quickDispatchTemplates.map((template) => (
            <Chip
              key={template}
              label={template}
              size="small"
              onClick={() => onQuickDispatch(template)}
              sx={{
                color: '#d7e3c5',
                border: '1px solid rgba(96, 117, 87, 0.85)',
                bgcolor: '#1f261c',
                cursor: 'pointer'
              }}
            />
          ))}
        </Stack>
      </Box>

      <Divider sx={{ my: 1.5, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

      <Box sx={{ mb: 1.3 }}>
        <Typography variant="caption" sx={{ color: '#a5b39a', display: 'block', mb: 0.8 }}>
          ACTIVE WORK ORDER QUEUE
        </Typography>
        <Box sx={{ maxHeight: 176, overflow: 'auto', pr: 0.5 }}>
          {workOrders.length === 0 ? (
            <Box
              sx={{
                p: 1.1,
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: '#1f261c'
              }}
            >
              <Typography variant="body2" sx={{ color: '#c7d0b1' }}>
                No local work orders yet.
              </Typography>
            </Box>
          ) : (
            workOrders.slice(0, 6).map((order) => (
              <Box
                key={order.id}
                sx={{
                  mb: 0.8,
                  p: 1,
                  border: '2px solid rgba(96, 117, 87, 0.9)',
                  bgcolor: '#1f261c',
                  boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
                }}
              >
                <Stack direction="row" justifyContent="space-between" spacing={1}>
                  <Box sx={{ minWidth: 0 }}>
                    <Typography variant="body2" sx={{ color: '#f3f7df', fontWeight: 700 }} noWrap>
                      {order.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#a5b39a' }}>
                      {order.createdAt} | {order.assignedFloor} | {order.district}
                    </Typography>
                  </Box>
                  <Chip
                    label={order.urgency}
                    size="small"
                    sx={{
                      color:
                        order.urgency === 'critical'
                          ? '#fecaca'
                          : order.urgency === 'priority'
                            ? '#fef3c7'
                            : '#d9f99d'
                    }}
                  />
                </Stack>
                <Typography variant="body2" sx={{ mt: 0.8, color: '#c7d0b1' }}>
                  {order.summary}
                </Typography>
                <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 0.8 }}>
                  <Chip label={order.status} size="small" sx={{ color: '#7dd3fc' }} />
                  {order.supportFloors.slice(0, 2).map((floor) => (
                    <Chip
                      key={`${order.id}-${floor}`}
                      label={floor}
                      size="small"
                      variant="outlined"
                      sx={{ color: '#f0abfc', borderColor: 'rgba(240, 171, 252, 0.45)' }}
                    />
                  ))}
                  <Button
                    onClick={() => onAdvanceWorkOrder(order.id)}
                    size="small"
                    startIcon={<Update fontSize="small" />}
                    sx={{ color: '#f5e6a6' }}
                  >
                    Advance
                  </Button>
                </Stack>
              </Box>
            ))
          )}
        </Box>
      </Box>

      <Divider sx={{ my: 1.2, borderColor: 'rgba(96, 117, 87, 0.75)' }} />

      <Box sx={{ flex: 1, minHeight: 0, overflow: 'auto', pr: 0.5 }}>
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              mb: 1,
              p: 1.15,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor:
                message.role === 'conference'
                  ? '#162229'
                  : message.role === 'user'
                    ? '#282113'
                    : '#1f261c',
              boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1 }}>
              <Typography variant="subtitle2" sx={{ color: '#f3f7df' }}>
                {message.title}
              </Typography>
              <Typography variant="caption" sx={{ color: '#a5b39a' }}>
                {message.timestamp}
              </Typography>
            </Box>
            <Typography
              variant="body2"
              sx={{ mt: 0.7, color: '#c7d0b1', whiteSpace: 'pre-wrap' }}
            >
              {message.body}
            </Typography>
            <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 0.8 }}>
              {message.route.map((routeStep) => (
                <Chip
                  key={`${message.id}-${routeStep}`}
                  label={routeStep}
                  size="small"
                  variant="outlined"
                  sx={{ color: '#cbd5e1', borderColor: 'rgba(148, 163, 184, 0.24)' }}
                />
              ))}
            </Stack>
          </Box>
        ))}
      </Box>

      <Box sx={{ mt: 1.4 }}>
        <TextField
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="Describe the repair order or ask Legion to coordinate a mash-up project"
          multiline
          minRows={3}
          maxRows={6}
          fullWidth
          sx={{
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
        <Button
          onClick={onSend}
          variant="contained"
          endIcon={<Send />}
          disabled={!draft.trim()}
          sx={{
            mt: 1.2,
            alignSelf: 'flex-start',
            background: 'linear-gradient(135deg, #f4ba3f 0%, #59b1a6 100%)',
            color: '#10150f',
            borderRadius: 0,
            boxShadow: '3px 3px 0 rgba(10, 13, 9, 0.86)'
          }}
        >
          Dispatch Work Order
        </Button>
        <Stack direction="row" spacing={0.75} useFlexGap flexWrap="wrap" sx={{ mt: 1.1 }}>
          {plan.supportFloors.map((floor) => (
            <Chip
              key={floor}
              icon={<SyncAlt sx={{ color: '#f0abfc !important' }} />}
              label={floor}
              size="small"
              variant="outlined"
              sx={{ color: '#f0abfc', borderColor: 'rgba(240, 171, 252, 0.45)' }}
            />
          ))}
        </Stack>
      </Box>
    </Box>
  );
};

export default LegionPanel;
