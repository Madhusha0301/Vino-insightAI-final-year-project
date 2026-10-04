import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// Brand colours (RGB arrays for jsPDF)
const WINE = [123, 29, 46];       // #7B1D2E
const WINE_DARK = [74, 15, 26];   // #4A0F1A
const GOLD = [201, 168, 76];      // #C9A84C
const INK = [42, 26, 31];         // #2A1A1F
const MUTED = [107, 90, 95];      // #6B5A5F
const LIGHT_BG = [250, 247, 243]; // #FAF7F3
const WHITE = [255, 255, 255];

function drawLogo(doc, x, y) {
  // Simple vector "wine glass" mark + wordmark — no external image file needed.
  doc.setDrawColor(...GOLD);
  doc.setLineWidth(0.6);
  // glass bowl
  doc.ellipse(x + 4, y + 3, 3.2, 2.6, 'S');
  doc.line(x + 4, y + 5.4, x + 4, y + 9);
  doc.line(x + 1.5, y + 9, x + 6.5, y + 9);
  // wordmark
  doc.setTextColor(...WHITE);
  doc.setFont('times', 'bold');
  doc.setFontSize(17);
  doc.text('VinoInsight', x + 12, y + 5);
  doc.setFontSize(9);
  doc.setTextColor(...GOLD);
  doc.setFont('helvetica', 'normal');
  doc.text('A I', x + 12, y + 10.5);
}

function sectionHeader(doc, title, y) {
  doc.setFillColor(...LIGHT_BG);
  doc.rect(14, y, 182, 8, 'F');
  doc.setDrawColor(...GOLD);
  doc.setLineWidth(0.4);
  doc.line(14, y + 8, 196, y + 8);
  doc.setTextColor(...WINE);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(10.5);
  doc.text(title.toUpperCase(), 17, y + 5.6);
  return y + 8;
}

// Unit labels use "dm3"/"cm3" (plain ASCII), not the Unicode superscript
// "³" (U+00B3) — project audit fix, found via PDF export screenshot
// verification: jsPDF's standard fonts don't render that glyph, so it was
// silently dropped in the exported PDF (e.g. "Alcohol (g/dm )" instead of
// "Alcohol (g/dm³)"). The on-screen Results page correctly renders ³ via
// the browser's own font stack, so this only affected the PDF export.
const inputLabels = {
  fixed_acidity: 'Fixed Acidity (g/dm3)',
  volatile_acidity: 'Volatile Acidity (g/dm3)',
  citric_acid: 'Citric Acid (g/dm3)',
  residual_sugar: 'Residual Sugar (g/dm3)',
  chlorides: 'Chlorides (g/dm3)',
  free_sulfur_dioxide: 'Free Sulfur Dioxide (mg/dm3)',
  total_sulfur_dioxide: 'Total Sulfur Dioxide (mg/dm3)',
  density: 'Density (g/cm3)',
  ph: 'pH',
  sulphates: 'Sulphates (g/dm3)',
  alcohol: 'Alcohol (% vol)',
};

/**
 * Generates a professional lab-report style PDF directly via jsPDF
 * drawing calls (no page screenshot / html2canvas) — guarantees crisp
 * text and consistent layout regardless of the app's on-screen theme.
 */
export function generateLabReportPDF(result) {
  const doc = new jsPDF('p', 'mm', 'a4');
  const pageWidth = 210;

  // ===== HEADER BAND =====
  doc.setFillColor(...WINE_DARK);
  doc.rect(0, 0, pageWidth, 32, 'F');
  drawLogo(doc, 14, 8);

  doc.setTextColor(...WHITE);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9);
  doc.text('WINE ANALYSIS CERTIFICATE', pageWidth - 14, 12, { align: 'right' });
  doc.setFontSize(8);
  doc.setTextColor(230, 220, 210);
  const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' });
  doc.text(`Generated: ${today}`, pageWidth - 14, 18, { align: 'right' });
  doc.text(`Report ID: VIA-${Date.now().toString().slice(-8)}`, pageWidth - 14, 23, { align: 'right' });

  let y = 40;

  // ===== TITLE =====
  doc.setTextColor(...INK);
  doc.setFont('times', 'bold');
  doc.setFontSize(16);
  doc.text(result.aroma_profile || 'Wine Sample Analysis', 14, y);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(9.5);
  doc.setTextColor(...MUTED);
  y += 6;
  doc.text(
    `Predicted quality ${result.quality_score}/10  ·  ${result.quality_range} quality range  ·  ${result.price_range}`,
    14, y
  );
  y += 10;

  // ===== SUMMARY RESULT CARDS (as a table) =====
  y = sectionHeader(doc, 'Prediction Summary', y);
  autoTable(doc, {
    startY: y + 3,
    theme: 'grid',
    styles: { font: 'helvetica', fontSize: 9.5, textColor: INK, lineColor: [237, 227, 221], cellPadding: 3 },
    headStyles: { fillColor: WINE, textColor: WHITE, fontStyle: 'bold' },
    columnStyles: { 0: { fontStyle: 'bold', cellWidth: 55 } },
    head: [['Metric', 'Predicted Result']],
    body: [
      ['Quality Score', `${result.quality_score} / 10`],
      ['Quality Range', result.quality_range],
      ['Price Range', result.price_range],
      ['Aroma Profile', result.aroma_profile],
      ['Consumer Segment', result.consumer_segment],
    ],
    margin: { left: 14, right: 14 },
  });
  y = doc.lastAutoTable.finalY + 10;

  // ===== INPUT CHEMISTRY TABLE =====
  if (result.inputs) {
    y = sectionHeader(doc, 'Physicochemical Properties (Lab Input)', y);
    const rows = Object.entries(result.inputs)
      .filter(([k]) => inputLabels[k])
      .map(([k, v]) => [inputLabels[k], String(v)]);
    autoTable(doc, {
      startY: y + 3,
      theme: 'striped',
      styles: { font: 'helvetica', fontSize: 9, textColor: INK, cellPadding: 2.6 },
      headStyles: { fillColor: [90, 20, 32], textColor: WHITE, fontStyle: 'bold' },
      alternateRowStyles: { fillColor: LIGHT_BG },
      columnStyles: { 1: { halign: 'right', fontStyle: 'bold' } },
      head: [['Property', 'Measured Value']],
      body: rows,
      margin: { left: 14, right: 14 },
    });
    y = doc.lastAutoTable.finalY + 10;
  }

  // Page break if needed
  if (y > 230) { doc.addPage(); y = 20; }

  // ===== SHAP FEATURE IMPORTANCE =====
  if (result.shap_values) {
    y = sectionHeader(doc, 'Feature Impact on Predicted Quality', y);
    const shapRows = Object.entries(result.shap_values)
      .filter(([k]) => k !== 'is_red')
      .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
      .map(([k, v]) => [
        (inputLabels[k] || k).replace(/\s*\(.*?\)/, ''),
        v > 0 ? `+${v.toFixed(3)}` : v.toFixed(3),
        v > 0 ? 'Increases quality' : 'Decreases quality',
      ]);
    autoTable(doc, {
      startY: y + 3,
      theme: 'grid',
      styles: { font: 'helvetica', fontSize: 9, textColor: INK, cellPadding: 2.6 },
      headStyles: { fillColor: WINE, textColor: WHITE, fontStyle: 'bold' },
      columnStyles: {
        1: { halign: 'center', cellWidth: 30 },
        2: { cellWidth: 55 },
      },
      head: [['Property', 'SHAP Value', 'Effect']],
      body: shapRows,
      margin: { left: 14, right: 14 },
      didParseCell: (data) => {
        if (data.section === 'body' && data.column.index === 1) {
          const val = parseFloat(data.cell.raw);
          data.cell.styles.textColor = val >= 0 ? [46, 125, 91] : [166, 26, 48];
          data.cell.styles.fontStyle = 'bold';
        }
      },
    });
    y = doc.lastAutoTable.finalY + 10;
  }

  if (y > 230) { doc.addPage(); y = 20; }

  // ===== RECOMMENDATIONS =====
  if (result.recommendations?.length) {
    y = sectionHeader(doc, 'Quality Improvement Recommendations', y);
    y += 6;
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9.5);
    doc.setTextColor(...INK);
    result.recommendations.forEach((rec) => {
      const lines = doc.splitTextToSize(rec, 170);
      doc.setFillColor(...GOLD);
      doc.circle(16.5, y - 1.3, 0.9, 'F');
      doc.text(lines, 20, y);
      y += lines.length * 5 + 3;
    });
    y += 4;
  }

  if (y > 250) { doc.addPage(); y = 20; }

  // ===== FOOTER =====
  const footerY = 285;
  doc.setDrawColor(...GOLD);
  doc.setLineWidth(0.3);
  doc.line(14, footerY - 6, 196, footerY - 6);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(7.5);
  doc.setTextColor(...MUTED);
  doc.text('VinoInsight AI — Chemistry-Based Wine Analysis', 14, footerY);
  doc.text('This report is AI-generated from physicochemical inputs and is intended as a decision-support tool.', 14, footerY + 4);

  doc.save(`VinoInsight_LabReport_${Date.now()}.pdf`);
}
