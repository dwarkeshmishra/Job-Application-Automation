import { useState } from 'react';
import { SOURCE_OPTIONS } from '../utils/constants';

export default function FilterBar({ onFilter }) {
  const [search, setSearch] = useState('');
  const [source, setSource] = useState('');
  const [minScore, setMinScore] = useState('');

  const apply = () => {
    onFilter({
      search: search || undefined,
      source: source || undefined,
      min_score: minScore ? parseInt(minScore) : undefined,
    });
  };

  return (
    <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap', alignItems: 'flex-end' }}>
      <div className="form-group" style={{ marginBottom: 0, flex: '1 1 200px' }}>
        <label>Search</label>
        <input
          className="input"
          placeholder="Role or company..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && apply()}
          id="filter-search"
        />
      </div>
      <div className="form-group" style={{ marginBottom: 0, flex: '0 0 150px' }}>
        <label>Source</label>
        <select className="select" value={source} onChange={(e) => setSource(e.target.value)} id="filter-source">
          <option value="">All</option>
          {SOURCE_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>
      <div className="form-group" style={{ marginBottom: 0, flex: '0 0 120px' }}>
        <label>Min ATS</label>
        <input
          className="input" type="number" min="0" max="100"
          placeholder="0" value={minScore}
          onChange={(e) => setMinScore(e.target.value)}
          id="filter-minscore"
        />
      </div>
      <button className="btn btn-primary btn-sm" onClick={apply} id="filter-apply-btn"
              style={{ height: 38 }}>
        Apply
      </button>
    </div>
  );
}
