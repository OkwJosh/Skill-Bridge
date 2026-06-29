import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * useAIInsight — opinionated wrapper around useApi for AI Engine endpoints.
 *
 * Adds, compared to useApi:
 *   - `refresh()`     — re-fetches with the `?refresh=true` param (force recompute)
 *   - `aiDisabled`    — boolean derived from the 503 `ai_disabled` error, so UI
 *                       can hide AI panels gracefully when the server lacks
 *                       GEMINI_API_KEY (common in local dev).
 *   - Cancellation    — in-flight request is aborted on unmount / new fetch.
 *
 * The `apiFn` must accept an optional `{ refresh }` argument:
 *   useAIInsight(({ refresh } = {}) => getMyTrustScore({ refresh }))
 *
 * Returns the same shape as useApi plus `refresh` and `aiDisabled`.
 */
export function useAIInsight(apiFn, deps = []) {
  const [data, setData]               = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [aiDisabled, setAiDisabled]   = useState(false);

  // Track the in-flight controller so a new fetch or unmount cancels the old.
  const inFlightRef = useRef(null);

  const run = useCallback(async ({ refresh = false } = {}) => {
    inFlightRef.current?.abort();
    const controller = new AbortController();
    inFlightRef.current = controller;

    setLoading(true);
    setError(null);
    setAiDisabled(false);

    try {
      // apiFn receives both the user-controlled `refresh` and the AbortSignal.
      const result = await apiFn({ refresh, signal: controller.signal });
      if (inFlightRef.current === controller) setData(result);
      return result;
    } catch (err) {
      if (err.name === 'AbortError') return null;
      if (inFlightRef.current !== controller) return null;
      // The client.js fetch wrapper surfaces backend error messages.
      // We don't have the error code directly, so detect by message text.
      // (See backend/ai_engine/views.py:_handle_ai_exception.)
      if (/AI features are not configured/i.test(err.message)) {
        setAiDisabled(true);
      } else {
        setError(err.message);
      }
      return null;
    } finally {
      if (inFlightRef.current === controller) {
        setLoading(false);
        inFlightRef.current = null;
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  // Initial load + when deps change
  useEffect(() => {
    run();
    return () => inFlightRef.current?.abort();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [run]);

  return {
    data,
    loading,
    error,
    aiDisabled,
    refetch: () => run(),
    refresh: () => run({ refresh: true }),
  };
}
