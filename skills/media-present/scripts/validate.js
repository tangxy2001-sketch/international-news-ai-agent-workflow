'use strict';
function validateArticles(articles) {
  if (!Array.isArray(articles) || !articles.length) throw new Error('Expected a non-empty article array');
  const seen = new Set();
  articles.forEach((a, i) => {
    if (!a || typeof a !== 'object' || a.footnote !== i + 1) throw new Error('Footnotes must be consecutive and ordered from 1');
    for (const field of ['media_cn', 'title_cn', 'url']) {
      if (typeof a[field] !== 'string' || !a[field].trim()) throw new Error(`Missing ${field}`);
    }
    const url = new URL(a.url);
    if (!['http:', 'https:'].includes(url.protocol)) throw new Error('Source must be HTTP(S)');
    if (seen.has(a.url)) throw new Error('Duplicate source URL');
    seen.add(a.url);
    if (a.truncated !== undefined && a.truncated !== false) throw new Error('Truncated translation cannot be delivered as complete');
    if (!Array.isArray(a.paragraphs) || !a.paragraphs.length) throw new Error('Missing paragraphs');
    for (const p of a.paragraphs) {
      if (!p || typeof p.text !== 'string' || !p.text.trim() || typeof p.highlight !== 'boolean') throw new Error('Invalid paragraph');
    }
    if (!a.paragraphs.some(p => p.highlight)) throw new Error('Missing cited paragraph highlight');
    if (JSON.stringify(a).includes('\uFFFD')) throw new Error('Unicode replacement character found');
  });
  return articles;
}
module.exports = { validateArticles };
