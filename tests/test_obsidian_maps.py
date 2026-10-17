"""Integration checks: run with the project's bundle available on PATH."""
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import os
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MapParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.maps = []
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if 'data-map' in attributes:
            self.maps.append(json.loads(attributes['data-map']))


class MapsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'source'
        shutil.copytree(ROOT, self.source, ignore=shutil.ignore_patterns(
            '.git', '.bundle', '_site', '.jekyll-cache', '__pycache__'))
        gitdir = subprocess.check_output(
            ['git', '-C', str(ROOT), 'rev-parse', '--absolute-git-dir'], text=True).strip()
        (self.source / '.git').write_text('gitdir: ' + gitdir + '\n')

    def build(self, success=True):
        result = subprocess.run(['bundle', 'exec', 'jekyll', 'build', '--baseurl', '/garden'],
                                cwd=self.source, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def payload(self):
        return MapParser((self.source / '_site/home.html').read_text()).maps[0]

    def test_sample_map(self):
        self.build()
        data = self.payload()
        self.assertEqual(len(data['markers']), 2)
        self.assertEqual(data['center'], [46.391390, 6.273161])
        self.assertEqual(data['zoom'], 9)
        self.assertEqual(data['maxZoom'], 24)
        self.assertEqual(data['markers'][0]['url'], '/garden/article-1')
        self.assertEqual(data['markers'][0]['icon'], 'book-image')
        self.assertEqual(data['markers'][0]['color'], 'red')
        self.assertIn('obsidian-maps.js', (self.source / '_site/home.html').read_text())

    def test_netlify_rebuild_uses_current_notes_and_base(self):
        config = tomllib.loads((self.source / 'netlify.toml').read_text())
        environment = os.environ.copy()
        environment.update(config['build']['environment'])

        def deploy_build():
            result = subprocess.run(config['build']['command'], shell=True,
                                    cwd=self.source, env=environment,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((self.source / config['build']['publish'] / 'home.html').exists())
            return self.payload()

        self.assertEqual(len(deploy_build()['markers']), 2)
        # A second deploy must read updated sources, not stale generated data.
        (self.source / '_notes/articles/article-1.md').write_text(
            '---\ncoordinates: [47, 7]\n---\n')
        (self.source / '_notes/articles/article-2.md').unlink()
        (self.source / '_notes/new-place.md').write_text(
            '---\ntitle: New place\ncoordinates: [48, 8]\n---\n')
        base = self.source / '_notes/index.base'
        base.write_text(base.read_text().replace('defaultZoom: 9', 'defaultZoom: 12'))
        data = deploy_build()
        self.assertEqual(data['zoom'], 12)
        self.assertEqual({tuple(marker['coordinates']) for marker in data['markers']},
                         {(47.0, 7.0), (48.0, 8.0)})
        self.assertEqual({marker['url'] for marker in data['markers']},
                         {'/article-1', '/new-place'})

    def test_coordinate_validation_and_safe_titles(self):
        (self.source / '_notes/articles/article-1.md').write_text('''---
coordinates: "46.5, 6.6"
title: '<img src=x onerror=alert(1)> & "quoted"'
---
''')
        (self.source / '_notes/articles/article-2.md').write_text('---\ncoordinates: [91, 6]\n---\n')
        self.build()
        data = self.payload()
        self.assertEqual(len(data['markers']), 1)
        self.assertEqual(data['markers'][0]['coordinates'], [46.5, 6.6])
        self.assertEqual(data['markers'][0]['title'], '<img src=x onerror=alert(1)> & "quoted"')

    def test_filters_fail_explicitly(self):
        base = self.source / '_notes/index.base'
        base.write_text('filters: \'file.inFolder("private")\'\n' + base.read_text())
        self.assertIn('filters are not supported', self.build(success=False))

    def test_missing_base_fails_explicitly(self):
        (self.source / '_notes/index.base').unlink()
        self.assertIn('Map base missing or ambiguous', self.build(success=False))


if __name__ == '__main__':
    unittest.main()
