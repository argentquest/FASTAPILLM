import React, { useState, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  showSuccessToast = false,
  successMessage = 'Operation completed successfully'
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      try {
        const result = await apiFunction(...args);
        setState(prev => ({ ...prev, data: result, loading: false }));
        
        if (showSuccessToast) {
          toast.success(successMessage);
        }
        
        return result;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error?.message || error.message || 'An error occurred';
        setState(prev => ({ ...prev, error: errorMessage, loading: false }));
        toast.error(errorMessage);
        return null;
      }
    },
    [apiFunction, showSuccessToast, successMessage]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}

export function useApiQuery<T>(
  apiFunction: () => Promise<T>,
  dependencies: React.DependencyList = []
): UseApiReturn<T> & { refetch: () => void } {
  const { execute, ...rest } = useApi(apiFunction);
  
  const refetch = useCallback(() => {
    execute();
  }, [execute]);

  // Auto-fetch on mount and when dependencies change
  useEffect(() => {
    execute();
  }, [execute, ...dependencies]);

  return { ...rest, execute, refetch };
}

// Custom hook for mutations with optimistic updates
export function useApiMutation<T, U>(
  apiFunction: (data: T) => Promise<U>,
  options: {
    onSuccess?: (data: U) => void;
    onError?: (error: string) => void;
    successMessage?: string;
  } = {}
) {
  const [loading, setLoading] = useState(false);

  const mutate = useCallback(
    async (data: T): Promise<U | null> => {
      setLoading(true);
      
      try {
        const result = await apiFunction(data);
        
        if (options.successMessage) {
          toast.success(options.successMessage);
        }
        
        options.onSuccess?.(result);
        return result;
      } catch (error: any) {
        const errorMessage = error.response?.data?.error?.message || error.message || 'An error occurred';
        toast.error(errorMessage);
        options.onError?.(errorMessage);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction, options]
  );

  return { mutate, loading };
}