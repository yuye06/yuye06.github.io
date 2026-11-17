"""Capture a point-cloud preview, with no raw camera photographs or uploads."""
import argparse
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--viewer', type=Path, required=True)
args = parser.parse_args()
assets = Path(__file__).resolve().parents[1] / 'assets'
with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True,
        args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width': 1800, 'height': 1300})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(args.viewer.resolve().as_uri())
    page.wait_for_function('window.mapReady === true', timeout=60000)
    assert not page.locator('#error').is_visible()
    page.locator('#color').select_option('0')
    page.locator('#size').fill('1.5')
    page.locator('#path').uncheck()
    page.locator('#outlines').uncheck()
    page.add_style_tag(content='header,.toolbar,footer,.overlay{display:none!important}.viewport{height:1100px!important;min-height:1100px!important;flex:none}body{height:1100px!important}')
    page.evaluate("azimuth=.72;elevation=.88;target=metadata.extents.campus.center.slice();distance=metadata.extents.campus.radius*1.9;draw()")
    temporary = assets / 'preview-capture.tmp.png'
    page.locator('#cloud').screenshot(path=str(temporary))
    assert not errors, errors
    browser.close()
with Image.open(temporary) as image:
    image.save(assets / 'clark-kerr-overview.webp', 'WEBP', quality=87, method=6)
temporary.unlink()
print('Public point-cloud poster captured; no camera imagery included.')
