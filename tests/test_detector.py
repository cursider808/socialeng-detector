from __future__ import annotations

import unittest

from detector import SocialEngineeringDetector


class DetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = SocialEngineeringDetector()

    def test_normal_message_low_risk(self) -> None:
        report = self.detector.analyze(
            sender='dekanat@university.kz',
            subject='Информация о занятиях',
            body='Добрый день! Напоминаем, что завтра в 10:00 состоится пара в аудитории 302.',
        )
        self.assertLess(report.risk_score, 45)

    def test_manipulative_message_high_risk(self) -> None:
        report = self.detector.analyze(
            sender='security-alert@verify-now.help',
            subject='СРОЧНО: подтвердите аккаунт!!!',
            body='Немедленно перейдите по ссылке http://verify-account-now.xyz/login иначе доступ будет заблокирован!!!',
        )
        self.assertGreaterEqual(report.risk_score, 70)
        self.assertTrue(report.techniques)

    def test_authority_heuristic(self) -> None:
        report = self.detector.analyze(
            sender='boss-request@instant-action.click',
            subject='Поручение от ректора',
            body='По распоряжению руководства перешлите код подтверждения без обсуждений.',
        )
        names = {hit.name for hit in report.techniques}
        self.assertIn('Authority', names)


if __name__ == '__main__':
    unittest.main()
