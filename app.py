from __future__ import annotations

import argparse
import io
import json
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from detector import SocialEngineeringDetector
from storage import fetch_analysis, fetch_history, init_db, save_analysis

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title='SocialEng Detector')
app.mount('/static', StaticFiles(directory=BASE_DIR / 'static'), name='static')
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))

detector = SocialEngineeringDetector()
init_db()


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'report': None},
    )


@app.post('/analyze', response_class=HTMLResponse)
async def analyze(
    request: Request,
    sender: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
):
    report = detector.analyze(sender=sender, subject=subject, body=body)
    payload = asdict(report)
    analysis_id = save_analysis({**payload, 'report_json': report.to_json()})
    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'report': report, 'analysis_id': analysis_id},
    )


@app.get('/history', response_class=HTMLResponse)
async def history(request: Request):
    rows = fetch_history()
    return templates.TemplateResponse(
        request=request,
        name='history.html',
        context={'rows': rows},
    )


@app.get('/analysis/{analysis_id}', response_class=HTMLResponse)
async def analysis_details(request: Request, analysis_id: int):
    row = fetch_analysis(analysis_id)
    if row is None:
        return RedirectResponse(url='/history', status_code=303)

    report = json.loads(row['report_json'])
    return templates.TemplateResponse(
        request=request,
        name='details.html',
        context={'report': report, 'analysis_id': analysis_id, 'row': row},
    )


@app.get('/analysis/{analysis_id}/pdf')
async def export_pdf(analysis_id: int):
    row = fetch_analysis(analysis_id)
    if row is None:
        return RedirectResponse(url='/history', status_code=303)

    report = json.loads(row['report_json'])
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story = [
        Paragraph('SocialEng Detector — отчёт анализа', styles['Title']),
        Spacer(1, 12),
        Paragraph(f"<b>Отправитель:</b> {report['sender']}", styles['BodyText']),
        Paragraph(f"<b>Тема:</b> {report['subject']}", styles['BodyText']),
        Paragraph(
            f"<b>Риск:</b> {report['risk_score']} / 100 ({report['risk_level']})",
            styles['BodyText'],
        ),
        Paragraph(
            f"<b>ML-вероятность:</b> {report['ml_probability']}",
            styles['BodyText'],
        ),
        Spacer(1, 12),
        Paragraph(f"<b>Итог:</b> {report['summary']}", styles['BodyText']),
        Spacer(1, 12),
        Paragraph('<b>Сработавшие техники:</b>', styles['Heading2']),
    ]

    if report['techniques']:
        for item in report['techniques']:
            story.append(
                Paragraph(
                    f"• {item['name']} ({item['principle']}): {item['explanation']}",
                    styles['BodyText'],
                )
            )
    else:
        story.append(Paragraph('• Не обнаружены.', styles['BodyText']))

    story.extend([
        Spacer(1, 12),
        Paragraph('<b>Статистические признаки:</b>', styles['Heading2']),
    ])

    if report['statistical_findings']:
        for item in report['statistical_findings']:
            story.append(
                Paragraph(
                    f"• {item['name']}: {item['value']} — {item['explanation']}",
                    styles['BodyText'],
                )
            )
    else:
        story.append(Paragraph('• Не обнаружены.', styles['BodyText']))

    story.extend([
        Spacer(1, 12),
        Paragraph('<b>Рекомендации:</b>', styles['Heading2']),
    ])

    for rec in report['recommendations']:
        story.append(Paragraph(f'• {rec}', styles['BodyText']))

    doc.build(story)
    buffer.seek(0)
    filename = f'socialeng_report_{analysis_id}.pdf'

    return StreamingResponse(
        buffer,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


def run_cli(sender: str, subject: str, body: str) -> None:
    report = detector.analyze(sender=sender, subject=subject, body=body)

    print('\n=== SocialEng Detector ===')
    print(f'Отправитель: {report.sender}')
    print(f'Тема: {report.subject}')
    print(f'Риск: {report.risk_score}/100 ({report.risk_level})')
    print(f'ML-вероятность: {report.ml_probability}')
    print(f'Итог: {report.summary}\n')

    print('Сработавшие техники:')
    if report.techniques:
        for hit in report.techniques:
            print(f'- {hit.name} [{hit.principle}] -> {", ".join(hit.matches) or "нет совпадений"}')
            print(f'  Объяснение: {hit.explanation}')
    else:
        print('- Не обнаружены')

    print('\nСтатистические признаки:')
    if report.statistical_findings:
        for item in report.statistical_findings:
            print(f'- {item.name}: {item.value} (вес {item.weight})')
    else:
        print('- Не обнаружены')

    print('\nРекомендации:')
    for rec in report.recommendations:
        print(f'- {rec}')


def main() -> None:
    parser = argparse.ArgumentParser(description='SocialEng Detector')
    parser.add_argument('--mode', choices=['cli', 'web'], default='web')
    parser.add_argument('--sender', default='')
    parser.add_argument('--subject', default='')
    parser.add_argument('--body', default='')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()

    if args.mode == 'cli':
        if not (args.sender and args.subject and args.body):
            parser.error('Для CLI нужно передать --sender, --subject и --body')
        run_cli(sender=args.sender, subject=args.subject, body=args.body)
    else:
        import uvicorn
        uvicorn.run('app:app', host=args.host, port=args.port, reload=False)


if __name__ == '__main__':
    main()