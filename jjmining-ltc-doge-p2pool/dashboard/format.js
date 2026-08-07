(function(root) {
  const DIFFICULTY_SUFFIXES = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'];

  function formatDifficulty(value) {
    if (value === null || value === undefined || typeof value === 'boolean' || value === '') return '—';
    const number = typeof value === 'number' ? value : Number(value);
    if (!Number.isFinite(number) || number < 0) return '—';
    if (number === 0) return '0 diff';

    let scaled = number;
    let suffixIndex = 0;
    while (scaled >= 1000 && suffixIndex < DIFFICULTY_SUFFIXES.length - 1) {
      scaled /= 1000;
      suffixIndex += 1;
    }

    const digits = scaled >= 100 ? 1 : 2;
    const suffix = DIFFICULTY_SUFFIXES[suffixIndex];
    return scaled.toFixed(digits) + (suffix ? ' ' + suffix : '') + ' diff';
  }

  root.formatDifficulty = formatDifficulty;
  if (typeof module !== 'undefined') module.exports = {formatDifficulty};
})(typeof globalThis !== 'undefined' ? globalThis : this);
