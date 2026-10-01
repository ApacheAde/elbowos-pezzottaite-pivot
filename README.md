# Pezzottaite Pivot

Full-colour Python 3 neon rotary colour-catch arcade for [ElbowOS](https://x.com/ElbowOS).

Shards fly in from the rim. Spin the eight-notch hub so a matching colour faces each shard as it hits. Coral, mint, amber, sky. Not a ROM and not an emulator — original rules and art.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 pezzottaite_pivot.py --play
```

A / D or arrows spin the hub. Space boosts the spin. R restarts. Esc quits.

## Record a 9:16 reel

```bash
python3 pezzottaite_pivot.py
```

Headless autoplay writes `PezzottaitePivot_ElbowOS.mp4` (1080x1920, 15s, 30fps, libx264 yuv420p). Needs ffmpeg on PATH. Dummy SDL video is fine.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/116qDOMLpXbDpkThLyRmCiV5p0T4g52kG/view
