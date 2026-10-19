import copy
import json
import unittest
from pathlib import Path
from page_contract import apply_contract, load_dates, verify_contract

ROOT = Path(__file__).resolve().parents[1]

class PageContractTests(unittest.TestCase):
    def setUp(self):
        self.editorial = json.loads((ROOT/'concepts/editorial/01.json').read_text())
        self.page = (ROOT/'concepts/01/index.html').read_text()

    def test_duplicate_and_body_metadata_are_rejected(self):
        for bad in [
            self.page.replace('</head>', '<meta name="description" content="duplicate"></head>'),
            self.page.replace('<meta name="robots" content="noindex,follow">', '').replace('</body>', '<meta name="robots" content="noindex,follow"></body>'),
            self.page.replace('rel="canonical"', 'rel="alternate"'),
        ]:
            with self.subTest(page=bad[:60]), self.assertRaises(AssertionError):
                verify_contract(bad, self.editorial)

    def test_global_update_date_does_not_refresh_evidence_or_publication(self):
        template = '<html><head></head><body><h1>단지명</h1><p>확인일 2026.10.07 · 2026년 6월 5일 공고 · 2028년 9월 입주 예정 · 494,000,000원</p><footer></footer></body></html>'
        dates = load_dates()
        before = apply_contract(template, self.editorial, dates)
        dates = copy.deepcopy(dates); dates['page_updated_at'] = '2026-10-20'
        after = apply_contract(template, self.editorial, dates)
        self.assertIn('datetime="2026-10-20"', after)
        self.assertIn('data-date-kind="record" datetime="2026-10-07"', after)
        self.assertEqual(before.replace('2026-10-19','2026-10-20').replace('2026.10.19','2026.10.20'), after)
        self.assertNotIn('운영 배포일', after)

if __name__ == '__main__': unittest.main()
