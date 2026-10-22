import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'


class Assets(HTMLParser):
    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        for name, value in attributes.items():
            if name.startswith('on'):
                raise AssertionError('Inline executable attribute')
            if name in {'src', 'href'} and value.startswith('./'):
                assert (SITE / value[2:]).is_file(), value
        if tag == 'script':
            assert attributes.get('src'), 'Inline script'


Assets().feed((SITE / 'index.html').read_text(encoding='utf-8'))
evidence = json.loads((SITE / 'evidence.json').read_text(encoding='utf-8'))
assert {s['id'] for s in evidence['scenarios']} == {'success', 'pending', 'race', 'permission'}
for case in evidence['scenarios']:
    assert case['done_calls'] == (1 if case['id'] == 'success' else 0)
    if case['id'] != 'permission':
        assert case['fixture']['before_exit'] != 0 and case['fixture']['after_exit'] == 0
assert 'test doubles' in evidence['scope']
print('PASS: asset references, executable markup and recorded outcomes.')
