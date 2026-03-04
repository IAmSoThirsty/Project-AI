//                                           [2026-03-03 13:45]
//                                          Productivity: Active
/**
 * Utility for merging class names
 */

import clsx, { ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
