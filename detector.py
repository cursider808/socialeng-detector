from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

from ml_model import load_or_train_model

CIALDINI_MAP = {
    'Urgency': 'Давление временем / urgency',
    'Fear': 'Страх потери',
    'Authority': 'Авторитет',
    'Greed': 'Выгода',
    'Reciprocity': 'Взаимность',
    'Scarcity': 'Дефицит',
}

SUSPICIOUS_TLDS = {'.xyz', '.top', '.click', '.help', '.biz', '.info', '.site'}
TRUSTED_DOMAINS = {'university.kz', 'edu.kz', 'company.local', 'campus.kz'}

PATTERNS = {
    'Urgency': {
        'weight': 14,
        'explanation': 'Сообщение давит по времени и подталкивает действовать без проверки.',
        'recommendation': 'Сделайте паузу и подтвердите запрос через официальный канал.',
        'patterns': [
            r'срочно',
            r'немедленно',
            r'прямо сейчас',
            r'последн(ее|ий) предупреждение',
            r'осталось \d+ минут',
            r'ответ нужен сейчас',
        ],
    },
    'Fear': {
        'weight': 13,
        'explanation': 'Используется страх блокировки, потери доступа или удаления данных.',
        'recommendation': 'Не верьте угрозам из письма. Проверьте статус аккаунта в официальной системе.',
        'patterns': [
            r'заблок',
            r'нарушени',
            r'удален',
            r'потеря доступа',
            r'скомпрометирован',
            r'штраф',
        ],
    },
    'Authority': {
        'weight': 15,
        'explanation': 'Автор письма ссылается на руководителя, ректора или службу безопасности.',
        'recommendation': 'Проверьте личность отправителя через известный вам номер или корпоративный каталог.',
        'patterns': [
            r'руководств',
            r'ректор',
            r'служба безопасности',
            r'финансов(ый|ого) отдел',
            r'обязательн(ая|ое) проверк',
            r'без обсуждений',
        ],
    },
    'Greed': {
        'weight': 10,
        'explanation': 'Обещается бонус, приз или денежная выгода за быстрое действие.',
        'recommendation': 'Не передавайте данные ради обещанной выгоды. Сначала проверьте источник предложения.',
        'patterns': [
            r'бонус',
            r'выиграл',
            r'вознаграждени',
            r'подарочн',
            r'выплат',
            r'деньги',
        ],
    },
    'Reciprocity': {
        'weight': 9,
        'explanation': 'Манипуляция строится на идее долга: мы помогли вам, теперь помогите нам.',
        'recommendation': 'Даже если просьба выглядит дружелюбно, проверяйте её отдельно и не сообщайте коды.',
        'patterns': [
            r'мы уже помогли',
            r'в ответ',
            r'небольшая услуга',
            r'взаимн',
            r'коллеги помогли',
        ],
    },
    'Scarcity': {
        'weight': 9,
        'explanation': 'Создаётся ощущение редкости или ограниченного окна времени.',
        'recommendation': 'Не принимайте решения под давлением “последнего шанса”.',
        'patterns': [
            r'последний шанс',
            r'ограниченн',
            r'осталось \d+',
            r'только сегодня',
            r'только час',
        ],
    },
}

URL_RE = re.compile(r'https?://[^\s]+', re.IGNORECASE)


@dataclass
class TechniqueHit:
    name: str
    principle: str
    weight: int
    explanation: str
    recommendation: str
    matches: list[str]


@dataclass
class StatisticalFinding:
    name: str
    value: float | int | str
    weight: int
    explanation: str


@dataclass
class AnalysisReport:
    sender: str
    subject: str
    body: str
    risk_score: int
    risk_level: str
    ml_probability: float
    label_prediction: int
    techniques: list[TechniqueHit]
    statistical_findings: list[StatisticalFinding]
    recommendations: list[str]
    summary: str

    def to_json(self) -> str:
        payload = asdict(self)
        return json.dumps(payload, ensure_ascii=False, indent=2)


class SocialEngineeringDetector:
    def __init__(self) -> None:
        self.model = load_or_train_model()

    @staticmethod
    def _normalize_text(sender: str, subject: str, body: str) -> str:
        return f'{sender} {subject} {body}'.strip().lower()

    def _heuristic_hits(self, sender: str, subject: str, body: str) -> list[TechniqueHit]:
        text = self._normalize_text(sender, subject, body)
        hits: list[TechniqueHit] = []
        for name, config in PATTERNS.items():
            matches: list[str] = []
            for pattern in config['patterns']:
                found = re.findall(pattern, text, flags=re.IGNORECASE)
                if found:
                    if isinstance(found[0], tuple):
                        flat = [' '.join(part for part in item if part) for item in found]
                        matches.extend(flat)
                    else:
                        matches.extend(found)
            if matches:
                hits.append(
                    TechniqueHit(
                        name=name,
                        principle=CIALDINI_MAP[name],
                        weight=config['weight'],
                        explanation=config['explanation'],
                        recommendation=config['recommendation'],
                        matches=sorted(set(matches)),
                    )
                )
        return hits

    def _extract_domain_risk(self, value: str) -> tuple[int, str]:
        if '@' in value:
            domain = value.split('@', 1)[1].lower()
        else:
            domain = urlparse(value).netloc.lower()
        for trusted in TRUSTED_DOMAINS:
            if domain.endswith(trusted):
                return 0, domain
        suffix = next((tld for tld in SUSPICIOUS_TLDS if domain.endswith(tld)), '')
        if suffix:
            return 8, domain
        if domain and '.' in domain:
            return 4, domain
        return 0, domain

    def _statistical_findings(self, sender: str, subject: str, body: str) -> list[StatisticalFinding]:
        findings: list[StatisticalFinding] = []
        text = f'{subject} {body}'.strip()
        exclamations = text.count('!')
        uppercase_letters = sum(1 for ch in text if ch.isupper())
        letters = sum(1 for ch in text if ch.isalpha()) or 1
        uppercase_ratio = uppercase_letters / letters
        urls = URL_RE.findall(text)
        sender_weight, sender_domain = self._extract_domain_risk(sender)

        if exclamations >= 3:
            findings.append(
                StatisticalFinding(
                    name='Много восклицательных знаков',
                    value=exclamations,
                    weight=6,
                    explanation='Избыточная эмоциональность часто используется для давления.',
                )
            )
        if uppercase_ratio >= 0.22:
            findings.append(
                StatisticalFinding(
                    name='Высокая доля заглавных букв',
                    value=round(uppercase_ratio, 3),
                    weight=5,
                    explanation='Текст визуально давит и имитирует срочность.',
                )
            )
        if urls:
            findings.append(
                StatisticalFinding(
                    name='Найдены ссылки',
                    value=len(urls),
                    weight=min(7, 2 + len(urls) * 2),
                    explanation='Социальная инженерия часто переводит жертву на внешний ресурс.',
                )
            )
            for url in urls[:3]:
                url_weight, domain = self._extract_domain_risk(url)
                if url_weight:
                    findings.append(
                        StatisticalFinding(
                            name='Подозрительный домен ссылки',
                            value=domain,
                            weight=url_weight,
                            explanation='Домен ссылки не похож на корпоративный и выглядит нетипично.',
                        )
                    )
        if sender_weight:
            findings.append(
                StatisticalFinding(
                    name='Подозрительный домен отправителя',
                    value=sender_domain,
                    weight=sender_weight,
                    explanation='Адрес отправителя не соответствует ожидаемому домену организации.',
                )
            )
        return findings

    def analyze(self, sender: str, subject: str, body: str) -> AnalysisReport:
        heuristics = self._heuristic_hits(sender, subject, body)
        stats = self._statistical_findings(sender, subject, body)

        combined_text = f'{sender} {subject} {body}'.strip()
        ml_prob = float(self.model.predict_proba([combined_text])[0][1])
        label_prediction = int(ml_prob >= 0.5)

        heuristic_score = sum(hit.weight for hit in heuristics)
        stats_score = sum(item.weight for item in stats)
        ml_score = round(ml_prob * 35)
        risk_score = min(100, heuristic_score + stats_score + ml_score)

        if risk_score >= 75:
            risk_level = 'Высокий'
        elif risk_score >= 45:
            risk_level = 'Средний'
        else:
            risk_level = 'Низкий'

        recommendations = [
            'Не переходите по ссылкам и не открывайте вложения, пока не проверите отправителя.',
            'Не передавайте пароли, одноразовые коды и персональные данные в ответ на сообщение.',
            'Проверьте запрос через официальный канал: сайт, корпоративный телефон или внутренний портал.',
        ]
        for hit in heuristics:
            if hit.recommendation not in recommendations:
                recommendations.append(hit.recommendation)

        if risk_level == 'Высокий':
            summary = 'Сообщение похоже на попытку социальной инженерии и требует обязательной независимой проверки.'
        elif risk_level == 'Средний':
            summary = 'В сообщении есть подозрительные признаки. Нужна дополнительная проверка источника и содержания.'
        else:
            summary = 'Выраженных признаков социальной инженерии мало, но базовая проверка отправителя всё равно рекомендуется.'

        return AnalysisReport(
            sender=sender,
            subject=subject,
            body=body,
            risk_score=risk_score,
            risk_level=risk_level,
            ml_probability=round(ml_prob, 4),
            label_prediction=label_prediction,
            techniques=heuristics,
            statistical_findings=stats,
            recommendations=recommendations,
            summary=summary,
        )


def report_to_dict(report: AnalysisReport) -> dict[str, Any]:
    return asdict(report)
