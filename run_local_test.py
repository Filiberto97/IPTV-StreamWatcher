#!/usr/bin/env python3
"""CLI helper: import M3U URL into DB and run a single check pass, printing results."""
import sys
import asyncio
from src.iptv_monitor.config import ensure_dirs
from src.iptv_monitor.worker import fetch_text, parse_m3u, Monitor
from src.iptv_monitor.db import init_db, add_channels_bulk

async def main():
    if len(sys.argv) < 2:
        print('Usage: run_local_test.py <m3u_url>')
        return
    url = sys.argv[1]
    ensure_dirs()
    await init_db()
    import aiohttp
    async with aiohttp.ClientSession() as session:
        txt = await fetch_text(session, url)
        items = await parse_m3u(txt)
    if not items:
        print('No channels found in M3U')
        return
    ids = await add_channels_bulk(items)
    print(f'Imported {len(ids)} channels')
    mon = Monitor(None)
    results = await mon.run_once()
    print('Results:')
    for r in results[:20]:
        print(f"{r['name']}: {r['result']} - {r['notes']}")

if __name__ == '__main__':
    asyncio.run(main())
