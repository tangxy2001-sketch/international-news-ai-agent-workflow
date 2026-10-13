const { Document, Packer, Paragraph, TextRun, ExternalHyperlink } = require('docx');
const fs = require('fs');
const { validateArticles } = require('./validate');

// Usage: node generate.js <articles.json> <output.docx>
const inputPath = process.argv[2] || 'articles.json';
const outputPath = process.argv[3] || '素材呈现.docx';

let articles;
try {
  articles = validateArticles(JSON.parse(fs.readFileSync(inputPath, 'utf8')));
} catch (error) {
  console.error(`Invalid input: ${error.message}`);
  process.exit(1);
}
if (fs.existsSync(outputPath)) {
  console.error('Output already exists; choose a new path or archive the old output.');
  process.exit(1);
}

const children = [];

articles.forEach((article, index) => {
  // Spacing between articles
  if (index > 0) {
    children.push(new Paragraph({ spacing: { before: 400 } }));
  }

  // 1. Title: blue text — "序号.媒体名-标题中文"
  children.push(new Paragraph({
    spacing: { after: 100 },
    children: [
      new TextRun({
        text: `${article.footnote}.${article.media_cn}-${article.title_cn}`,
        color: '0000FF',
        font: 'SimSun',
        size: 21, // 10.5pt
      })
    ]
  }));

  // 2. URL as clickable hyperlink
  children.push(new Paragraph({
    spacing: { after: 100 },
    children: [
      new ExternalHyperlink({
        link: article.url,
        children: [
          new TextRun({
            text: article.url,
            style: 'Hyperlink',
            font: 'SimSun',
            size: 21,
          })
        ]
      })
    ]
  }));

  // 3. Body paragraphs with optional yellow highlight
  article.paragraphs.forEach(para => {
    if (!para.text || para.text.trim() === '') return;

    const runProps = {
      text: para.text,
      font: 'SimSun',
      size: 21,
    };

    if (para.highlight) {
      runProps.highlight = 'yellow';
    }

    children.push(new Paragraph({
      spacing: { after: 60 },
      children: [new TextRun(runProps)]
    }));
  });
});

const doc = new Document({
  styles: {
    default: {
      document: {
        run: {
          font: 'SimSun',
          size: 21,
        }
      }
    }
  },
  sections: [{
    properties: {
      page: {
        size: {
          width: 11906, // A4
          height: 16838
        },
        margin: {
          top: 1440,
          right: 1440,
          bottom: 1440,
          left: 1440
        }
      }
    },
    children: children
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer, { flag: 'wx' });
  console.log(`Generated: ${outputPath}`);
  console.log(`Articles: ${articles.length}`);
  console.log(`Total paragraphs: ${articles.reduce((sum, a) => sum + a.paragraphs.length, 0)}`);
}).catch(error => {
  console.error(`Generation failed: ${error.message}`);
  process.exitCode = 1;
});
