import { useEffect } from 'react';
import logger from '../utils/logger';

export const useComponentLogger = (componentName: string) => {
  const componentLogger = logger.component(componentName);

  useEffect(() => {
    componentLogger.debug(`Component ${componentName} mounted`);
    
    return () => {
      componentLogger.debug(`Component ${componentName} unmounted`);
    };
  }, [componentName, componentLogger]);

  // Track user interactions
  const logUserAction = (action: string, data?: any) => {
    logger.userAction(action, data, componentName);
  };

  // Track performance
  const logPerformance = (operation: string, startTime: number) => {
    const duration = Date.now() - startTime;
    logger.performance(operation, duration, componentName);
  };

  return {
    ...componentLogger,
    logUserAction,
    logPerformance,
  };
};