/**
 * Utility functions for safe date handling
 */

export const formatDate = (dateString: string | undefined | null): string => {
  if (!dateString) return 'Unknown date';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid date';
    }
    return date.toLocaleDateString();
  } catch (error) {
    return 'Invalid date';
  }
};

export const formatTime = (dateString: string | undefined | null): string => {
  if (!dateString) return 'Unknown time';
  
  try {
    // Handle both string and Date objects
    const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
    if (!date || isNaN(date.getTime())) {
      console.warn('Invalid date for formatTime:', dateString);
      return 'Invalid time';
    }
    return date.toLocaleTimeString();
  } catch (error) {
    console.error('Error formatting time:', error, 'Input:', dateString);
    return 'Invalid time';
  }
};

export const formatDateTime = (dateString: string | undefined | null): string => {
  if (!dateString) return 'Unknown date/time';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return 'Invalid date/time';
    }
    return date.toLocaleString();
  } catch (error) {
    return 'Invalid date/time';
  }
};