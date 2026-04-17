import { formatStatus, getStatusBadgeClass } from '../utils/formatters';

export default function StatusBadge({ status }) {
  return (
    <span className={`badge ${getStatusBadgeClass(status)}`}>
      {formatStatus(status)}
    </span>
  );
}
