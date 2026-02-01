import asyncio
import aiohttp
import time
import m3u8
from .db import insert_result

async def fetch_text(session, url, timeout=15):
    async with session.get(url, timeout=timeout) as r:
        r.raise_for_status()
        return await r.text()

async def fetch_bytes(session, url, timeout=15):
    start = time.time()
    async with session.get(url, timeout=timeout) as r:
        r.raise_for_status()
        data = await r.read()
    elapsed = time.time() - start
    return len(data), elapsed

async def check_hls(url):
    async with aiohttp.ClientSession() as session:
        try:
            txt = await fetch_text(session, url)
            manifest = m3u8.loads(txt)
            # pick first variant or the playlist itself
            playlist_url = url
            if manifest.is_variant:
                # pick highest bandwidth
                best = max(manifest.playlists, key=lambda p: (p.stream_info.bandwidth or 0))
                playlist_url = best.uri
            # fetch media playlist
            media_txt = await fetch_text(session, playlist_url)
            media = m3u8.loads(media_txt)
            segments = (media.segments or [])[:2]
            if not segments:
                return 'error', 'no segments', None, None
            total_bytes = 0
            total_seconds = 0
            for seg in segments:
                seg_url = seg.uri if seg.uri.startswith('http') else '/'.join(playlist_url.split('/')[:-1]) + '/' + seg.uri
                b, s = await fetch_bytes(session, seg_url)
                total_bytes += b
                total_seconds += s
            throughput = (total_bytes * 8) / (total_seconds * 1_000_000) if total_seconds > 0 else 0
            startup = (segments[0].duration or 0) + 0.5
            return 'pass', f'fetched {len(segments)} segments', throughput, startup
        except Exception as e:
            return 'error', str(e), None, None

class Monitor:
    def __init__(self, db, interval=900):
        self.db = db
        self.interval = interval
        self._task = None
        self._running = False

    async def _run_one(self, channel):
        cid, name, url = channel
        result, notes, throughput, startup = await check_hls(url)
        await insert_result(cid, result, notes, throughput, startup)

    async def _loop(self):
        from .db import list_channels
        while self._running:
            channels = await list_channels()
            tasks = [self._run_one(c) for c in channels]
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(self.interval)

    def start(self):
        if self._task and not self._task.done():
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
