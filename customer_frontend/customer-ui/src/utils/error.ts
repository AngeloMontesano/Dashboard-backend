import { classifyError } from './errorClassify';

export function stringifyError(err: unknown): string {
  const classified = classifyError(err);
  if (classified.detailMessage && classified.detailMessage !== classified.userMessage) {
    return classified.detailMessage;
  }
  return classified.userMessage;
}
