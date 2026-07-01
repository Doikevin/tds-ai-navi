# -*- coding: utf-8 -*-
"""
東京ディズニーシー 待ち時間ロガー（CSV版 / GitHub Actions対応）
------------------------------------------------------------
Queue-Times.com API から待ち時間を、Open-Meteo から天気を取得し、
data/ フォルダの CSV ファイルに 1 回分を追記します。

CSV は月ごとにファイルを分けます（例: data/waits_2026-07.csv）。
これにより GitHub 上でデータが扱いやすく、履歴も自動でバックアップされます。

このスクリプトは「1回実行したら1回分を追記して終了」します。
定期実行（15分ごと）は GitHub Actions に任せます。

データ提供: Powered by Queue-Times.com  (https://queue-times.com/)
"""

import csv
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

# ── 設定 ──────────────────────────────────────────────
PARK_ID = 275  # Queue-Times 上の東京ディズニーシーのID
LAT, LON = 35.6267, 139.8851  # 東京ディズニーシーのおおよその位置（天気取得用）

# サーバー管理者があなたに連絡できるよう連絡先を明記します（作法）。
# ↓ の連絡先メールは、あなたのものに書き換えてください。
USER_AGENT = "TDS-Navi-Logger/1.0 (contact: your-email@example.com)"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
JST = ZoneInfo("Asia/Tokyo")

WAIT_HEADER = ["fetched_at", "ride_id", "ride_name",
               "is_open", "wait_time", "api_last_updated"]
WEATHER_HEADER = ["fetched_at", "temperature", "apparent_temperature",
                  "precipitation", "rain", "weather_code",
                  "cloud_cover", "wind_speed", "humidity"]


# ── HTTP 取得（失敗したら少し待って再試行）───────────────
def fetch_json(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(
                url, params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            wait = 2 ** attempt  # 1秒 → 2秒 → 4秒 と待ち時間を伸ばす
            print(f"  取得失敗 ({attempt + 1}/{retries}): {e} → {wait}秒待って再試行")
            time.sleep(wait)
    return None


# ── CSV に 1 行追記（無ければヘッダーを先に書く）──────────
def append_rows(path, header, rows):
    is_new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(header)
        writer.writerows(rows)


# ── 待ち時間の取得 ────────────────────────────────────
def get_wait_times():
    url = f"https://queue-times.com/parks/{PARK_ID}/queue_times.json"
    data = fetch_json(url)
    if data is None:
        return []
    rides = list(data.get("rides", []))
    for land in data.get("lands", []):
        rides.extend(land.get("rides", []))
    return rides


# ── 天気の取得 ────────────────────────────────────────
def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": "temperature_2m,apparent_temperature,precipitation,rain,"
                   "weather_code,cloud_cover,wind_speed_10m,relative_humidity_2m",
        "timezone": "Asia/Tokyo",
    }
    data = fetch_json(url, params=params)
    if data is None:
        return None
    return data.get("current")


# ── メイン処理 ────────────────────────────────────────
def main():
    now = datetime.now(JST)
    fetched_at = now.isoformat(timespec="seconds")
    month = now.strftime("%Y-%m")  # 月ごとにファイルを分ける

    DATA_DIR.mkdir(exist_ok=True)

    # 待ち時間
    rides = get_wait_times()
    wait_rows = [
        [fetched_at, r.get("id"), r.get("name"),
         1 if r.get("is_open") else 0, r.get("wait_time"), r.get("last_updated")]
        for r in rides
    ]
    if wait_rows:
        append_rows(DATA_DIR / f"waits_{month}.csv", WAIT_HEADER, wait_rows)

    # 天気
    w = get_weather()
    if w:
        weather_row = [[
            fetched_at, w.get("temperature_2m"), w.get("apparent_temperature"),
            w.get("precipitation"), w.get("rain"), w.get("weather_code"),
            w.get("cloud_cover"), w.get("wind_speed_10m"),
            w.get("relative_humidity_2m"),
        ]]
        append_rows(DATA_DIR / f"weather_{month}.csv", WEATHER_HEADER, weather_row)

    weather_str = f"{w.get('temperature_2m')}C" if w else "取得失敗"
    print(f"[{fetched_at}] 待ち時間 {len(wait_rows)}件を追記 / 天気 {weather_str}")


if __name__ == "__main__":
    main()
