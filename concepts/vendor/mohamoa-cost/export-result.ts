// 계산 결과를 이미지(PNG)나 PDF로 내려받기 위한 브라우저 전용 도구. 외부 라이브러리를 쓰지 않는다.
export type ExportRow = { label: string; value: string };
export type ExportSpec = {
  title: string;
  headline?: ExportRow;
  rows?: ExportRow[];
  notes?: string[];
  filename: string;
};

const WIDTH = 900;
const PAD = 48;
const FONT = '"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic",sans-serif';

function wrap(ctx: CanvasRenderingContext2D, text: string, maxWidth: number) {
  const lines: string[] = [];
  let line = '';
  for (const char of text) {
    if (ctx.measureText(line + char).width > maxWidth && line) { lines.push(line); line = char === ' ' ? '' : char; } else line += char;
  }
  if (line) lines.push(line);
  return lines;
}

/** 결과를 그린 캔버스를 만든다. 높이는 내용에 맞춰 정해진다. */
export function renderResultCanvas(spec: ExportSpec) {
  const canvas = document.createElement('canvas');
  const measure = canvas.getContext('2d');
  if (!measure) throw new Error('canvas unavailable');
  const rows = spec.rows ?? [];
  const notes = spec.notes ?? [];
  measure.font = `400 22px ${FONT}`;
  const noteLines = notes.flatMap((note) => wrap(measure, note, WIDTH - PAD * 2));
  const height = 190 + (spec.headline ? 150 : 0) + rows.length * 56 + (rows.length ? 24 : 0) + noteLines.length * 34 + 120;
  canvas.width = WIDTH; canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = '#fffaf1'; ctx.fillRect(0, 0, WIDTH, height);
  ctx.fillStyle = '#071a32'; ctx.fillRect(0, 0, WIDTH, 14);
  ctx.fillStyle = '#80591f'; ctx.font = `700 24px ${FONT}`; ctx.fillText('호반써밋 첨단3지구 계산 결과', PAD, 74);
  ctx.fillStyle = '#071a32'; ctx.font = `800 36px ${FONT}`;
  let y = 130;
  for (const line of wrap(ctx, spec.title, WIDTH - PAD * 2)) { ctx.fillText(line, PAD, y); y += 46; }
  y += 8;
  if (spec.headline) {
    ctx.fillStyle = '#10243b'; ctx.fillRect(PAD, y, WIDTH - PAD * 2, 124);
    ctx.fillStyle = '#c9a15f'; ctx.font = `700 22px ${FONT}`; ctx.fillText(spec.headline.label, PAD + 28, y + 42);
    ctx.fillStyle = '#f8fafc'; ctx.font = `800 52px ${FONT}`; ctx.fillText(spec.headline.value, PAD + 28, y + 100);
    y += 150;
  }
  ctx.font = `500 26px ${FONT}`;
  for (const row of rows) {
    ctx.fillStyle = '#334155'; ctx.textAlign = 'left'; ctx.fillText(row.label, PAD, y + 34);
    ctx.fillStyle = '#071a32'; ctx.font = `700 26px ${FONT}`; ctx.textAlign = 'right'; ctx.fillText(row.value, WIDTH - PAD, y + 34);
    ctx.font = `500 26px ${FONT}`; ctx.textAlign = 'left';
    ctx.strokeStyle = '#e2d6bf'; ctx.beginPath(); ctx.moveTo(PAD, y + 50); ctx.lineTo(WIDTH - PAD, y + 50); ctx.stroke();
    y += 56;
  }
  y += rows.length ? 24 : 0;
  ctx.fillStyle = '#64748b'; ctx.font = `400 22px ${FONT}`;
  for (const line of noteLines) { ctx.fillText(line, PAD, y + 24); y += 34; }
  ctx.fillStyle = '#80591f'; ctx.font = `600 22px ${FONT}`;
  ctx.fillText('참고용 모의 계산입니다 · 호반써밋 첨단3지구 모델하우스 안내', PAD, height - 48);
  return canvas;
}

function save(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function downloadImage(spec: ExportSpec) {
  renderResultCanvas(spec).toBlob((blob) => { if (blob) save(blob, `${spec.filename}.png`); }, 'image/png');
}

/** JPEG 한 장을 담은 한 쪽짜리 PDF(A4 세로)를 만든다. */
export function buildSinglePagePdf(jpeg: Uint8Array, imageWidth: number, imageHeight: number) {
  const pageWidth = 595, pageHeight = 842, margin = 40;
  const drawWidth = pageWidth - margin * 2;
  const drawHeight = Math.min(pageHeight - margin * 2, (drawWidth * imageHeight) / imageWidth);
  const drawY = pageHeight - margin - drawHeight;
  const encoder = new TextEncoder();
  const chunks: Uint8Array[] = [];
  const offsets: number[] = [];
  let length = 0;
  const push = (data: Uint8Array | string) => { const bytes = typeof data === 'string' ? encoder.encode(data) : data; chunks.push(bytes); length += bytes.length; };
  const object = (id: number, body: string, stream?: Uint8Array) => {
    offsets[id] = length;
    push(`${id} 0 obj\n${body}`);
    if (stream) { push('\nstream\n'); push(stream); push('\nendstream'); }
    push('\nendobj\n');
  };
  push('%PDF-1.4\n');
  object(1, '<< /Type /Catalog /Pages 2 0 R >>');
  object(2, '<< /Type /Pages /Kids [3 0 R] /Count 1 >>');
  object(3, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /XObject << /Im0 5 0 R >> >> /Contents 4 0 R >>`);
  const content = encoder.encode(`q ${drawWidth.toFixed(2)} 0 0 ${drawHeight.toFixed(2)} ${margin} ${drawY.toFixed(2)} cm /Im0 Do Q`);
  object(4, `<< /Length ${content.length} >>`, content);
  object(5, `<< /Type /XObject /Subtype /Image /Width ${imageWidth} /Height ${imageHeight} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${jpeg.length} >>`, jpeg);
  const xrefAt = length;
  push(`xref\n0 6\n0000000000 65535 f \n${[1, 2, 3, 4, 5].map((id) => `${String(offsets[id]).padStart(10, '0')} 00000 n \n`).join('')}`);
  push(`trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xrefAt}\n%%EOF\n`);
  const out = new Uint8Array(length);
  let position = 0;
  for (const chunk of chunks) { out.set(chunk, position); position += chunk.length; }
  return out;
}

export function downloadPdf(spec: ExportSpec) {
  const canvas = renderResultCanvas(spec);
  canvas.toBlob(async (blob) => {
    if (!blob) return;
    const buffer = new Uint8Array(await blob.arrayBuffer());
    const pdf = buildSinglePagePdf(buffer, canvas.width, canvas.height);
    save(new Blob([pdf.buffer as ArrayBuffer], { type: 'application/pdf' }), `${spec.filename}.pdf`);
  }, 'image/jpeg', 0.92);
}
