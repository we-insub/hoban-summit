'use client';

import { downloadImage, downloadPdf, type ExportSpec } from './export-result';

/** 계산 결과를 이미지(PNG)나 PDF로 저장하는 버튼 묶음. */
export function ResultExport({ spec, disabled = false }: { spec: ExportSpec; disabled?: boolean }) {
  return <div className="result-export" role="group" aria-label="계산 결과 저장">
    <button type="button" onClick={() => downloadImage(spec)} disabled={disabled}>이미지 저장</button>
    <button type="button" onClick={() => downloadPdf(spec)} disabled={disabled}>PDF 저장</button>
  </div>;
}
