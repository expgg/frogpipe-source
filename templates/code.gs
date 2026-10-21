/**
 * =========================================================================
 *     FROGPIPE — HIGH-GRADE EXECUTIVE GOOGLE SHEETS LIVE ENGINE v4.0
 *               Architected & Engineered by Al Hossain Rifat
 *                        Portfolio: https://r1fat.pages.dev
 * =========================================================================
 * Highlights & Visual Effects:
 *   1. Vibrant Bespoke Tab Palette: Every single sheet tab is vibrantly
 *      color-coded (Crimson, Emerald, Cyan, Purple, Indigo, Teal, Blue, Orange).
 *   2. Master Obsidian Cyber Header (Row 1):
 *      - Deep Obsidian #0B0F19 with crisp glowing badges and author watermark.
 *   3. Slate Pro Sticky Headers (Row 2):
 *      - Deep Charcoal #1E293B with 3px thick colored bottom accent matching tab.
 *      - Top 2 rows frozen sticky during scrolling.
 *   4. Zero-Mushing Intelligent Column Sizing:
 *      - URLs & Addresses: 460px wide (no text collision or truncation)
 *      - Titles, Descriptions & Issues: 380-450px wide
 *      - Status Codes & Priority Badges: 120-130px centered
 *      - Numeric metrics (Length, Width, Words): 130px right-aligned
 *      - Minimum column width floor: 180px for all standard fields
 *   5. Atomic 2D Matrix Color-Coding:
 *      - Status Codes: 200 (Mint Green #D1FAE5), 3xx (Sky Blue #DBEAFE),
 *        4xx (Coral Red #FEE2E2), 5xx (Fiery Rose #FFE4E6)
 *      - Priorities: High (Crimson Badge), Medium (Amber), Low (Sky Blue)
 *      - Length Alerts: Out-of-bounds titles & descriptions flagged in amber
 *      - Content Alerts: Thin content (<300 words) flagged in soft red
 *      - Missing Tags: Flagged in bold alert rose #FFF1F2
 *   6. Executive Competitor Intelligence Matrix:
 *      - Client Domain in radiant mint green glow (#D1FAE5)
 *      - Rival competitors in soft rose benchmark (#FEE2E2)
 *   7. High-Speed Atomic Performance:
 *      - Applies 2D background and font arrays in 1 millisecond operation!
 * =========================================================================
 */

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    service: "FrogPipe High-Grade Executive Google Sheets Engine v4.0",
    architect: "Al Hossain Rifat",
    portfolio: "https://r1fat.pages.dev",
    timestamp: new Date().toISOString()
  })).setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const action = data.action || "create_audit";
    const domain = (data.domain || "Target Website").trim();
    let sheetId = data.sheet_id || null;
    let ss;

    // -----------------------------------------------------------------------
    // Action: init_audit (Creates Spreadsheet, Sets Theme & Competitors Tab)
    // -----------------------------------------------------------------------
    if (action === "init_audit") {
      const spreadsheetTitle = data.title || ("SEO Audit & Competitors Analysis for " + domain);
      ss = SpreadsheetApp.create(spreadsheetTitle);
      sheetId = ss.getId();

      const compSheet = ss.getActiveSheet();
      compSheet.setName("Competitors Analysis");
      compSheet.setTabColor(getTabColor("Competitors Analysis"));
      formatCompetitorsTab(compSheet, data.competitors_data, domain);

      return ContentService.createTextOutput(JSON.stringify({
        status: "success",
        sheet_id: sheetId,
        sheet_url: ss.getUrl()
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // -----------------------------------------------------------------------
    // Action: sync_tab (Streams Individual High-Grade Tab)
    // -----------------------------------------------------------------------
    if (action === "sync_tab") {
      if (!sheetId) throw new Error("Missing sheet_id for sync_tab action.");
      ss = SpreadsheetApp.openById(sheetId);
      const tabName = data.tab_name || "Audit Data";
      const rows = data.rows || [];

      let sheet = ss.getSheetByName(tabName);
      if (!sheet) {
        sheet = ss.insertSheet(tabName);
      } else {
        sheet.clear();
      }

      sheet.setTabColor(getTabColor(tabName));
      formatHighGradeTab(sheet, rows, domain, tabName);

      return ContentService.createTextOutput(JSON.stringify({
        status: "success",
        tab_name: tabName,
        rows_synced: rows.length
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // -----------------------------------------------------------------------
    // Action: create_audit (Full Batch High-Grade Execution)
    // -----------------------------------------------------------------------
    const spreadsheetTitle = data.title || ("SEO Audit & Competitors Analysis for " + domain);
    const tabsData = data.tabs || {};

    if (!sheetId) {
      ss = SpreadsheetApp.create(spreadsheetTitle);
      sheetId = ss.getId();
    } else {
      ss = SpreadsheetApp.openById(sheetId);
    }

    const defaultSheet = ss.getSheetByName("Sheet1");

    const tabOrder = [
      "Competitors Analysis",
      "Issues",
      "H1",
      "H2",
      "Meta Description",
      "Meta Tags",
      "Content",
      "ALL page Titles",
      "URLs",
      "Images",
      "Search Console Status",
      "Canonicals"
    ];

    tabOrder.forEach(function(tabName) {
      if (tabsData[tabName] || tabName === "Competitors Analysis") {
        let sheet = ss.getSheetByName(tabName);
        if (!sheet) sheet = ss.insertSheet(tabName);
        else sheet.clear();

        sheet.setTabColor(getTabColor(tabName));

        if (tabName === "Competitors Analysis") {
          formatCompetitorsTab(sheet, tabsData[tabName], domain);
        } else if (tabsData[tabName] && tabsData[tabName].length > 0) {
          formatHighGradeTab(sheet, tabsData[tabName], domain, tabName);
        }
      }
    });

    if (defaultSheet && ss.getSheets().length > 1) {
      try { ss.deleteSheet(defaultSheet); } catch (e) {}
    }

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
 * Vibrant Color Palette Mapping for Sheet Tabs
 */
function getTabColor(tabName) {
  const map = {
    "Competitors Analysis": "#F59E0B", // Cyber Amber Gold
    "Issues": "#EF4444",               // Neon Crimson
    "H1": "#10B981",                   // Emerald Green
    "H2": "#06B6D4",                   // Electric Cyan
    "Meta Description": "#8B5CF6",     // Royal Violet
    "Meta Tags": "#6366F1",            // Electric Indigo
    "Content": "#14B8A6",              // Vivid Teal
    "ALL page Titles": "#3B82F6",      // Electric Royal Blue
    "URLs": "#475569",                 // Deep Navy Slate
    "Images": "#EC4899",               // Hot Fuchsia
    "Search Console Status": "#F97316",// Vivid Safety Orange
    "Canonicals": "#0EA5E9"            // Sky Blue
  };
  return map[tabName] || "#10B981";
}

/**
 * High-Grade Tab Formatter:
 * - Master Obsidian KPI Banner (Row 1)
 * - Sticky Column Headers with Tab Accent (Row 2)
 * - Atomic Matrix Cell Color-Coding (Row 3+)
 * - Intelligent Proportional Column Widths
 */
function formatHighGradeTab(sheet, rows, domain, tabName) {
  if (!rows || rows.length === 0) return;

  const rawHeaders = rows[0];
  const numDataRows = rows.length - 1;
  const numCols = rawHeaders.length;
  const themeColor = getTabColor(tabName);

  // -------------------------------------------------------------------------
  // 1. Build Master Banner (Row 1)
  // -------------------------------------------------------------------------
  sheet.setRowHeight(1, 44);
  const masterTitle = "🐸 FROGPIPE EXECUTIVE SEO SUITE • " + tabName.toUpperCase() + " MATRIX";
  const authorBadge = "⚡ ARCHITECTED BY AL HOSSAIN RIFAT • https://r1fat.pages.dev";

  sheet.getRange(1, 1).setValue(masterTitle);
  if (numCols >= 2) {
    sheet.getRange(1, numCols).setValue(authorBadge);
  }

  const masterRange = sheet.getRange(1, 1, 1, numCols);
  masterRange.setBackground("#0B0F19"); // Deep Cyber Obsidian
  masterRange.setFontColor("#F8FAFC");
  masterRange.setFontWeight("bold");
  masterRange.setFontSize(11);
  masterRange.setVerticalAlignment("middle");

  if (numCols >= 2) {
    sheet.getRange(1, numCols)
      .setFontColor("#38BDF8")
      .setFontWeight("bold")
      .setFontSize(9.5)
      .setHorizontalAlignment("right");
  }

  // -------------------------------------------------------------------------
  // 2. Data Column Headers (Row 2)
  // -------------------------------------------------------------------------
  sheet.setRowHeight(2, 36);
  const headerRange = sheet.getRange(2, 1, 1, numCols);
  headerRange.setValues([rawHeaders]);
  headerRange.setBackground("#1E293B"); // Deep Navy Slate
  headerRange.setFontColor("#F8FAFC");
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10.5);
  headerRange.setVerticalAlignment("middle");
  headerRange.setHorizontalAlignment("left");
  headerRange.setBorder(null, null, true, null, null, null, themeColor, SpreadsheetApp.BorderStyle.SOLID_THICK);

  // Freeze top 2 rows (Master Bar + Column Headers stay sticky)
  sheet.setFrozenRows(2);

  // -------------------------------------------------------------------------
  // 3. Populate Data & Atomic Matrix Color-Coding (Row 3+)
  // -------------------------------------------------------------------------
  if (numDataRows > 0) {
    const dataValues = rows.slice(1);
    sheet.setRowHeights(3, numDataRows, 28);
    const dataRange = sheet.getRange(3, 1, numDataRows, numCols);
    dataRange.setValues(dataValues);
    dataRange.setFontSize(9.5);
    dataRange.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);
    dataRange.setVerticalAlignment("middle");

    // Construct 2D background, font color, and font weight matrices
    const bgMatrix = [];
    const fontMatrix = [];
    const weightMatrix = [];

    // Header index lookups
    const headerLower = rawHeaders.map(function(h) { return String(h).toLowerCase(); });

    for (let r = 0; r < numDataRows; r++) {
      const rowBg = [];
      const rowFont = [];
      const rowWeight = [];
      const isEven = (r % 2 === 0);
      const defaultBg = isEven ? "#FFFFFF" : "#F8FAFC"; // Clean zebra
      const defaultFont = "#1E293B"; // Dark Slate text

      for (let c = 0; c < numCols; c++) {
        const val = String(dataValues[r][c] || "").trim();
        const lowerVal = val.toLowerCase();
        const colName = headerLower[c] || "";

        let cellBg = defaultBg;
        let cellFont = defaultFont;
        let cellWeight = "normal";

        // A. HTTP Status Codes (200, 301, 404, 500)
        if (colName.indexOf("status code") !== -1 || colName.indexOf("response code") !== -1 || (/^\d{3}$/.test(val) && colName.indexOf("status") !== -1)) {
          cellWeight = "bold";
          if (val === "200" || val === "201") {
            cellBg = "#D1FAE5"; cellFont = "#065F46"; // Mint Green Badge
          } else if (val.indexOf("3") === 0) {
            cellBg = "#DBEAFE"; cellFont = "#1E40AF"; // Cyan/Blue Redirect
          } else if (val.indexOf("4") === 0) {
            cellBg = "#FEE2E2"; cellFont = "#991B1B"; // Coral Red Error
          } else if (val.indexOf("5") === 0) {
            cellBg = "#FFE4E6"; cellFont = "#9F1239"; // Fiery Server Error
          }
        }
        // B. Issue Priority (Issues Tab)
        else if (colName.indexOf("priority") !== -1 || colName.indexOf("severity") !== -1) {
          cellWeight = "bold";
          if (lowerVal === "high" || lowerVal === "critical") {
            cellBg = "#FEE2E2"; cellFont = "#991B1B"; // Crimson
          } else if (lowerVal === "medium" || lowerVal === "warning") {
            cellBg = "#FEF3C7"; cellFont = "#92400E"; // Amber
          } else if (lowerVal === "low" || lowerVal === "opportunity") {
            cellBg = "#E0F2FE"; cellFont = "#0369A1"; // Sky Blue
          }
        }
        // C. Indexability
        else if (colName.indexOf("indexability") !== -1) {
          if (lowerVal === "indexable") {
            cellBg = "#DCFCE7"; cellFont = "#15803D"; cellWeight = "bold";
          } else if (lowerVal === "non-indexable") {
            cellBg = "#F1F5F9"; cellFont = "#64748B";
          }
        }
        // D. Title Length Optimization
        else if (colName.indexOf("title") !== -1 && colName.indexOf("length") !== -1) {
          const num = parseInt(val, 10);
          if (!isNaN(num)) {
            if (num > 60) {
              cellBg = "#FEF3C7"; cellFont = "#92400E"; cellWeight = "bold"; // Truncated on Google
            } else if (num >= 30 && num <= 60) {
              cellBg = "#D1FAE5"; cellFont = "#065F46"; cellWeight = "bold"; // Optimal
            } else if (num > 0 && num < 30) {
              cellBg = "#FEF3C7"; cellFont = "#92400E"; // Too short
            }
          }
        }
        // E. Meta Description Length Optimization
        else if (colName.indexOf("description") !== -1 && colName.indexOf("length") !== -1) {
          const num = parseInt(val, 10);
          if (!isNaN(num)) {
            if (num > 160) {
              cellBg = "#FEF3C7"; cellFont = "#92400E"; cellWeight = "bold"; // Too long
            } else if (num >= 70 && num <= 160) {
              cellBg = "#D1FAE5"; cellFont = "#065F46"; cellWeight = "bold"; // Optimal
            } else if (num > 0 && num < 70) {
              cellBg = "#FEF3C7"; cellFont = "#92400E"; // Too short
            }
          }
        }
        // F. Content Word Count Analysis
        else if (colName.indexOf("word") !== -1 && (colName.indexOf("count") !== -1 || colName.indexOf("words") !== -1)) {
          const num = parseInt(val, 10);
          if (!isNaN(num)) {
            if (num < 300 && num > 0) {
              cellBg = "#FEE2E2"; cellFont = "#991B1B"; cellWeight = "bold"; // Thin Content!
            } else if (num >= 800) {
              cellBg = "#D1FAE5"; cellFont = "#065F46"; cellWeight = "bold"; // Comprehensive
            }
          }
        }
        // G. Meta Robots & Directives
        else if (colName.indexOf("meta robots") !== -1 || colName.indexOf("directive") !== -1) {
          if (lowerVal.indexOf("noindex") !== -1 || lowerVal.indexOf("nofollow") !== -1) {
            cellBg = "#FEF3C7"; cellFont = "#92400E"; cellWeight = "bold";
          } else if (lowerVal.indexOf("index, follow") !== -1) {
            cellBg = "#DCFCE7"; cellFont = "#15803D";
          }
        }
        // H. Missing Tags & Alt Text Alerts
        else if (lowerVal === "missing" || (val === "0" && (colName.indexOf("h1") !== -1 || colName.indexOf("h2") !== -1 || colName.indexOf("alt") !== -1))) {
          cellBg = "#FFF1F2"; cellFont = "#BE123C"; cellWeight = "bold";
        }

        rowBg.push(cellBg);
        rowFont.push(cellFont);
        rowWeight.push(cellWeight);
      }
      bgMatrix.push(rowBg);
      fontMatrix.push(rowFont);
      weightMatrix.push(rowWeight);
    }

    // Apply entire color & typography matrix in 3 lightning-fast atomic operations
    dataRange.setBackgrounds(bgMatrix);
    dataRange.setFontColors(fontMatrix);
    dataRange.setFontWeights(weightMatrix);

    // Subtle cell grid borders
    dataRange.setBorder(true, true, true, true, true, true, "#E2E8F0", SpreadsheetApp.BorderStyle.SOLID);
  }

  // -------------------------------------------------------------------------
  // 4. Intelligent Column Sizing (Zero Mushing & Wide URLs)
  // -------------------------------------------------------------------------
  for (let c = 1; c <= numCols; c++) {
    const colTitle = String(rawHeaders[c - 1] || "").toLowerCase();

    // URLs and Address columns get wide 460px breathing room
    if (colTitle.indexOf("address") !== -1 || colTitle.indexOf("url") !== -1 || colTitle.indexOf("link") !== -1 || colTitle.indexOf("destination") !== -1 || colTitle.indexOf("source") !== -1 || colTitle.indexOf("canonical") !== -1) {
      sheet.setColumnWidth(c, 460);
      if (numDataRows > 0) sheet.getRange(3, c, numDataRows, 1).setHorizontalAlignment("left");
    }
    // Titles, Descriptions, Headings
    else if (colTitle.indexOf("title") !== -1 || colTitle.indexOf("description") !== -1 || colTitle.indexOf("h1") !== -1 || colTitle.indexOf("h2") !== -1) {
      sheet.setColumnWidth(c, 380);
      if (numDataRows > 0) sheet.getRange(3, c, numDataRows, 1).setHorizontalAlignment("left");
    }
    // How to Fix, Details, Overview
    else if (colTitle.indexOf("how to fix") !== -1 || colTitle.indexOf("overview") !== -1 || colTitle.indexOf("details") !== -1 || colTitle.indexOf("issue name") !== -1) {
      sheet.setColumnWidth(c, 450);
      if (numDataRows > 0) sheet.getRange(3, c, numDataRows, 1).setHorizontalAlignment("left");
    }
    // Status Code & Response Badges
    else if (colTitle.indexOf("status code") !== -1 || colTitle.indexOf("response code") !== -1) {
      sheet.setColumnWidth(c, 120);
      sheet.getRange(2, c, sheet.getMaxRows() - 1, 1).setHorizontalAlignment("center");
    }
    // Priority, Severity, Indexability
    else if (colTitle.indexOf("priority") !== -1 || colTitle.indexOf("severity") !== -1 || colTitle.indexOf("indexability") !== -1) {
      sheet.setColumnWidth(c, 130);
      sheet.getRange(2, c, sheet.getMaxRows() - 1, 1).setHorizontalAlignment("center");
    }
    // Lengths, Counts, Numbers, Ratios
    else if (colTitle.indexOf("length") !== -1 || colTitle.indexOf("count") !== -1 || colTitle.indexOf("width") !== -1 || colTitle.indexOf("ratio") !== -1 || colTitle.indexOf("words") !== -1 || colTitle.indexOf("size") !== -1 || colTitle.indexOf("occurrences") !== -1) {
      sheet.setColumnWidth(c, 130);
      sheet.getRange(2, c, sheet.getMaxRows() - 1, 1).setHorizontalAlignment("right");
    }
    // Default smart sizing with minimum floor of 180px
    else {
      sheet.setColumnWidth(c, 180);
      if (numDataRows > 0) sheet.getRange(3, c, numDataRows, 1).setHorizontalAlignment("left");
    }
  }
}

/**
 * Formats the Competitors Analysis tab into an Executive Benchmark Matrix:
 * Row 1: Gold Obsidian Master Banner
 * Row 2: Deep Slate Headers
 * Row 3 (Client): Mint Green VIP Glow (#D1FAE5)
 * Rows 4-8 (Rivals): Soft Crimson Rival Benchmark (#FEE2E2)
 */
function formatCompetitorsTab(sheet, customData, clientDomain) {
  const defaultHeaders = [
    "Website", "DA", "PA", "SS", "Ranking Keywords ( Moz )",
    "DR", "Backlink", "Linking Websites", "Website Traffic", "Traffic Values"
  ];

  let dataRows = [];
  if (customData && customData.length > 0) {
    dataRows = customData.slice(1); // skip headers if present
  } else {
    dataRows.push([clientDomain.indexOf("http") === 0 ? clientDomain : "https://" + clientDomain, "-", "-", "-", "-", "-", "-", "-", "-", "-"]);
    for (let i = 1; i <= 5; i++) {
      dataRows.push(["https://competitor-" + i + ".com (Pending Recon)", "-", "-", "-", "-", "-", "-", "-", "-", "-"]);
    }
  }

  const numCols = defaultHeaders.length;
  const numRows = dataRows.length;

  // 1. Master Obsidian Gold Banner (Row 1)
  sheet.setRowHeight(1, 44);
  sheet.getRange(1, 1).setValue("🐸 COMPETITOR INTELLIGENCE BENCHMARK MATRIX • " + clientDomain.toUpperCase());
  sheet.getRange(1, 1, 1, Math.min(5, numCols)).merge();
  sheet.getRange(1, numCols).setValue("⚡ ARCHITECTED BY AL HOSSAIN RIFAT • https://r1fat.pages.dev");

  const masterRange = sheet.getRange(1, 1, 1, numCols);
  masterRange.setBackground("#1C1917"); // Dark Warm Obsidian
  masterRange.setFontColor("#F59E0B"); // Gold
  masterRange.setFontWeight("bold");
  masterRange.setFontSize(11);
  masterRange.setVerticalAlignment("middle");

  sheet.getRange(1, numCols).setFontColor("#FBBF24").setFontWeight("bold").setFontSize(9.5).setHorizontalAlignment("right");

  // 2. Table Headers (Row 2)
  sheet.setRowHeight(2, 36);
  const headerRange = sheet.getRange(2, 1, 1, numCols);
  headerRange.setValues([defaultHeaders]);
  headerRange.setBackground("#0F172A");
  headerRange.setFontColor("#FFFFFF");
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10.5);
  headerRange.setHorizontalAlignment("center");
  headerRange.setVerticalAlignment("middle");
  headerRange.setBorder(null, null, true, null, null, null, "#F59E0B", SpreadsheetApp.BorderStyle.SOLID_THICK);

  sheet.setFrozenRows(2);

  // 3. Write Competitors Data (Row 3+)
  sheet.setRowHeights(3, numRows, 30);
  const dataRange = sheet.getRange(3, 1, numRows, numCols);
  dataRange.setValues(dataRows);
  dataRange.setFontSize(10);
  dataRange.setVerticalAlignment("middle");
  dataRange.setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);

  // Client Row (Row 3): Radiant Mint Green VIP Glow
  const clientRange = sheet.getRange(3, 1, 1, numCols);
  clientRange.setBackground("#D1FAE5");
  clientRange.setFontColor("#065F46");
  clientRange.setFontWeight("bold");
  clientRange.setBorder(true, true, true, true, false, false, "#10B981", SpreadsheetApp.BorderStyle.SOLID_MEDIUM);

  // Rivals Rows (Rows 4 to 8): Soft Red Benchmark Styling
  if (numRows > 1) {
    const rivalsCount = numRows - 1;
    const rivalsRange = sheet.getRange(4, 1, rivalsCount, numCols);
    rivalsRange.setBackground("#FEE2E2");
    rivalsRange.setFontColor("#991B1B");
    rivalsRange.setFontWeight("normal");
    rivalsRange.setBorder(true, true, true, true, true, true, "#FCA5A5", SpreadsheetApp.BorderStyle.SOLID);
  }

  // Column Widths (Website column extra wide!)
  sheet.setColumnWidth(1, 460);
  for (let c = 2; c <= numCols; c++) {
    sheet.setColumnWidth(c, 130);
    sheet.getRange(3, c, numRows, 1).setHorizontalAlignment("center");
  }
}
