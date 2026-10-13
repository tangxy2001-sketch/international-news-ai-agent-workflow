const { test } = require('node:test');
const assert = require('node:assert/strict');
const { validateArticles } = require('../skills/media-present/scripts/validate');
const sample = require('../examples/demo/articles.json');
const copy = () => JSON.parse(JSON.stringify(sample));
test('accept valid Unicode text and quoted text', () => {
  const a = copy(); a[0].paragraphs[0].text = '保留 "原话" 与中文引号“原话”';
  assert.equal(validateArticles(a), a);
});
for (const [name, mutate] of [
  ['duplicate URL', a => a[1].url = a[0].url],
  ['unordered footnote', a => a[0].footnote = 3],
  ['invalid URL scheme', a => a[0].url = 'file:///secret'],
  ['missing highlight', a => a[0].paragraphs.forEach(p => p.highlight = false)],
  ['truncated translation', a => a[0].truncated = true],
  ['damaged encoding', a => a[0].title_cn = '\uFFFD'],
  ['invalid paragraph', a => a[0].paragraphs = [{text:'',highlight:true}]],
]) test(`reject ${name}`, () => { const a = copy(); mutate(a); assert.throws(() => validateArticles(a)); });
