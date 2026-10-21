/**
 * =========================================================================
 *     FROGPIPE — HIGH-GRADE EXECUTIVE GOOGLE SHEETS LIVE ENGINE v4.5
 *          CHROMATIC COLOR CIRCLE HARMONY & BESPOKE COLUMN STYLING
 *               Architected & Engineered by Al Hossain Rifat
 *                        Portfolio: https://r1fat.pages.dev
 * =========================================================================
 * Highlights & Visual Effects:
 *   1. Chromatic Color Circle Theory (Harmonized Column Identities):
 *      Every column possesses its own tailored jewel-tone header badge and
 *      cohesive harmonic pastel lane tinting derived from the 360° color wheel:
 *        - Addressing & URLs: Deep Sapphire Navy (#1E3A8A / #F0F4F8)
 *        - Health & HTTP Protocols: Deep Forest Emerald (#064E3B / #F0FDF4)
 *        - Editorial & Headings/Titles: Deep Ocean Teal (#0F766E / #F0FDFA)
 *        - Meta Descriptions & SERP: Deep Royal Violet (#581C87 / #FAF5FF)
 *        - Directives & Robots Directives: Deep Twilight Indigo (#312E81 / #EEF2FF)
 *        - Quantitative Metrics & Lengths: Deep Bronze Amber (#78350F / #FFFBEB)
 *        - Quality & Diagnostic Issues: Deep Ruby Crimson (#881337 / #FFF1F2)
 *        - Media & Image Assets: Deep Raspberry Plum (#701A75 / #FDF2F8)
 *   2. Vibrant Sheet Tab Palette:
 *      Every sheet tab features its own saturated badge at the bottom.
 *   3. Executive Dual Sticky Headers:
 *      - Row 1: Deep Cyber Obsidian Master Bar (#0B0F19) with Author Credit
 *      - Row 2: Chromatically Tailored Column Headers with White Bold text
 *      - Top 2 rows frozen sticky during scrolling.
 *   4. Zero-Mushing Intelligent Column Sizing:
 *      - URLs & Addresses: 460px wide (no collision or truncation)
 *      - Titles, Descriptions & Issues: 380-450px wide
 *      - Status Codes & Priority Badges: 120-130px centered
 *      - Numeric metrics (Length, Width, Words): 130px right-aligned
 *      - Minimum floor: 180px for standard attributes
 *   5. Dynamic 2D Matrix Badges & Triage Flags:
 *      - Status Codes: 200 (Mint Green #D1FAE5), 3xx (Sky Blue #DBEAFE),
 *        4xx (Coral Red #FEE2E2), 5xx (Fiery Rose #FFE4E6)
 *      - Priorities: High (Crimson Badge), Medium (Amber), Low (Sky Blue)
 *      - SEO Length & Depth Warnings: Truncated titles/descriptions in amber;
 *        thin content (<300 words) in soft red; rich content in green
 *      - Missing Tags: Highlighted in bold alert rose #FFF1F2
 *   6. Executive Competitor Intelligence Matrix:
 *      - Harmonized Moz, Ahrefs, and Traffic metric column headers
 *      - Client Domain in radiant mint green glow (#D1FAE5 + 2px emerald border)
 *      - Rival competitors in soft rose benchmark (#FEE2E2)
 *   7. High-Speed Atomic Performance:
 *      - Renders thousands of cells via 2D background and font arrays in milliseconds!
 * =========================================================================
 */

function doGet(e) {
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    service: "FrogPipe Chromatic Color Harmony Google Sheets Engine v4.5",
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
 * Color Circle Theory Harmonic Palette Engine:
 * Maps column semantic identities into 8 cohesive, harmonized color families:
 *   1. Addressing & URLs (Deep Sapphire Navy #1E3A8A / Soft Slate Ice #F0F4F8)
 *   2. HTTP Protocol & Health (Deep Forest Emerald #064E3B / Soft Mint #F0FDF4)
 *   3. Editorial & Headings/Titles (Deep Ocean Teal #0F766E / Soft Oceanic #F0FDFA)
 *   4. Meta Descriptions & SERP (Deep Royal Violet #581C87 / Soft Violet #FAF5FF)
 *   5. Directives & Indexing (Deep Twilight Indigo #312E81 / Soft Indigo #EEF2FF)
 *   6. Quantitative Metrics & Lengths (Deep Bronze Amber #78350F / Soft Parchment #FFFBEB)
 *   7. Quality & Diagnostic Issues (Deep Ruby Crimson #881337 / Soft Rose #FFF1F2)
 *   8. Media & Image Assets (Deep Raspberry Plum #701A75 / Soft Blush Plum #FDF2F8)
 */
function getColumnColorTheme(colName) {
  const col = String(colName || "").toLowerCase();

  // Family 1: Addressing, URLs, Links, Canonicals (Navy Sapphire)
  if (col.indexOf("address") !== -1 || col.indexOf("url") !== -1 || col.indexOf("link") !== -1 || col.indexOf("destination") !== -1 || col.indexOf("source") !== -1 || col.indexOf("canonical") !== -1) {
    return {
      headerBg: "#1E3A8A",      // Deep Sapphire Navy
      headerFont: "#FFFFFF",
      accentBorder: "#38BDF8",  // Sky Blue Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#F0F4F8",     // Cool Slate Ice
      textColor: "#0F172A"
    };
  }

  // Family 2: HTTP Status & Health (Forest Emerald)
  if (col.indexOf("status code") !== -1 || col.indexOf("response code") !== -1 || col.indexOf("status") !== -1 || col.indexOf("protocol") !== -1) {
    return {
      headerBg: "#064E3B",      // Deep Forest Emerald
      headerFont: "#FFFFFF",
      accentBorder: "#34D399",  // Mint Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#F0FDF4",     // Subtle Mint Tint
      textColor: "#064E3B"
    };
  }

  // Family 3: Editorial, Headings & Titles (Ocean Teal)
  if (col.indexOf("title") !== -1 || col.indexOf("h1") !== -1 || col.indexOf("h2") !== -1 || col.indexOf("snippet") !== -1 || col.indexOf("heading") !== -1) {
    return {
      headerBg: "#0F766E",      // Deep Ocean Teal
      headerFont: "#FFFFFF",
      accentBorder: "#2DD4BF",  // Cyan Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#F0FDFA",     // Soft Oceanic Tint
      textColor: "#134E4A"
    };
  }

  // Family 4: Meta Descriptions (Royal Violet)
  if (col.indexOf("description") !== -1) {
    return {
      headerBg: "#581C87",      // Deep Royal Violet
      headerFont: "#FFFFFF",
      accentBorder: "#A855F7",  // Violet Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#FAF5FF",     // Soft Violet Tint
      textColor: "#3B0764"
    };
  }

  // Family 5: Indexing, Meta Robots & Directives (Twilight Indigo)
  if (col.indexOf("indexability") !== -1 || col.indexOf("directive") !== -1 || col.indexOf("robot") !== -1 || col.indexOf("meta") !== -1) {
    return {
      headerBg: "#312E81",      // Deep Twilight Indigo
      headerFont: "#FFFFFF",
      accentBorder: "#818CF8",  // Electric Indigo Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#EEF2FF",     // Soft Indigo Tint
      textColor: "#1E1B4B"
    };
  }

  // Family 6: Quantitative Metrics, Lengths, Counts, Words (Warm Bronze Amber)
  if (col.indexOf("length") !== -1 || col.indexOf("count") !== -1 || col.indexOf("word") !== -1 || col.indexOf("width") !== -1 || col.indexOf("ratio") !== -1 || col.indexOf("size") !== -1 || col.indexOf("occurrences") !== -1 || col.indexOf("bytes") !== -1) {
    return {
      headerBg: "#78350F",      // Deep Warm Bronze
      headerFont: "#FFFFFF",
      accentBorder: "#FBBF24",  // Amber Gold Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#FFFBEB",     // Soft Parchment Tint
      textColor: "#451A03"
    };
  }

  // Family 7: Diagnostic Issues, Severity, Priorities (Ruby Crimson)
  if (col.indexOf("issue") !== -1 || col.indexOf("priority") !== -1 || col.indexOf("severity") !== -1 || col.indexOf("error") !== -1 || col.indexOf("warning") !== -1 || col.indexOf("how to fix") !== -1) {
    return {
      headerBg: "#881337",      // Deep Ruby Carbon
      headerFont: "#FFFFFF",
      accentBorder: "#F87171",  // Rose Red Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#FFF1F2",     // Soft Rose Tint
      textColor: "#4C0519"
    };
  }

  // Family 8: Media Assets, Images, Dimensions (Raspberry Plum)
  if (col.indexOf("image") !== -1 || col.indexOf("alt") !== -1 || col.indexOf("picture") !== -1 || col.indexOf("media") !== -1) {
    return {
      headerBg: "#701A75",      // Deep Raspberry Plum
      headerFont: "#FFFFFF",
      accentBorder: "#F472B6",  // Pink Glow
      cellBgEven: "#FFFFFF",
      cellBgOdd: "#FDF2F8",     // Soft Blush Plum
      textColor: "#4A044E"
    };
  }

  // Default Fallback (Executive Charcoal Navy)
  return {
    headerBg: "#1E293B",        // Deep Navy Slate
    headerFont: "#FFFFFF",
    accentBorder: "#94A3B8",    // Slate Silver Glow
    cellBgEven: "#FFFFFF",
    cellBgOdd: "#F8FAFC",       // Ice White
    textColor: "#1E293B"
  };
}

/**
 * High-Grade Tab Formatter:
 * - Master Obsidian KPI Banner (Row 1)
 * - Chromatic Column Headers with Harmonized Palette (Row 2)
 * - Subtle Harmonic Column Lane Tinting & Badge Triage (Row 3+)
 * - Intelligent Proportional Column Widths
 */
function formatHighGradeTab(sheet, rows, domain, tabName) {
  if (!rows || rows.length === 0) return;

  const rawHeaders = rows[0];
  const numDataRows = rows.length - 1;
  const numCols = rawHeaders.length;

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
  // 2. Chromatic Data Column Headers (Row 2)
  // -------------------------------------------------------------------------
  sheet.setRowHeight(2, 38);
  const headerRange = sheet.getRange(2, 1, 1, numCols);
  headerRange.setValues([rawHeaders]);

  const headerBgs = [];
  const headerFonts = [];
  const colThemes = [];

  for (let c = 0; c < numCols; c++) {
    const theme = getColumnColorTheme(rawHeaders[c]);
    colThemes.push(theme);
    headerBgs.push(theme.headerBg);
    headerFonts.push(theme.headerFont);
  }

  headerRange.setBackgrounds([headerBgs]);
  headerRange.setFontColors([headerFonts]);
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10.5);
  headerRange.setVerticalAlignment("middle");
  headerRange.setHorizontalAlignment("left");
  headerRange.setBorder(true, true, true, true, true, true, "#334155", SpreadsheetApp.BorderStyle.SOLID);

  // Freeze top 2 rows (Master Bar + Column Headers stay sticky)
  sheet.setFrozenRows(2);

  // -------------------------------------------------------------------------
  // 3. Populate Data & Harmonic Matrix Color-Coding (Row 3+)
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

      for (let c = 0; c < numCols; c++) {
        const theme = colThemes[c];
        const val = String(dataValues[r][c] || "").trim();
        const lowerVal = val.toLowerCase();
        const colName = headerLower[c] || "";

        // Base harmonic column lane tint
        let cellBg = isEven ? theme.cellBgEven : theme.cellBgOdd;
        let cellFont = theme.textColor;
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
 * Row 2: Chromatic Jewel-Tone Column Headers
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

  // 2. Chromatic Jewel-Tone Headers (Row 2)
  sheet.setRowHeight(2, 38);
  const headerRange = sheet.getRange(2, 1, 1, numCols);
  headerRange.setValues([defaultHeaders]);

  const compHeaderBgs = [
    "#1E3A8A", // Website (Sapphire Navy)
    "#78350F", // DA (Warm Bronze)
    "#78350F", // PA (Warm Bronze)
    "#881337", // SS (Spam Score Ruby)
    "#0F766E", // Keywords (Ocean Teal)
    "#312E81", // DR (Twilight Indigo)
    "#312E81", // Backlinks (Twilight Indigo)
    "#312E81", // Linking Domains (Twilight Indigo)
    "#064E3B", // Traffic (Forest Emerald)
    "#064E3B"  // Traffic Values (Forest Emerald)
  ];
  const compHeaderFonts = Array(numCols).fill("#FFFFFF");

  headerRange.setBackgrounds([compHeaderBgs]);
  headerRange.setFontColors([compHeaderFonts]);
  headerRange.setFontWeight("bold");
  headerRange.setFontSize(10.5);
  headerRange.setHorizontalAlignment("center");
  headerRange.setVerticalAlignment("middle");
  headerRange.setBorder(true, true, true, true, true, true, "#334155", SpreadsheetApp.BorderStyle.SOLID);

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
