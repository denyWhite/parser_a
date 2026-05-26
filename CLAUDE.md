# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Avito Parser is a Python 3.11+ scraper that monitors new listings on Avito (Russian classifieds), filters them, and sends notifications via Telegram or VK. Runs as a GUI app (Flet), CLI, or Docker container.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run GUI mode
python AvitoParser.py

# Run CLI/headless mode
python parser_cls.py

# Install Playwright browsers (needed for cookie retrieval)
playwright install chromium
```

### Docker (via Makefile)
```bash
make build      # Build image
make run        # Start in background
make logs       # View logs
make restart    # Restart container
make rebuild    # Rebuild and restart
make shell      # Open container shell
make clean      # Full cleanup (stop + remove image)
```

## Architecture

### Entry Points
- **`AvitoParser.py`** — Flet-based GUI; reads/writes `config.toml`, starts/stops the parser
- **`parser_cls.py`** — `AvitoParse` class; headless/CLI mode, the core parsing orchestrator

### Core Flow
1. `AvitoParse` builds an `AvitoConfig` DTO from `config.toml`
2. Selects proxy, cookie provider, notifier, and storage via factory functions
3. Calls Avito's internal API (`/web/1/map/items` endpoint) in a polling loop
4. Passes results through `AdsFilter` pipeline
5. Tracks seen ads in SQLite (`db_service.py`) to avoid duplicates
6. Sends new ads via notifier and writes to Excel if configured

### Key Modules

| Path | Responsibility |
|------|----------------|
| `dto.py` | `AvitoConfig` dataclass — single source of truth for all user settings |
| `models.py` | Pydantic models for Avito API responses (`Item`, `ItemsResponse`) |
| `filters/ads_filter.py` | Sequential filter pipeline (price, keywords, geo, sellers, time, etc.) |
| `db_service.py` | SQLite singleton for tracking viewed ad IDs |
| `get_cookies.py` | Playwright-based automated cookie/session retrieval |
| `parser/http/client.py` | `HttpClient` using `curl_cffi` with Chrome browser impersonation |
| `parser/proxies/` | Proxy abstraction: `NoProxy`, `ServerProxy`, `MobileProxy` + factory |
| `parser/cookies/` | Cookie providers (external API, own cookies) + factory |
| `parser/export/` | Storage backends (Excel via `openpyxl`) + composite + factory |
| `integrations/notifications/` | Notifier plugins (Telegram, VK) + `CompositeNotifier` + factory |
| `utils/` | Config building helpers, phone parsing utilities |

### Design Patterns
- **Factory** — `proxy_factory.py`, `cookies/factory.py`, `export/factory.py`, `notifications/factory.py` select implementations based on `AvitoConfig`
- **Composite** — `CompositeNotifier` and `CompositeResultStorage` fan out to multiple backends simultaneously
- **Singleton** — `SQLiteDBHandler` in `db_service.py`
- **Pipeline** — `AdsFilter` applies filters sequentially; each filter is a method called in order

### Adding a New Notifier
1. Create a class inheriting from `BaseNotifier` in `integrations/notifications/`
2. Register it in `integrations/notifications/factory.py`
3. Add any new config fields to `AvitoConfig` in `dto.py`

### Adding a New Filter
Add a method to `AdsFilter` in `filters/ads_filter.py` and call it in the main `filter()` method.

## Release Process

- Version is defined in `version.py`
- Pushing to `master` triggers GitHub Actions to build a Windows `.exe` via PyInstaller (`release.yml`)
- Tagging a version triggers Docker multi-arch image build and push to `ghcr.io` (`docker.yml`)

## Key Dependencies

- `flet` 0.24.1 — GUI framework
- `curl_cffi` — HTTP client with Chrome TLS/JA3 fingerprint impersonation (anti-bot bypass)
- `playwright` + `playwright-stealth` — browser automation for cookie retrieval
- `pydantic` 2.x — API response validation
- `loguru` — structured logging throughout
- `openpyxl` / `pyexcel` — Excel export