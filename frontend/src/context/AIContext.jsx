import {
  createContext, useContext, useState, useCallback, useRef, useEffect,
} from 'react';
import { matchCv as matchCvRequest } from '../api/ai';

const AIContext = createContext(null);

export function AIProvider({ children }) {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [result, setResult]   = useState(null);

  // Track the in-flight AbortController so a new request cancels the old one
  // and unmount cancels any pending request.
  const inFlightRef = useRef(null);

  useEffect(() => () => inFlightRef.current?.abort(), []);

  const matchCv = useCallback(async (cvData) => {
    inFlightRef.current?.abort();
    const controller = new AbortController();
    inFlightRef.current = controller;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await matchCvRequest(cvData, { signal: controller.signal });
      if (inFlightRef.current === controller) {
        setResult(data);
        return data;
      }
      return null;
    } catch (err) {
      if (err.name === 'AbortError') return null;
      if (inFlightRef.current === controller) setError(err.message);
      throw err;
    } finally {
      if (inFlightRef.current === controller) {
        setLoading(false);
        inFlightRef.current = null;
      }
    }
  }, []);

  const reset = useCallback(() => {
    inFlightRef.current?.abort();
    setLoading(false);
    setError(null);
    setResult(null);
  }, []);

  return (
    <AIContext.Provider value={{ loading, error, result, matchCv, reset }}>
      {children}
    </AIContext.Provider>
  );
}

export const useAI = () => {
  const ctx = useContext(AIContext);
  if (!ctx) throw new Error('useAI must be used inside <AIProvider>');
  return ctx;
};
