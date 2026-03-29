import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Box, Button, Chip, MenuItem, Slider, Stack, TextField, Typography } from '@mui/material';
import type {
  WaterfallNativeDocument,
  WaterfallNativeRenderBox,
  WaterfallNativeRenderResult,
  WaterfallNativeRouteAction,
  WaterfallTabState
} from '../types/sovereign';

interface WaterfallNativeRoutePaneProps {
  tab: WaterfallTabState;
  active: boolean;
  reloadToken: number;
  nativeDocument?: WaterfallNativeDocument | null;
  actions: WaterfallNativeRouteAction[];
  onAction: (action: WaterfallNativeRouteAction) => void;
  onRendered: (tabId: string, renderResult: WaterfallNativeRenderResult) => void;
  onRenderError: (tabId: string, message: string) => void;
}

const GRID_X = 9;
const GRID_Y = 30;
const getRenderBoxDomKey = (renderBox: WaterfallNativeRenderBox, index: number) =>
  `${renderBox.nodePath}-${index}`;

const getControlDraftKey = (renderBox: WaterfallNativeRenderBox) =>
  `${renderBox.nodePath}:${renderBox.settingPath || 'unset'}`;

const getInitialControlDraft = (renderBox: WaterfallNativeRenderBox) => {
  if (typeof renderBox.controlStringValue === 'string') {
    return renderBox.controlStringValue;
  }

  if (typeof renderBox.controlNumberValue === 'number') {
    return String(renderBox.controlNumberValue);
  }

  return '';
};

const coerceSliderValue = (value: number | number[]) => (Array.isArray(value) ? value[0] : value);

const formatControlSuffix = (settingPath: string | null) => {
  if (!settingPath) {
    return '';
  }

  if (settingPath.includes('Percent')) {
    return '%';
  }

  if (settingPath.includes('Minutes')) {
    return ' min';
  }

  return '';
};

const getBlueprintPalette = (renderBox: WaterfallNativeRenderBox, interactive: boolean) => {
  const role = renderBox.role;
  const surface = renderBox.surface || '';
  const tone = renderBox.tone || '';

  if (surface === 'hero' || role.includes('hero')) {
    return {
      borderColor:
        tone === 'ember'
          ? interactive
            ? 'rgba(251, 146, 60, 0.92)'
            : 'rgba(251, 146, 60, 0.72)'
          : interactive
            ? 'rgba(244, 186, 63, 0.92)'
            : 'rgba(244, 186, 63, 0.72)',
      background:
        tone === 'signal'
          ? 'linear-gradient(180deg, rgba(7, 38, 49, 0.82) 0%, rgba(10, 24, 38, 0.92) 100%)'
          : 'linear-gradient(180deg, rgba(69, 49, 11, 0.78) 0%, rgba(28, 22, 7, 0.9) 100%)',
      color: tone === 'signal' ? '#d7f4ff' : '#fde7ae'
    };
  }

  if (surface === 'control' || role.includes('control')) {
    return {
      borderColor: interactive ? 'rgba(244, 186, 63, 0.9)' : 'rgba(244, 186, 63, 0.72)',
      background:
        'linear-gradient(180deg, rgba(58, 42, 12, 0.82) 0%, rgba(23, 18, 8, 0.92) 100%)',
      color: '#fdf0c4'
    };
  }

  if (
    interactive ||
    renderBox.interactive ||
    role.includes('link') ||
    role.includes('action') ||
    tone === 'signal'
  ) {
    return {
      borderColor: 'rgba(125, 211, 252, 0.88)',
      background:
        'linear-gradient(180deg, rgba(7, 38, 49, 0.82) 0%, rgba(10, 24, 38, 0.92) 100%)',
      color: '#d7f4ff'
    };
  }

  if (surface === 'card' || surface === 'panel' || surface === 'cluster' || role.includes('card')) {
    return {
      borderColor: 'rgba(89, 177, 166, 0.74)',
      background:
        'linear-gradient(180deg, rgba(14, 56, 54, 0.7) 0%, rgba(10, 27, 31, 0.9) 100%)',
      color: '#e2f8f2'
    };
  }

  if (role === 'text') {
    return {
      borderColor: 'rgba(89, 177, 166, 0.62)',
      background: 'rgba(14, 56, 54, 0.54)',
      color: '#e2f8f2'
    };
  }

  if (role.includes('h1') || role.includes('h2')) {
    return {
      borderColor: 'rgba(244, 186, 63, 0.72)',
      background: 'rgba(69, 49, 11, 0.72)',
      color: '#fde7ae'
    };
  }

  if (role.includes('main') || role.includes('section')) {
    return {
      borderColor: 'rgba(125, 211, 252, 0.68)',
      background: 'rgba(10, 30, 49, 0.7)',
      color: '#d7f4ff'
    };
  }

  return {
    borderColor: 'rgba(164, 180, 152, 0.55)',
    background: 'rgba(23, 28, 20, 0.74)',
    color: '#f3f7df'
  };
};

const WaterfallNativeRoutePane: React.FC<WaterfallNativeRoutePaneProps> = ({
  tab,
  active,
  reloadToken,
  nativeDocument,
  actions,
  onAction,
  onRendered,
  onRenderError
}) => {
  const [renderResult, setRenderResult] = useState<WaterfallNativeRenderResult | null>(null);
  const [renderError, setRenderError] = useState('');
  const [controlDrafts, setControlDrafts] = useState<Record<string, string>>({});
  const interactiveRefs = React.useRef<Record<string, HTMLDivElement | null>>({});
  const actionMap = useMemo(
    () => new Map(actions.map((action) => [action.id, action])),
    [actions]
  );
  const focusableBoxes = useMemo(
    () =>
      (renderResult?.boxes || [])
        .map((renderBox, index) => ({
          renderBox,
          domKey: getRenderBoxDomKey(renderBox, index)
        }))
        .filter((entry) => typeof entry.renderBox.focusIndex === 'number')
        .sort((left, right) => (left.renderBox.focusIndex || 0) - (right.renderBox.focusIndex || 0)),
    [renderResult]
  );

  useEffect(() => {
    if (!renderResult) {
      return;
    }

    const nextDrafts = renderResult.boxes.reduce<Record<string, string>>((drafts, renderBox) => {
      if (renderBox.controlKind && renderBox.settingPath) {
        drafts[getControlDraftKey(renderBox)] = getInitialControlDraft(renderBox);
      }
      return drafts;
    }, {});

    setControlDrafts(nextDrafts);
  }, [renderResult]);

  useEffect(() => {
    if (!active || !tab.url) {
      return;
    }

    if (
      !window.electron?.browser?.renderInternalRoute ||
      !window.electron?.browser?.renderMarkupDocument
    ) {
      const message = 'WaterFall native routes require the local Electron bridge.';
      setRenderError(message);
      onRenderError(tab.id, message);
      return;
    }

    let cancelled = false;
    setRenderError('');
    setRenderResult((current) => (current?.route === tab.url ? current : null));

    const renderPromise = nativeDocument
      ? window.electron.browser.renderMarkupDocument(nativeDocument, 92)
      : window.electron.browser.renderInternalRoute(tab.url, 92);

    void renderPromise
      .then((result) => {
        if (cancelled) {
          return;
        }

        setRenderResult(result);
        onRendered(tab.id, result);
      })
      .catch((error) => {
        if (cancelled) {
          return;
        }

        const message =
          error instanceof Error
            ? error.message
            : 'WaterFall could not render that native route.';
        setRenderError(message);
        onRenderError(tab.id, message);
      });

    return () => {
      cancelled = true;
    };
  }, [active, nativeDocument, onRenderError, onRendered, reloadToken, tab.id, tab.url]);

  const resolveRenderBoxAction = (renderBox: WaterfallNativeRenderBox) => {
    if (renderBox.actionId) {
      const mappedAction = actionMap.get(renderBox.actionId);
      if (mappedAction) {
        return mappedAction;
      }
    }

    if (renderBox.href) {
      return {
        id: `inline:${tab.id}:${renderBox.href}`,
        title: renderBox.text || renderBox.href,
        caption: renderBox.href,
        kind: 'navigate' as const,
        target: renderBox.href
      };
    }

    return null;
  };

  const triggerRenderBoxAction = (renderBox: WaterfallNativeRenderBox) => {
    const nextAction = resolveRenderBoxAction(renderBox);
    if (nextAction) {
      onAction(nextAction);
    }
  };

  const focusSiblingTarget = (renderBox: WaterfallNativeRenderBox, direction: -1 | 1) => {
    const currentFocusIndex = renderBox.focusIndex;
    if (typeof currentFocusIndex !== 'number' || focusableBoxes.length === 0) {
      return;
    }

    const currentIndex = focusableBoxes.findIndex(
      (entry) => entry.renderBox.focusIndex === currentFocusIndex
    );
    if (currentIndex < 0) {
      return;
    }

    const nextIndex = Math.min(
      focusableBoxes.length - 1,
      Math.max(0, currentIndex + direction)
    );
    const nextTarget = interactiveRefs.current[focusableBoxes[nextIndex].domKey];
    nextTarget?.focus();
  };

  const commitControlValue = (
    renderBox: WaterfallNativeRenderBox,
    nextStringValue?: string,
    nextNumberValue?: number
  ) => {
    if (!renderBox.settingPath) {
      return;
    }

    onAction({
      id: `control:${renderBox.nodePath}:${renderBox.settingPath}`,
      title: renderBox.controlLabel || renderBox.settingPath,
      caption: renderBox.controlCaption || renderBox.settingPath,
      kind: 'set-setting',
      settingPath: renderBox.settingPath,
      stringValue: nextStringValue,
      numberValue: nextNumberValue
    });
  };

  if (!tab.url) {
    return null;
  }

  const interactiveCount =
    renderResult?.boxes.filter((renderBox) => renderBox.interactive).length ||
    0;
  const focusableCount =
    renderResult?.boxes.filter((renderBox) => typeof renderBox.focusIndex === 'number').length ||
    0;

  return (
    <Box
      sx={{
        display: active ? 'flex' : 'none',
        flexDirection: 'column',
        height: '100%',
        overflow: 'auto',
        p: 3,
        background:
          'radial-gradient(circle at top left, rgba(89, 177, 166, 0.18), transparent 38%), linear-gradient(180deg, #090c08 0%, #0f130d 55%, #131812 100%)'
      }}
    >
      {!renderResult && !renderError && (
        <Box
          sx={{
            p: 2,
            border: '2px solid rgba(96, 117, 87, 0.9)',
            bgcolor: 'rgba(16, 21, 15, 0.92)'
          }}
        >
          <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 1.8 }}>
            Native Route
          </Typography>
          <Typography variant="h5" sx={{ color: '#f5e6a6', fontFamily: 'var(--font-code)' }}>
            Rendering {tab.url}
          </Typography>
          <Typography variant="body2" sx={{ mt: 1, color: '#c7d0b1' }}>
            WaterFall is calling its native engine lane and building a render blueprint.
          </Typography>
        </Box>
      )}

      {renderError && (
        <Alert
          severity="warning"
          sx={{
            bgcolor: '#221b12',
            border: '2px solid rgba(96, 117, 87, 0.9)',
            borderRadius: 0
          }}
        >
          {renderError}
        </Alert>
      )}

      {renderResult && (
        <Stack spacing={2.25}>
          <Box>
            <Typography variant="overline" sx={{ color: '#f4ba3f', letterSpacing: 2.1 }}>
              waterfall:// native route
            </Typography>
            <Typography
              variant="h3"
              sx={{ mt: 0.5, color: '#f5e6a6', fontWeight: 800, fontFamily: 'var(--font-code)' }}
            >
              {renderResult.title}
            </Typography>
            <Typography variant="body1" sx={{ mt: 1, color: '#d7e3c5', maxWidth: 820 }}>
              {renderResult.subtitle}
            </Typography>
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1.5 }}>
              <Chip label={renderResult.route} sx={{ color: '#7dd3fc' }} />
              <Chip label={renderResult.engine.engineId} sx={{ color: '#fbbf24' }} />
              <Chip label={renderResult.engine.integration} sx={{ color: '#c4b5fd' }} />
              {interactiveCount > 0 && (
                <Chip
                  label={`${interactiveCount} interactive box${interactiveCount === 1 ? '' : 'es'}`}
                  sx={{ color: '#86efac' }}
                />
              )}
              {focusableCount > 0 && (
                <Chip label={`${focusableCount} focus target${focusableCount === 1 ? '' : 's'}`} sx={{ color: '#93c5fd' }} />
              )}
              {renderResult.engine.focus.map((focus) => (
                <Chip key={focus} label={focus} size="small" sx={{ color: '#86efac' }} />
              ))}
            </Stack>
          </Box>

          {actions.length > 0 && (
            <Box
              sx={{
                p: 2,
                border: '2px solid rgba(96, 117, 87, 0.9)',
                bgcolor: 'rgba(16, 21, 15, 0.92)'
              }}
            >
              <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
                Action Deck
              </Typography>
              <Typography variant="body2" sx={{ mt: 0.75, color: '#a5b39a' }}>
                Blueprint clicks are live now. This deck remains as a fallback and a route summary.
              </Typography>
              <Box
                sx={{
                  mt: 1.5,
                  display: 'grid',
                  gap: 1.1,
                  gridTemplateColumns: {
                    xs: '1fr',
                    md: 'repeat(2, minmax(0, 1fr))'
                  }
                }}
              >
                {actions.map((action) => (
                  <Box
                    key={action.id}
                    onClick={() => onAction(action)}
                    sx={{
                      p: 1.15,
                      cursor: 'pointer',
                      border: '1px solid rgba(89, 177, 166, 0.46)',
                      bgcolor: 'rgba(10, 30, 49, 0.52)',
                      color: '#d7f4ff',
                      '&:hover': {
                        bgcolor: 'rgba(21, 58, 72, 0.72)'
                      }
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>
                      {action.title}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ color: '#c7d0b1', display: 'block', mt: 0.35 }}
                    >
                      {action.caption}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          )}

          <Box
            sx={{
              p: 2,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: 'rgba(16, 21, 15, 0.92)'
            }}
          >
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Native Blueprint
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.75, color: '#a5b39a' }}>
              The Rust engine parsed WaterFall markup, preserved route metadata, and emitted
              positioned boxes. Cyan boxes can move you through WaterFall directly.
            </Typography>

            <Box
              sx={{
                mt: 2,
                minWidth: Math.max(360, renderResult.viewportWidth * GRID_X + 42),
                minHeight: Math.max(300, renderResult.documentHeight * GRID_Y + 42),
                position: 'relative',
                border: '1px solid rgba(89, 177, 166, 0.24)',
                background:
                  'linear-gradient(180deg, rgba(7, 18, 18, 0.9) 0%, rgba(7, 14, 10, 0.96) 100%)',
                overflow: 'hidden'
              }}
            >
              {renderResult.boxes.map((renderBox, index) => {
                const nextAction = resolveRenderBoxAction(renderBox);
                const hasNativeControl = Boolean(renderBox.controlKind && renderBox.settingPath);
                const interactive = renderBox.interactive || Boolean(nextAction) || hasNativeControl;
                const clickable = Boolean(nextAction) && !hasNativeControl;
                const palette = getBlueprintPalette(renderBox, interactive);
                const controlKey = getControlDraftKey(renderBox);
                const controlDraft = controlDrafts[controlKey] ?? getInitialControlDraft(renderBox);
                const controlSuffix = formatControlSuffix(renderBox.settingPath);
                const sliderValue = Math.min(
                  renderBox.controlMax ?? Number(controlDraft || 0),
                  Math.max(
                    renderBox.controlMin ?? 0,
                    Number(controlDraft || renderBox.controlNumberValue || 0)
                  )
                );

                return (
                  <Box
                    key={getRenderBoxDomKey(renderBox, index)}
                    ref={(node: HTMLDivElement | null) => {
                      interactiveRefs.current[getRenderBoxDomKey(renderBox, index)] = node;
                    }}
                    role={clickable ? (renderBox.href ? 'link' : 'button') : undefined}
                    tabIndex={clickable ? 0 : -1}
                    aria-label={clickable ? nextAction?.title || renderBox.text || renderBox.role : undefined}
                    onClick={clickable ? () => triggerRenderBoxAction(renderBox) : undefined}
                    onKeyDown={
                      clickable
                        ? (event) => {
                            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                              event.preventDefault();
                              focusSiblingTarget(renderBox, 1);
                              return;
                            }

                            if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                              event.preventDefault();
                              focusSiblingTarget(renderBox, -1);
                              return;
                            }

                            if (event.key === 'Enter' || event.key === ' ') {
                              event.preventDefault();
                              triggerRenderBoxAction(renderBox);
                            }
                          }
                        : undefined
                    }
                    sx={{
                      position: 'absolute',
                      left: 18 + renderBox.x * GRID_X,
                      top: 18 + renderBox.y * GRID_Y,
                      width: Math.max(96, renderBox.width * GRID_X),
                      height: Math.max(28, renderBox.height * GRID_Y),
                      p: 0.9,
                      zIndex: renderBox.zIndex,
                      border: `1px solid ${palette.borderColor}`,
                      borderStyle: renderBox.layout === 'grid' ? 'dashed' : 'solid',
                      bgcolor: palette.background,
                      color: palette.color,
                      overflow: 'hidden',
                      display: 'flex',
                      flexDirection: 'column',
                      boxShadow: interactive
                        ? '0 14px 28px rgba(0, 0, 0, 0.24)'
                        : '0 8px 18px rgba(0, 0, 0, 0.16)',
                      cursor: clickable ? 'pointer' : 'default',
                      transition:
                        'transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease',
                      outline: 'none',
                      '&:hover': clickable
                        ? {
                            transform: 'translate(-2px, -2px)',
                            boxShadow: '0 16px 32px rgba(0, 0, 0, 0.28)',
                            borderColor: '#7dd3fc'
                          }
                        : undefined,
                      '&:focus-visible': clickable
                        ? {
                            borderColor: '#f4ba3f',
                            boxShadow: '0 0 0 2px rgba(244, 186, 63, 0.3)'
                          }
                        : undefined
                    }}
                  >
                    <Typography variant="caption" sx={{ display: 'block', opacity: 0.72 }}>
                      {renderBox.role}
                    </Typography>
                    {hasNativeControl && (
                      <Stack spacing={0.85} sx={{ mt: 0.55, minHeight: 0 }}>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 700 }}>
                            {renderBox.controlLabel || renderBox.settingPath}
                          </Typography>
                          {renderBox.controlCaption && (
                            <Typography
                              variant="caption"
                              sx={{ display: 'block', mt: 0.35, color: '#c7d0b1' }}
                            >
                              {renderBox.controlCaption}
                            </Typography>
                          )}
                        </Box>

                        {renderBox.controlKind === 'text' && (
                          <Stack direction="row" spacing={0.8} alignItems="center">
                            <TextField
                              size="small"
                              fullWidth
                              value={controlDraft}
                              placeholder={renderBox.controlPlaceholder || undefined}
                              onChange={(event) =>
                                setControlDrafts((current) => ({
                                  ...current,
                                  [controlKey]: event.target.value
                                }))
                              }
                              onBlur={() => commitControlValue(renderBox, controlDraft)}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter') {
                                  event.preventDefault();
                                  commitControlValue(renderBox, controlDraft);
                                }
                              }}
                              sx={{
                                '& .MuiOutlinedInput-root': {
                                  bgcolor: 'rgba(9, 12, 8, 0.92)',
                                  color: '#f3f7df',
                                  borderRadius: 0,
                                  fontSize: 12
                                }
                              }}
                            />
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => commitControlValue(renderBox, controlDraft)}
                              sx={{
                                minWidth: 0,
                                px: 1.2,
                                color: '#fde7ae',
                                borderColor: 'rgba(244, 186, 63, 0.6)'
                              }}
                            >
                              Apply
                            </Button>
                          </Stack>
                        )}

                        {renderBox.controlKind === 'select' && (
                          <TextField
                            select
                            size="small"
                            fullWidth
                            value={controlDraft}
                            onChange={(event) => {
                              const nextValue = event.target.value;
                              setControlDrafts((current) => ({
                                ...current,
                                [controlKey]: nextValue
                              }));
                              commitControlValue(renderBox, nextValue);
                            }}
                            sx={{
                              '& .MuiOutlinedInput-root': {
                                bgcolor: 'rgba(9, 12, 8, 0.92)',
                                color: '#f3f7df',
                                borderRadius: 0,
                                fontSize: 12
                              }
                            }}
                          >
                            {renderBox.controlOptions.map((option) => (
                              <MenuItem key={option.value} value={option.value}>
                                {option.label}
                              </MenuItem>
                            ))}
                          </TextField>
                        )}

                        {renderBox.controlKind === 'range' && (
                          <Box sx={{ px: 0.6 }}>
                            <Slider
                              size="small"
                              value={sliderValue}
                              min={renderBox.controlMin ?? 0}
                              max={renderBox.controlMax ?? 100}
                              step={renderBox.controlStep ?? 1}
                              valueLabelDisplay="auto"
                              onChange={(_, value) => {
                                const nextValue = String(coerceSliderValue(value));
                                setControlDrafts((current) => ({
                                  ...current,
                                  [controlKey]: nextValue
                                }));
                              }}
                              onChangeCommitted={(_, value) =>
                                commitControlValue(renderBox, undefined, coerceSliderValue(value))
                              }
                              sx={{
                                color: '#f4ba3f',
                                mt: 0.25,
                                '& .MuiSlider-valueLabel': {
                                  bgcolor: '#1b2017'
                                }
                              }}
                            />
                            <Typography variant="caption" sx={{ color: '#c7d0b1' }}>
                              Current value: {sliderValue}
                              {controlSuffix}
                            </Typography>
                          </Box>
                        )}
                      </Stack>
                    )}
                    {!hasNativeControl && renderBox.text && (
                      <Typography variant="body2" sx={{ mt: 0.45 }}>
                        {renderBox.text}
                      </Typography>
                    )}
                    {clickable && !renderBox.text && nextAction && (
                      <Typography variant="body2" sx={{ mt: 0.45, fontWeight: 700 }}>
                        {nextAction.title}
                      </Typography>
                    )}
                    {clickable && nextAction && renderBox.role !== 'text' && (
                      <Typography
                        variant="caption"
                        sx={{ display: 'block', mt: 0.4, color: '#c7d0b1' }}
                      >
                        {nextAction.caption}
                      </Typography>
                    )}
                  </Box>
                );
              })}
            </Box>
          </Box>

          <Box
            sx={{
              p: 2,
              border: '2px solid rgba(96, 117, 87, 0.9)',
              bgcolor: 'rgba(16, 21, 15, 0.92)'
            }}
          >
            <Typography variant="subtitle2" sx={{ color: '#f5e6a6' }}>
              Route Markup
            </Typography>
            <Box
              component="pre"
              sx={{
                mt: 1.2,
                mb: 0,
                p: 1.5,
                overflow: 'auto',
                bgcolor: '#090c08',
                color: '#d7f4ff',
                fontFamily: 'var(--font-code)',
                fontSize: 12,
                border: '1px solid rgba(96, 117, 87, 0.75)'
              }}
            >
              {renderResult.markup}
            </Box>
          </Box>
        </Stack>
      )}
    </Box>
  );
};

export default WaterfallNativeRoutePane;
