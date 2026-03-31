from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Iterable

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATASET_PATH = DATA_DIR / 'synthetic_messages.csv'

NORMAL_SENDERS = [
    'practice@eisu.kz',
    'dekanat@university.kz',
    'library@university.kz',
    'teacher.portal@edu.kz',
    'it_support@campus.kz',
    'group.curator@university.kz',
    'news@studentlife.kz',
    'registrar@university.kz',
    'hr@company.local',
    'office@department.kz',
]

SUSPICIOUS_SENDERS = [
    'security-alert@verify-now.help',
    'rector.office@fast-approve.site',
    'finance@urgent-wallet.net',
    'support@account-check.info',
    'bonus@reward-center.biz',
    'helpdesk@secure-portal-login.xyz',
    'admin@access-reset-now.top',
    'boss-request@instant-action.click',
]

NORMAL_SUBJECTS = [
    'Отчёт по практике',
    'Информация о занятиях',
    'Напоминание о дедлайне',
    'Обновление расписания',
    'Проверка доступа к порталу',
    'Встреча команды',
    'Изменения в графике',
    'Поздравление',
    'Материалы к лекции',
    'Подтверждение заявки',
]

NORMAL_BODIES = [
    'Здравствуйте! Просим до конца недели загрузить обычный отчёт в портал. Если возникнут вопросы, обратитесь к куратору.',
    'Добрый день! Напоминаем, что завтра в 10:00 состоится занятие в аудитории 302. Возьмите, пожалуйста, конспект.',
    'Коллеги, прикрепляем материалы к лекции и план работ на неделю. Никаких срочных действий не требуется.',
    'Уважаемый студент! Доступ к учебному порталу работает штатно. Для смены пароля используйте внутренний кабинет.',
    'Добрый день! Просим подтвердить участие во встрече команды до пятницы через корпоративный календарь.',
    'Сообщаем, что расписание на следующую неделю обновлено. Проверьте время занятий в личном кабинете.',
    'Здравствуйте! Ваша заявка принята и будет обработана в течение двух рабочих дней.',
    'Поздравляем! Вы успешно завершили модуль. Сертификат будет доступен в системе после проверки преподавателя.',
]

MANIPULATIVE_TEMPLATES = {
    'Urgency': {
        'subjects': [
            'СРОЧНО: подтвердите аккаунт за 10 минут',
            'Немедленно ответьте на запрос руководства',
            'Последнее предупреждение по доступу',
            'Срочная проверка учётной записи',
        ],
        'bodies': [
            'Выполните действие прямо сейчас, иначе доступ будет закрыт уже сегодня. Перейдите по ссылке и подтвердите данные.',
            'У вас осталось 15 минут. Если не ответите немедленно, система автоматически заблокирует вашу учётную запись.',
            'Это срочное распоряжение. Нужен быстрый ответ без задержек, иначе последуют ограничения.',
        ],
        'keywords': ['срочно', 'немедленно', 'последнее предупреждение', '15 минут'],
    },
    'Fear': {
        'subjects': [
            'Ваша учётная запись будет заблокирована',
            'Обнаружено нарушение безопасности',
            'Риск удаления данных',
            'Возможна потеря доступа к сервису',
        ],
        'bodies': [
            'Система обнаружила подозрительную активность. Если вы не подтвердите данные, ваши файлы будут удалены.',
            'Ваш пароль считается скомпрометированным. Без немедленной проверки доступ к сервисам будет отключён.',
            'Если не пройти верификацию, возможна блокировка аккаунта и потеря всех документов.',
        ],
        'keywords': ['заблокирована', 'нарушение', 'удалены', 'потеря доступа'],
    },
    'Authority': {
        'subjects': [
            'Поручение от ректора',
            'Распоряжение финансового отдела',
            'Требование службы безопасности',
            'Запрос от руководителя проекта',
        ],
        'bodies': [
            'По распоряжению руководства отправьте код подтверждения ответным письмом. Это обязательная проверка.',
            'Служба безопасности требует незамедлительно подтвердить логин и пароль для аудита.',
            'Ректор просит без обсуждений выполнить инструкцию и переслать данные доступа.',
        ],
        'keywords': ['руководства', 'служба безопасности', 'ректор', 'обязательная проверка'],
    },
    'Greed': {
        'subjects': [
            'Вы выиграли премию',
            'Бонус доступен только сегодня',
            'Получите денежное вознаграждение',
            'Подарочный сертификат ожидает вас',
        ],
        'bodies': [
            'Поздравляем! Вам начислен бонус. Чтобы получить награду, подтвердите карту и пароль для перевода.',
            'Доступна эксклюзивная выплата. Укажите реквизиты прямо сейчас и получите деньги в течение часа.',
            'Вы выбраны для срочного вознаграждения. Подтвердите личные данные ради мгновенного бонуса.',
        ],
        'keywords': ['выиграли', 'бонус', 'вознаграждение', 'подарочный сертификат'],
    },
    'Reciprocity': {
        'subjects': [
            'Мы уже помогли вам — ответьте взаимностью',
            'Подтвердите помощь отделу',
            'Нужна небольшая услуга',
            'Просьба в ответ на ранее оказанную помощь',
        ],
        'bodies': [
            'Мы уже подготовили для вас документы, поэтому просим в ответ сообщить код из SMS для завершения операции.',
            'Коллеги помогли вам раньше, теперь нужна небольшая услуга: отправьте подтверждение входа.',
            'В знак взаимной поддержки выполните простой шаг и перешлите одноразовый код.',
        ],
        'keywords': ['помогли', 'в ответ', 'услуга', 'взаимной поддержки'],
    },
    'Scarcity': {
        'subjects': [
            'Осталось 2 места на подтверждение',
            'Предложение действует только час',
            'Последний шанс сохранить доступ',
            'Ограниченное окно верификации',
        ],
        'bodies': [
            'Окно подтверждения скоро закроется. Только первые пользователи сохранят доступ без штрафа.',
            'Доступно всего несколько мест на срочную проверку. Заполните форму немедленно.',
            'Это последнее ограниченное предложение. После окончания времени ссылка станет недоступна.',
        ],
        'keywords': ['осталось', 'только час', 'последний шанс', 'ограниченное'],
    },
}

SAFE_LINKS = [
    'https://portal.university.kz',
    'https://lms.edu.kz',
    'https://intra.company.local',
]

SUSPICIOUS_LINKS = [
    'http://verify-account-now.xyz/login',
    'http://fast-check.help/confirm',
    'https://bonus-wallet.biz/claim',
    'http://secure-reset.top/auth',
]


def _mix_case(text: str) -> str:
    parts = text.split()
    if not parts:
        return text
    idx = random.randrange(len(parts))
    parts[idx] = parts[idx].upper()
    return ' '.join(parts)



def _generate_normal_rows(n: int) -> Iterable[dict[str, str | int]]:
    for i in range(n):
        subject = random.choice(NORMAL_SUBJECTS)
        body = random.choice(NORMAL_BODIES)
        sender = random.choice(NORMAL_SENDERS)
        if random.random() < 0.35:
            body += f' Ссылка для входа: {random.choice(SAFE_LINKS)}.'
        yield {
            'id': i + 1,
            'subject': subject,
            'body': body,
            'sender': sender,
            'label': 0,
            'main_principle': 'None',
        }



def _generate_manipulative_rows(start_id: int, n: int) -> Iterable[dict[str, str | int]]:
    principles = list(MANIPULATIVE_TEMPLATES.keys())
    for i in range(n):
        principle = principles[i % len(principles)]
        tpl = MANIPULATIVE_TEMPLATES[principle]
        subject = random.choice(tpl['subjects'])
        body = random.choice(tpl['bodies'])
        sender = random.choice(SUSPICIOUS_SENDERS)
        if random.random() < 0.75:
            body += f' Перейдите по ссылке: {random.choice(SUSPICIOUS_LINKS)}.'
        if random.random() < 0.55:
            body += ' ОТВЕТ НУЖЕН СЕЙЧАС!!!'
        if random.random() < 0.25:
            subject = _mix_case(subject) + '!!!'
        yield {
            'id': start_id + i,
            'subject': subject,
            'body': body,
            'sender': sender,
            'label': 1,
            'main_principle': principle,
        }



def build_dataset(path: Path = DATASET_PATH, size: int = 300, seed: int = 42) -> Path:
    random.seed(seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    normal_count = size // 2
    manip_count = size - normal_count
    rows = list(_generate_normal_rows(normal_count))
    rows.extend(_generate_manipulative_rows(normal_count + 1, manip_count))
    random.shuffle(rows)

    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['id', 'subject', 'body', 'sender', 'label', 'main_principle'],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


if __name__ == '__main__':
    dataset_path = build_dataset()
    print(f'Датасет создан: {dataset_path}')
