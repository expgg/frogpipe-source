/**
 * =========================================================================
 *         FROGPIPE — GOOGLE SHEETS LIVE ENGINE v2.0 (MARK 2)
 *                 Architected & Engineered by Al Hossain Rifat
 *                          Portfolio: https://r1fat.pages.dev
 * =========================================================================
 * Features:
 *   1. Auto-Creates an Executive Multi-Tab Google Spreadsheet for any audit session.
 *   2. Generates the 10 Technical Screaming Frog Tabs with 100% full data preservation.
 *   3. Auto-Formats the "Competitors Analysis" tab:
 *      - Row 2: Client Website (Soft Mint Green highlight #D1FAE5).
 *      - Rows 3-7: Top 5 Rivals (Soft Rose Red highlight #FEE2E2).
 *   4. Executive Dark Header Bar (#0F172A), Sticky Frozen Rows, & Text Clipping (WrapStrategy.CLIP).
 *   5. Intelligent Column Width Clamping (Max 320px) preventing URL text bleed.
 * =========================================================================
 */

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    service: "FrogPipe Google Sheets Live Engine v2.0",
    architect: "Al Hossain Rifat",
    portfolio: "https://r1fat.pages.dev",
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const domain = (data.domain || "Target Website").trim();
    const spreadsheetTitle = data.title || ("SEO Audit & Competitors Analysis for " + domain);
    const tabsData = data.tabs || {};

    let sheetId = data.sheet_id || null;
    let ss;

    // 1. Target or create the spreadsheet
    if (!sheetId) {
      ss = SpreadsheetApp.create(spreadsheetTitle);
      sheetId = ss.getId();
    } else {
      try {
        ss = SpreadsheetApp.openById(sheetId);
      } catch (err) {
        ss = SpreadsheetApp.create(spreadsheetTitle);
        sheetId = ss.getId();
      }
    }

    const defaultSheet = ss.getSheetByName("Sheet1");

    // Preferred tab order matching teacher's requirements
    const tabOrder = [
      "Issues",
      "H1",
      "H2",
      "Meta Tags + Meta description",
      "Content",
      "ALL page Titles",
      "URLs",
      "Images",
      "Search Console Status",
      "Canonicals",
      "Competitors Analysis"
    ];

    // Collect all tab names
    const allTabNames = [];
    tabOrder.forEach(function(t) {
      if (tabsData[t] || t === "Competitors Analysis") {
        allTabNames.push(t);
      }
    });

    // Add any extra tabs in payload not in default tabOrder
    Object.keys(tabsData).forEach(function(t) {
      if (allTabNames.indexOf(t) === -1) {
        allTabNames.push(t);
      }
    });

    // 2. Build and populate each sheet tab
    allTabNames.forEach(function(tabName) {
      let sheet = ss.getSheetByName(tabName);
      if (!sheet) {
        sheet = ss.insertSheet(tabName);
      } else {
        sheet.clear();
      }

      if (tabName === "Competitors Analysis") {
        formatCompetitorsTab(sheet, tabsData[tabName], domain);
      } else if (tabsData[tabName] && tabsData[tabName].length > 0) {
        formatStandardTab(sheet, tabsData[tabName]);
      }
    });

    // 3. Remove default empty Sheet1 if present
    if (defaultSheet && ss.getSheets().length > 1) {
      try {
        ss.deleteSheet(defaultSheet);
      } catch (e) {
        // Ignore if only 1 sheet
      }
    }

    // Set first tab as active
    ss.setActiveSheet(ss.getSheets()[0]);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      sheet_id: sheetId,
      sheet_url: ss.getUrl(),
      total_tabs: ss.getSheets().length
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Formats standard audit tabs with executive dark header, text clipping, and zebra stripes.
 */
function formatStandardTab(sheet, rows) {
  if (!rows || rows.length === 0) return;

  const numRows = rows.length;
  const numCols = rows[0].length;

  // Insert all data at once for high-speed batch execution
  const range = sheet.getRange(1, 1, numRows, numCols);
  range.setValues(rows);

  // 1. Header Styling (Row 1)
  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange.setBackground("#0F172A"); // Dark Slate
  headerRange.setFontColor("#F8FAFC"); // Crisp Off-White
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10);
  headerRange.setHorizontalAlignment("left");
  headerRange.setVerticalAlignment("middle");
  sheet.setRowHeight(1, 34);
  sheet.setFrozenRows(1);

  // 2. Data Rows Styling
  if (numRows > 1) {
    const dataRange = sheet.getRange(2, 1, numRows - 1, numCols);
    dataRange.setFontSize(10);
    dataRange.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);
    dataRange.setVerticalAlignment("middle");

    // Zebra striping
    for (let r = 2; r <= numRows; r++) {
      const rowRange = sheet.getRange(r, 1, 1, numCols);
      if (r % 2 === 0) {
        rowRange.setBackground("#FFFFFF");
      } else {
        rowRange.setBackground("#F8FAFC");
      }
      sheet.setRowHeight(r, 26);
    }
  }

  // 3. Optimize Column Widths (clamp maximum width to 320px)
  for (let c = 1; c <= numCols; c++) {
    sheet.autoResizeColumn(c);
    const w = sheet.getColumnWidth(c);
    if (w < 90) {
      sheet.setColumnWidth(c, 100);
    } else if (w > 320) {
      sheet.setColumnWidth(c, 320);
    }
  }
}

/**
 * Formats the Competitors Analysis tab per the teacher's exact grading rubric:
 * Row 2 (Client Site): Soft Green (#D1FAE5)
 * Rows 3-7 (5 Rivals): Soft Red (#FEE2E2)
 */
function formatCompetitorsTab(sheet, customData, clientDomain) {
  const defaultHeaders = [
    "Website",
    "DA",
    "PA",
    "SS",
    "Ranking Keywords ( Moz )",
    "DR",
    "Backlink",
    "Linking Websites",
    "Website Traffic",
    "Traffic Values"
  ];

  let rows = [];
  if (customData && customData.length > 0) {
    rows = customData;
  } else {
    // Scaffold default template structure
    rows.push(defaultHeaders);
    rows.push([clientDomain.indexOf("http") === 0 ? clientDomain : "https://" + clientDomain, "-", "-", "-", "-", "-", "-", "-", "-", "-"]);
    for (let i = 1; i <= 5; i++) {
      rows.push(["https://competitor-" + i + ".com (Pending Recon)", "-", "-", "-", "-", "-", "-", "-", "-", "-"]);
    }
  }

  const numRows = rows.length;
  const numCols = rows[0].length;

  const range = sheet.getRange(1, 1, numRows, numCols);
  range.setValues(rows);

  // 1. Header Styling
  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange.setBackground("#0F172A");
  headerRange.setFontColor("#FFFFFF");
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10);
  headerRange.setHorizontalAlignment("center");
  sheet.setRowHeight(1, 36);
  sheet.setFrozenRows(1);

  // 2. Row 2: Client Website (Light Green Highlight)
  if (numRows >= 2) {
    const clientRange = sheet.getRange(2, 1, 1, numCols);
    clientRange.setBackground("#D1FAE5"); // Light Green
    clientRange.setFontColor("#065F46"); // Dark Emerald Green
    clientRange.setFontWeight("bold");
    clientRange.setFontSize(10);
    sheet.setRowHeight(2, 30);
  }

  // 3. Rows 3-7: Competitors (Light Red Highlight)
  if (numRows >= 3) {
    const rivalsCount = Math.min(5, numRows - 2);
    const rivalsRange = sheet.getRange(3, 1, rivalsCount, numCols);
    rivalsRange.setBackground("#FEE2E2"); // Light Red/Pink
    rivalsRange.setFontColor("#991B1B"); // Dark Maroon Red
    rivalsRange.setFontSize(10);
    for (let r = 3; r <= 2 + rivalsCount; r++) {
      sheet.setRowHeight(r, 28);
    }
  }

  // Auto-resize columns
  for (let c = 1; c <= numCols; c++) {
    sheet.autoResizeColumn(c);
    const w = sheet.getColumnWidth(c);
    if (w < 110) sheet.setColumnWidth(c, 120);
    if (w > 320) sheet.setColumnWidth(c, 320);
  }
}
