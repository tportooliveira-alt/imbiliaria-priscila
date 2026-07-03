import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const pacoteDir = path.join(
  root,
  "_marketing_ia",
  "criativos",
  "2026-07-03-pacote-instagram-make",
);
const csvPath = path.join(pacoteDir, "fila-make-google-sheets-segura.csv");
const outputDir = path.join(pacoteDir, "make-operacao");
const xlsxPath = path.join(outputDir, "fila-instagram-priscila-make.xlsx");
const previewPath = path.join(outputDir, "preview-fila-instagram.png");

await fs.mkdir(outputDir, { recursive: true });

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Fila Instagram" });
const fila = workbook.worksheets.getItem("Fila Instagram");

fila.showGridLines = false;
fila.freezePanes.freezeRows(1);
fila.freezePanes.freezeColumns(2);

const totalRows = 28;
const totalCols = 21;

fila.getRange("A1:U1").format = {
  fill: "#16284B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  borders: { preset: "inside", style: "thin", color: "#D9D9D9" },
};
fila.getRange("A2:U28").format = {
  font: { color: "#1F2937" },
  borders: { preset: "inside", style: "thin", color: "#E5E7EB" },
};
fila.getRange("A1:U1").format.rowHeightPx = 34;
fila.getRange("A2:U28").format.rowHeightPx = 68;
fila.getRange("G2:J28").format.wrapText = true;
fila.getRange("A2:F28").format.wrapText = false;
fila.getRange("K2:K28").format.numberFormat = "yyyy-mm-dd hh:mm";
fila.getRange("S2:S28").format.numberFormat = "0";

const widths = [
  ["A1:A28", 150],
  ["B1:B28", 70],
  ["C1:C28", 145],
  ["D1:D28", 90],
  ["E1:E28", 105],
  ["F1:F28", 260],
  ["G1:G28", 360],
  ["H1:H28", 340],
  ["I1:I28", 330],
  ["J1:J28", 330],
  ["K1:K28", 170],
  ["L1:L28", 120],
  ["M1:M28", 260],
  ["N1:N28", 230],
  ["O1:O28", 240],
  ["P1:P28", 120],
  ["Q1:Q28", 140],
  ["R1:R28", 220],
  ["S1:S28", 90],
  ["T1:T28", 170],
  ["U1:U28", 170],
];
for (const [range, width] of widths) {
  fila.getRange(range).format.columnWidthPx = width;
}

fila.getRange("C2:C28").dataValidation = {
  rule: {
    type: "list",
    values: ["PENDENTE_REVISAO", "APROVADO", "PUBLICADO", "ERRO"],
  },
};
fila.getRange("D2:D28").dataValidation = {
  rule: {
    type: "list",
    values: ["instagram"],
  },
};
fila.getRange("E2:E28").dataValidation = {
  rule: {
    type: "list",
    values: ["foto", "carrossel", "story"],
  },
};

fila.tables.add(`A1:U${totalRows}`, true, "FilaInstagramMake");
fila.getRange("A1:U1").format = {
  fill: "#16284B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  borders: { preset: "inside", style: "thin", color: "#D9D9D9" },
};

const guia = workbook.worksheets.add("Como usar no Make");
guia.showGridLines = false;
guia.getRange("A1:F1").merge();
guia.getRange("A1").values = [["Operacao Make - Priscila Vasconcelos Imoveis"]];
guia.getRange("A1:F1").format = {
  fill: "#16284B",
  font: { bold: true, color: "#FFFFFF" },
};
guia.getRange("A3:B12").values = [
  ["Objetivo", "Fila segura para o Make publicar somente o que estiver aprovado."],
  ["Primeiro modulo", "Google Sheets: Watch/Search rows nesta planilha."],
  ["Filtro principal", "status = APROVADO e publish_at <= agora."],
  ["Rota foto", "Instagram for Business: Create a photo post usando media_url + legenda."],
  ["Rota carrossel", "Instagram for Business: Create a carousel post usando media_urls_json ou media_urls_pipe."],
  ["Depois de publicar", "Atualizar status para PUBLICADO, preencher post_id e publicado_em."],
  ["Se der erro", "Atualizar status para ERRO, preencher erro e avisar Thiago."],
  ["Trava noticia", "Noticia precisa ter fonte_url ou fonte_nome conferida."],
  ["Trava imovel", "Imovel precisa ter slug ativo na carteira."],
  ["Observacao", "Make precisa acessar as imagens por URL HTTPS publica."],
];
guia.getRange("A3:A12").format = {
  fill: "#F7F3EA",
  font: { bold: true, color: "#16284B" },
};
guia.getRange("B3:B12").format = { wrapText: true };
guia.getRange("A3:B12").format.borders = { preset: "inside", style: "thin", color: "#E5E7EB" };
guia.getRange("A1:F12").format.font = { color: "#1F2937" };
guia.getRange("A1").format.font = { bold: true, color: "#FFFFFF" };
guia.getRange("A1:F1").format.rowHeightPx = 32;
guia.getRange("A3:B12").format.rowHeightPx = 42;
guia.getRange("A1:A12").format.columnWidthPx = 180;
guia.getRange("B1:B12").format.columnWidthPx = 620;

const inspect = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 6000,
  tableMaxRows: 4,
  tableMaxCols: 8,
});
console.log(inspect.ndjson);

const preview = await workbook.render({
  sheetName: "Fila Instagram",
  range: "A1:J12",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(xlsxPath);

console.log(JSON.stringify({ xlsxPath, previewPath, rows: totalRows - 1, cols: totalCols }));
