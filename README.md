# Yuye Zhou — research in progress

Static research portfolio and sampled Clark Kerr LiDAR explorer for GitHub Pages.

## Public scope

- Eight curated project summaries, with status and open questions.
- The current sampled 3D explorer, preserving its per-tile and dataset controls.
- A point-cloud poster captured from that explorer.

Website code and the selected viewer are public. This repository does not distribute raw LiDAR recordings, full-resolution LAS/LAZ files, camera photographs, other private project implementation code, private study datasets, or credentials. The explorer's numeric buffers are the same sampled visualization data as the local viewer, compressed for delivery. It remains a diagnostic registered point-cloud comparison, not accepted analytical fusion or a thermal simulation.

## Update content

Edit `content/projects.json`, then run:

```text
python scripts/build.py
```

To replace the sampled explorer from an updated local multi-tile viewer:

```text
python scripts/build.py --viewer path/to/view_alignment_pilot.html
```

The builder uses Python's standard library. Optional poster capture uses Playwright, Pillow, and an installed Microsoft Edge:

```text
python scripts/capture_preview.py --viewer path/to/view_alignment_pilot.html
```

Preview through an HTTP server, since the explorer fetches compressed numeric buffers:

```text
python -m http.server 8000
```

Open `http://localhost:8000/`. Modern browsers with WebGL and `DecompressionStream` support are required for the 3D explorer. Portfolio pages remain ordinary static HTML.

## Hosting

GitHub Pages publishes the root of `main`. `.nojekyll` keeps the site buildless. Main URL: `https://yuye06.github.io/`; interactive preview: `https://yuye06.github.io/explore/clark-kerr/`.

## Attribution and interpretation

Airborne point data: USGS. Provisional campus boundary: © OpenStreetMap contributors, https://www.openstreetmap.org/copyright. Portable reconstruction and its registration remain diagnostic. Agreement statistics shown in the explorer apply only to the original northern pilot.

Project summaries were curated from the owner's project notes with authorization to share summaries of private projects. A summary does not make the underlying repository or datasets public. No publication status, degree, institutional appointment, or validated model performance is inferred.
