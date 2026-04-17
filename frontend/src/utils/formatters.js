import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'MMM d, yyyy');
  } catch {
    return dateStr;
  }
}

export function formatRelative(dateStr) {
  if (!dateStr) return '—';
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function formatScore(score) {
  if (score === null || score === undefined) return '—';
  return Math.round(score);
}

export function formatMatchPercent(score) {
  if (score === null || score === undefined) return '—';
  return `${Math.round(score * 100)}%`;
}

export function getScoreColor(score) {
  if (score >= 80) return 'var(--success)';
  if (score >= 60) return 'var(--warning)';
  return 'var(--danger)';
}

export function getStatusBadgeClass(status) {
  const map = {
    not_applied: 'badge-neutral',
    applied: 'badge-info',
    interview_r1: 'badge-warning',
    interview_r2: 'badge-warning',
    offer: 'badge-success',
    rejected: 'badge-danger',
    withdrawn: 'badge-neutral',
  };
  return map[status] || 'badge-neutral';
}

export function formatStatus(status) {
  const map = {
    not_applied: 'Not Applied',
    applied: 'Applied',
    interview_r1: 'Interview R1',
    interview_r2: 'Interview R2',
    offer: 'Offer',
    rejected: 'Rejected',
    withdrawn: 'Withdrawn',
  };
  return map[status] || status;
}
