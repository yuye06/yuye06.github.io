"""Build the static research portfolio and optionally export a public LiDAR preview.

This uses only the Python standard library. It never reads credentials,
downloads private repositories, or copies raw scans/camera photographs.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://yuye06.github.io'
OWNER = 'Yuye Zhou'
REVIEWED = '17 November 2026'


def write(path, content):
    destination = ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def status(project):
    planned = any(word in project['status'].lower() for word in ('concept', 'direction'))
    return '<span class="status' + (' concept' if planned else '') + '">' + escape(project['status']) + '</span>'


def head(title, description, base, canonical):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="theme-color" content="#f6f5ef">
<link rel="canonical" href="{SITE}/{canonical}"><link rel="icon" type="image/svg+xml" href="{base}assets/mark.svg"><link rel="stylesheet" href="{base}assets/site.css">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{SITE}/{canonical}"><meta property="og:image" content="{SITE}/assets/clark-kerr-overview.webp">
<meta name="twitter:card" content="summary_large_image"><script defer src="{base}assets/site.js"></script></head><body>
<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="{base}index.html" aria-label="Yuye Zhou home"><span class="brand-mark" aria-hidden="true">YZ</span><span><strong>Yuye Zhou</strong><small>Research in progress</small></span></a>
<button class="nav-button" aria-expanded="false" aria-controls="primary-nav">Menu <span aria-hidden="true">☰</span></button><nav id="primary-nav" class="site-nav" aria-label="Primary"><a href="{base}index.html#research">Projects</a><a href="{base}explore/clark-kerr/">3D explorer <span aria-hidden="true">↗</span></a><a href="{base}index.html#about">About</a><a href="https://github.com/yuye06" rel="me">GitHub <span aria-hidden="true">↗</span></a></nav></div></header>'''


def footer(base):
    return f'''<footer class="site-footer"><div class="wrap footer-inner"><div><p>Yuye Zhou <span aria-hidden="true"> / </span> Urban environments, spatial data, and human experience.</p><p class="footer-meta">Project notes curated {REVIEWED}. Work and status remain specific to each project.</p></div><div><p><a href="{base}index.html#research">Research notes</a> · <a href="https://github.com/yuye06">GitHub</a></p><p class="footer-meta">© 2026 Yuye Zhou</p></div></div></footer></body></html>'''


def home(projects):
    rows = []
    for index, project in enumerate(projects, 1):
        live = '<a class="live-link" href="explore/clark-kerr/">Open 3D <span aria-hidden="true">↗</span></a>' if project.get('featured') else f'<a href="projects/{project["slug"]}/">Project note <span aria-hidden="true">↗</span></a>'
        rows.append(f'''<article class="project-row" data-categories="{' '.join(project['categories'])}"><span class="project-index" aria-hidden="true">{index:02d}</span><div class="project-main"><div class="project-theme">{escape(project['theme'])}</div><h3><a href="projects/{project['slug']}/">{escape(project['title'])}</a></h3><p>{escape(project['summary'])}</p></div><div class="project-side">{status(project)}{live}</div></article>''')
    description = 'Research in progress by Yuye Zhou: urban heat, LiDAR, street-level perception, spatial modeling, and causal inference.'
    html = head('Yuye Zhou — research in progress', description, './', '')
    html += '''<main id="main"><div class="wrap"><section class="hero" aria-labelledby="hero-title"><div class="hero-copy"><p class="eyebrow">Urban environments / spatial research</p><h1 id="hero-title">Cities, climate,<br>and human<br><em>experience.</em></h1><p>I’m Yuye Zhou. I work across 3D sensing, street-level imagery, environmental modeling, and causal inference to study the places we live in.</p><div class="actions"><a class="button" href="explore/clark-kerr/">Explore Clark Kerr in 3D <span aria-hidden="true">↗</span></a><a class="text-link" href="#research">Browse the research</a></div><p class="hero-note">Interactive point-cloud preview. Data loads when you open the explorer.</p></div><div class="hero-visual"><a class="image-shell" href="projects/clark-kerr/" aria-label="Read about the Clark Kerr LiDAR project"><div class="image-topline"><span>Clark Kerr Campus / Berkeley</span><span><i class="live-dot"></i>3D preview</span></div><img src="assets/clark-kerr-overview.webp" alt="Elevation-colored 3D point cloud of Clark Kerr Campus and surrounding urban terrain" width="1800" height="1100" fetchpriority="high"></a><div class="image-caption"><div><strong>A campus, seen in depth.</strong><span>Airborne + portable LiDAR · elevation color · diagnostic alignment</span></div><a href="projects/clark-kerr/">Read the project <span aria-hidden="true">↗</span></a></div></div></section>
<div class="data-strip" aria-label="Portfolio and featured project overview"><div class="data-item"><strong>8</strong><span>research project notes</span></div><div class="data-item"><strong>4</strong><span>primary airborne tiles</span></div><div class="data-item"><strong>8.33 M</strong><span>portable map points</span></div><div class="data-item"><strong>2.2 M</strong><span>points in the browser preview</span></div></div>
<section id="research" class="research-section" aria-labelledby="research-title"><div class="section-heading"><div><p class="eyebrow">Questions, methods, and working results</p><h2 id="research-title">Work in progress.</h2></div><p>From field observations to model-based questions. Each note makes its current stage explicit.</p></div><div class="filter-bar" aria-label="Filter projects"><button class="filter" data-filter="all" aria-pressed="true">All projects</button><button class="filter" data-filter="sensing" aria-pressed="false">Sensing &amp; urban form</button><button class="filter" data-filter="heat" aria-pressed="false">Heat &amp; mobility</button><button class="filter" data-filter="human" aria-pressed="false">Human experience</button><span id="filter-count" class="filter-count" role="status" aria-live="polite">8 projects shown</span></div><div class="project-list">'''
    html += ''.join(rows)
    html += '''</div></section></div><section class="themes" aria-labelledby="threads-title"><div class="wrap"><p class="eyebrow" id="threads-title">Three connected threads</p><div class="theme-grid"><div><span class="theme-number">01 / OBSERVE</span><h3>Measure what surrounds us.</h3><p>LiDAR and street imagery offer different views of urban geometry, greenery, and sky openness. Their differences are part of the research.</p></div><div><span class="theme-number">02 / MODEL</span><h3>Connect form with exposure.</h3><p>Physical and learning-based models help ask how urban surfaces and atmospheric conditions shape heat through the day.</p></div><div><span class="theme-number">03 / INTERPRET</span><h3>Keep people in the picture.</h3><p>Perception, mobility, and emotional resilience bring human experience into the interpretation of urban environments.</p></div></div></div></section>
<div class="wrap"><section class="updates" aria-labelledby="updates-title"><div class="section-heading"><div><p class="eyebrow">Recent field notes</p><h2 id="updates-title">Building the evidence.</h2></div></div><article class="update-row"><time datetime="2026-11-17">17 November 2026</time><div><h3>Clark Kerr expands to a multi-tile view.</h3><p>Four primary airborne tiles and two optional overlap versions are now available beside the portable map, with source, elevation, class, and intensity controls.</p></div></article><article class="update-row"><time datetime="2026-11-16">16 November 2026</time><div><h3>A first alignment checkpoint.</h3><p>A single-tile diagnostic fit and spatially held-out checks established a starting point for reviewing local agreement. The expanded area still needs its own assessment.</p></div></article></section>
<section id="about" class="about" aria-labelledby="about-title"><div><p class="eyebrow">About this notebook</p><h2 id="about-title">Research,<br>made inspectable.</h2></div><div class="about-copy"><p>I’m interested in how the structure of a city relates to environmental exposure and everyday experience—and how to study those relationships with spatial data.</p><p>This site brings together ongoing pipelines, prototypes, and research directions. The project notes separate current checkpoints from open questions, with the Clark Kerr explorer as an interactive view into the work.</p><a class="text-link" href="https://github.com/yuye06">Find me on GitHub <span aria-hidden="true">↗</span></a><small>Selected project summaries are public here. The underlying code or study data may have separate access conditions.</small></div></section></div></main>'''
    return html + footer('./')


def project_page(project, lookup):
    base = '../../'
    slug = project['slug']
    html = head(project['title'] + ' — Yuye Zhou', project['summary'], base, 'projects/' + slug + '/')
    html += f'''<main id="main" class="wrap"><div class="breadcrumb"><a href="../../index.html">Home</a> <span aria-hidden="true"> / </span><a href="../../index.html#research">Projects</a> <span aria-hidden="true"> / </span>{escape(project['short'])}</div><section class="project-hero"><p class="eyebrow">{escape(project['theme'])}</p><div class="project-status-line">{status(project)}<span>Research note / November 2026</span></div><h1>{escape(project['title'])}</h1><p class="project-lead">{escape(project['summary'])}</p>'''
    if slug == 'clark-kerr':
        html += '<div class="actions"><a class="button" href="../../explore/clark-kerr/">Open the interactive 3D explorer <span aria-hidden="true">↗</span></a></div>'
    html += '</section>'
    if slug == 'clark-kerr':
        html += '<figure class="project-figure"><img src="../../assets/clark-kerr-overview.webp" alt="Actual elevation-colored point-cloud preview of the campus and surrounding terrain" width="1800" height="1100"><figcaption>Actual sampled point-cloud view. Elevation colors are not camera RGB; the registered portable geometry remains diagnostic.</figcaption></figure>'
    else:
        html += '<div class="diagram" aria-label="Research approach sketch">'
        for index, step in enumerate(project['diagram']):
            if index:
                html += '<span class="diagram-arrow" aria-hidden="true">→</span>'
            html += '<div class="diagram-step">' + escape(step) + '</div>'
        html += '</div>'
    html += '<div class="project-body"><div><section class="article-block"><h2>The question</h2><p class="question">' + escape(project['question']) + '</p></section>'
    html += '<section class="article-block"><h2>Approach</h2><ol>' + ''.join('<li>' + escape(step) + '</li>' for step in project['approach']) + '</ol></section>'
    html += '<section class="article-block"><h2>Current checkpoint</h2><p>' + escape(project['checkpoint']) + '</p></section>'
    html += '<div class="research-note"><strong>Scope &amp; interpretation.</strong> ' + escape(project['limitations']) + '</div>'
    html += '<section class="article-block"><h2>Next questions</h2><ul>' + ''.join('<li>' + escape(step) + '</li>' for step in project['next']) + '</ul></section>'
    if project.get('source_public'):
        html += '<div class="resource-row"><a class="button secondary" href="' + escape(project['source_url']) + '">Public replication repository <span aria-hidden="true">↗</span></a></div>'
    html += '</div><aside class="project-aside"><h3>Project at a glance</h3>'
    if slug == 'clark-kerr':
        for value, label in [('497.5 M', 'recorded airborne points in four primary tiles'), ('8.33 M', 'points in the portable map'), ('0.173 m', 'original northern-pilot median absolute difference'), ('1.444 m', 'original northern-pilot 95th-percentile difference')]:
            html += f'<div class="aside-stat"><strong>{value}</strong><span>{label}</span></div>'
        html += '<p>The agreement checks are conditional on a reference within 3 m. They are not independent survey-accuracy estimates and have not been extended to the added tiles.</p><div class="resource-row"><a class="text-link" href="../../explore/clark-kerr/">Explore the sampled data ↗</a></div><p>Airborne data: USGS. Provisional boundary: © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>. Full-resolution scans and camera recordings are not distributed here.</p>'
    else:
        html += '<p><strong>Stage:</strong> ' + escape(project['status']) + '</p><p>This note summarizes the available project scope. Its status does not imply that all proposed analyses or evaluations are complete.</p>'
    html += '<div class="related"><h3>Connected projects</h3>'
    for related in project['related']:
        target = lookup[related]
        html += f'<a href="../{related}/">{escape(target["short"])} <span aria-hidden="true">↗</span></a>'
    html += '</div></aside></div></main>'
    return html + footer(base)


def export_viewer(path):
    """Retain the full sampled viewer, using compressed same-origin numeric buffers."""
    source = path.read_text(encoding='utf-8')
    if 'CLARK_KERR_MULTI_TILE_VIEWER:1' not in source[:4096]:
        raise ValueError('Expected the verified multi-tile viewer.')
    public = ROOT / 'explore/clark-kerr'
    (public / 'data').mkdir(parents=True, exist_ok=True)
    manifest = {}
    for tag, filename in [('map-data', 'points.f32.gz'), ('class-data', 'classes.u8.gz'), ('trajectory-data', 'path.f32.gz')]:
        pattern = r'(<script id="' + tag + r'" type="application/octet-stream">)(.*?)(</script>)'
        match = re.search(pattern, source, flags=re.S)
        if not match:
            raise ValueError('Missing numeric buffer: ' + tag)
        raw = base64.b64decode(match[2], validate=True)
        compressed = gzip.compress(raw, compresslevel=7, mtime=0)
        (public / 'data' / filename).write_bytes(compressed)
        manifest[tag] = {'url': 'data/' + filename, 'bytes': len(raw), 'compressedBytes': len(compressed),
                         'sha256': hashlib.sha256(raw).hexdigest()}
        source = source[:match.start(2)] + source[match.end(2):]
    marker = 'function decode(id,Type)'
    start = source.index(marker)
    end = source.index('\nfunction shader(', start)
    replacement = "const publicBuffers={};function decode(id,Type){const data=publicBuffers[id];if(!data)throw Error('Missing point buffer');delete publicBuffers[id];$(id).remove();return new Type(data);}"
    source = source[:start] + replacement + source[end:]
    source = source.replace('<div><h1>Clark Kerr', '<div><a class="portfolio-back" href="../../index.html">← Yuye Zhou / research</a><h1>Clark Kerr', 1)
    source = source.replace('</style>', '.portfolio-back{font-size:11px;color:#94cbbd;text-decoration:none;display:inline-block;margin-bottom:5px}.portfolio-back:hover{text-decoration:underline}.public-loading{position:absolute;z-index:4;left:50%;top:45%;transform:translate(-50%,-50%);width:min(460px,88%);background:#122235;padding:25px;border:1px solid #344b61;border-radius:8px;line-height:1.7;color:#d7e4ef;box-shadow:0 14px 44px #0005}.public-loading strong{font-size:17px}.public-loading p{font-size:12px;margin:9px 0}.public-loading progress{width:100%;height:9px;accent-color:#79d7c4}.public-loading[hidden]{display:none}button:disabled,select:disabled,input:disabled{opacity:.45}</style>', 1)
    source = source.replace('<div id="error" role="alert" hidden>', '<div class="public-loading" id="public-loading" role="status" aria-live="polite"><strong>Loading the 3D preview</strong><p id="public-progress">Connecting to the sampled point data…</p><progress id="public-progress-bar" max="100" value="0"></progress><p>2.2 million preview points. Full-resolution scans and camera recordings are not included.</p></div><div id="error" role="alert" hidden>', 1)
    source = source.replace('<footer id="method"></footer>', '<footer><div id="method"></div><span>Airborne data: USGS · Boundary: © <a style="color:#94cbbd" href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · <a style="color:#94cbbd" href="../../projects/clark-kerr/">Project note</a></span></footer>', 1)
    expected = 'try{init();}catch(error){$(\'error\').textContent=error.message;$(\'error\').hidden=false;console.error(error);}'
    if expected not in source:
        raise ValueError('Viewer initialization hook changed; inspect before exporting.')
    loader = '''
const publicData=__DATA_MANIFEST__;
const publicReceived={};
const publicControls=[...document.querySelectorAll('button,select,input')];
publicControls.forEach(control=>control.disabled=true);
function publicProgress(){const total=Object.values(publicData).reduce((n,v)=>n+v.compressedBytes,0),received=Object.values(publicReceived).reduce((a,b)=>a+b,0);$('public-progress').textContent=(received/1e6).toFixed(1)+' / '+(total/1e6).toFixed(1)+' MB · preparing the point cloud';$('public-progress-bar').value=Math.min(99,received/total*100);}
async function publicLoad(id,record){const response=await fetch(record.url);if(!response.ok)throw Error('Point data could not be loaded ('+response.status+').');const chunks=[];let bytes=0;const reader=response.body.getReader();for(;;){const result=await reader.read();if(result.done)break;chunks.push(result.value);bytes+=result.value.byteLength;publicReceived[id]=bytes;publicProgress();}const packed=new Uint8Array(bytes);let offset=0;for(const chunk of chunks){packed.set(chunk,offset);offset+=chunk.byteLength;}let raw;if(packed[0]===31&&packed[1]===139){if(typeof DecompressionStream==='undefined')throw Error('Please use a current version of Chrome, Edge, Firefox or Safari to open this compressed 3D preview.');raw=await new Response(new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();}else raw=packed.buffer;if(raw.byteLength!==record.bytes)throw Error('Point data was incomplete. Please reload the page.');publicBuffers[id]=raw;}
async function publicStart(){await Promise.all(Object.entries(publicData).map(([id,record])=>publicLoad(id,record)));$('public-progress').textContent='Preparing the 3D view…';await new Promise(resolve=>requestAnimationFrame(resolve));init();publicControls.forEach(control=>control.disabled=false);$('public-loading').hidden=true;}
publicStart().catch(error=>{$('public-loading').hidden=true;$('error').textContent=error.message+' Reload this page to try again.';$('error').hidden=false;console.error(error);});
'''.replace('__DATA_MANIFEST__', json.dumps(manifest))
    source = source.replace(expected, loader)
    # The published artifact must not contain local filesystem links or user paths.
    for pattern in (r'file://', r'[A-Za-z]:\\', r'C:/Users/', r'github_pat_', r'ghp_[A-Za-z0-9]{20,}'):
        if re.search(pattern, source):
            raise ValueError('A local-path or credential pattern was found in the public viewer.')
    (public / 'index.html').write_text(source, encoding='utf-8')
    (public / 'preview_manifest.json').write_text(json.dumps({'kind': 'sampled visualization, not full-resolution survey', 'buffers': manifest}, indent=2), encoding='utf-8')
    return {'compressed_bytes': sum(row['compressedBytes'] for row in manifest.values()),
            'numeric_bytes': sum(row['bytes'] for row in manifest.values())}


def build(viewer=None):
    projects = json.loads((ROOT / 'content/projects.json').read_text(encoding='utf-8'))
    assert len({p['slug'] for p in projects}) == len(projects) == 8
    lookup = {p['slug']: p for p in projects}
    write('index.html', home(projects))
    for project in projects:
        write('projects/' + project['slug'] + '/index.html', project_page(project, lookup))
    missing = head('Page not found — Yuye Zhou', 'Return to the research portfolio.', '/', '404.html')
    missing += '<main id="main" class="wrap notfound"><p class="eyebrow">404 / page not found</p><h1>Back to the research.</h1><p>This page may have moved.</p><a class="button" href="/">Return to the portfolio</a></main>'
    write('404.html', missing + footer('/'))
    write('robots.txt', 'User-agent: *\nAllow: /\nSitemap: ' + SITE + '/sitemap.xml\n')
    urls = [SITE + '/'] + [SITE + '/projects/' + p['slug'] + '/' for p in projects] + [SITE + '/explore/clark-kerr/']
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + escape(url) + '</loc><lastmod>2026-11-17</lastmod></url>' for url in urls) + '</urlset>\n')
    report = {'projects': len(projects), 'personal_data': 'Display name and GitHub profile only; no email or credentials.',
              'raw_survey_files_included': False, 'other_private_project_implementation_code_included': False}
    if viewer:
        report['preview'] = export_viewer(viewer)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--viewer', type=Path, help='Optional local verified multi-tile HTML to update the public sampled explorer.')
    build(parser.parse_args().viewer)
