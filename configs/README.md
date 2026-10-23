# Spider Configuration Profiles (`configs/`)

FrogPipe automatically detects and loads custom Screaming Frog `.seospiderconfig` profiles placed in this directory.

## Automatic Detection Priority
1. Any file specified via `--config-file <path>` CLI flag.
2. Any path specified under `"spider_config_file"` in `config.json`.
3. Auto-detected default preset in `configs/`:
   - `configs/ecommerce.seospiderconfig`
   - `configs/default.seospiderconfig`

## How to Export an Ecommerce Configuration from Screaming Frog
Screaming Frog `.seospiderconfig` files are binary serialized Java configuration objects generated directly by the SEO Spider desktop software:

1. Launch Screaming Frog SEO Spider UI.
2. Go to **Configuration > Spider**:
   - Enable **Crawl Canonicals** and **Follow Next/Prev**.
   - Under **Limits**, configure sensible max page limits or depth if needed.
   - Under **URL Rewriting / Parameters**, strip tracking query parameters (e.g. `utm_*`, `fbclid`, `gclid`).
3. Under **Configuration > Exclude**, add regex patterns for ecommerce parameter traps:
   - `.*(\?|&)(sort|order|orderby|dir|view|limit|add-to-cart|currency|sessionid|sid|PHPSESSID)=.*`
4. Click **File > Configuration > Save As...**.
5. Save the file directly to:
   `FrogPipe/configs/ecommerce.seospiderconfig`

Once saved, FrogPipe automatically applies this profile across all headless and batch crawls!
