from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from datetime import date, timedelta, datetime

from app.db.session import get_db
from app.models.matriz import Matriz
from app.models.exame_toque import ExameToque
from app.models.toque_matriz import ToqueMatriz

router = APIRouter()


def _to_date(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, str):
        try:
            return date.fromisoformat(v[:10])
        except ValueError:
            return None
    return v


@router.get("/desempenho-reprodutivo")
def relatorio_desempenho(db: Session = Depends(get_db)):
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    # --- Dados ---
    exame = db.query(ExameToque).order_by(ExameToque.data_realizacao.desc()).first()
    data_toque = _to_date(exame.data_realizacao) if exame else date.today()

    matrizes = db.query(Matriz).filter(
        Matriz.status.notin_(['descartada', 'morta'])
    ).all()

    def sort_key(m):
        try:
            return (0, int(m.numero_registro))
        except (ValueError, TypeError):
            return (1, 0)

    matrizes.sort(key=sort_key)

    toque_map: dict[int, ToqueMatriz] = {}
    if exame:
        toques = db.query(ToqueMatriz).filter(ToqueMatriz.id_exame_toque == exame.id).all()
        toque_map = {t.id_matriz: t for t in toques}

    # --- Cores e estilos ---
    COR_VERDE    = colors.HexColor('#1a7a1e')
    COR_VERMELHO = colors.HexColor('#c62828')
    COR_AMARELO  = colors.HexColor('#FFFF00')
    COR_HEADER   = colors.HexColor('#92D050')
    COR_ALT      = colors.HexColor('#F2F7F2')

    s_center = ParagraphStyle('c',  fontSize=8, fontName='Helvetica',      alignment=TA_CENTER, leading=10)
    s_left   = ParagraphStyle('l',  fontSize=8, fontName='Helvetica',      alignment=TA_LEFT,   leading=10)
    s_hdr    = ParagraphStyle('h',  fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=10)
    s_verde  = ParagraphStyle('v',  fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=10, textColor=COR_VERDE)
    s_verm   = ParagraphStyle('x',  fontSize=8, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=10, textColor=COR_VERMELHO)
    s_title  = ParagraphStyle('tt', fontSize=15, fontName='Helvetica-Bold', alignment=TA_CENTER, leading=20, textColor=colors.black)
    s_sub    = ParagraphStyle('sb', fontSize=9,  fontName='Helvetica',      alignment=TA_LEFT,   leading=14, textColor=colors.black)

    # --- Layout da página ---
    PAGE   = landscape(A4)
    MARGIN = 15 * mm
    USABLE = PAGE[0] - 2 * MARGIN

    col_w = [16*mm, 20*mm, 36*mm, 20*mm, 24*mm, 26*mm]
    col_w.append(USABLE - sum(col_w))  # observações ocupa o restante

    # --- Cabeçalho da tabela ---
    header = [
        Paragraph('Nº\nORD.', s_hdr),
        Paragraph('Nº DE\nREG.', s_hdr),
        Paragraph('SITUAÇÃO\nATUAL', s_hdr),
        Paragraph('Nº DE\nCRIAS', s_hdr),
        Paragraph('INT/CRIA\nMESES', s_hdr),
        Paragraph('RESULT\nTOQUE', s_hdr),
        Paragraph('OBSERVAÇÕES', s_hdr),
    ]

    rows = [header]

    for i, m in enumerate(matrizes, 1):
        ultima = _to_date(m.ultima_cria_data)

        if ultima:
            ultima_str = ultima.strftime('%d/%m/%Y')
            if ultima + timedelta(days=60) < data_toque:
                sit = Paragraph(f'V  {ultima_str}', s_verde)
            else:
                sit = Paragraph(f'X  {ultima_str}', s_verm)
        else:
            sit = Paragraph('-', s_center)

        if m.media_dias_intervalo:
            intervalo = f"{m.media_dias_intervalo / 30.44:.2f}"
        else:
            intervalo = '-'

        toque = toque_map.get(m.id)
        if toque:
            res = (toque.resultado or '').lower()
            if 'vazia' in res:
                resultado = 'VZ'
            elif toque.dias_estimados_fecundacao:
                resultado = str(toque.dias_estimados_fecundacao)
            elif toque.resultado:
                resultado = toque.resultado[:8]
            else:
                resultado = 'VZ'
        else:
            resultado = 'VZ'

        rows.append([
            Paragraph(str(i), s_center),
            Paragraph(m.numero_registro, s_center),
            sit,
            Paragraph(str(m.total_crias or 0), s_center),
            Paragraph(intervalo, s_center),
            Paragraph(resultado, s_center),
            '',  # observações — espaço em branco para escrita manual
        ])

    # --- Estilo da tabela ---
    ts = TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),  COR_HEADER),
        ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE',     (0, 0), (-1, -1), 8),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING',   (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 3),
        ('LEFTPADDING',  (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    # linhas alternadas
    for idx in range(1, len(rows)):
        if idx % 2 == 0:
            ts.add('BACKGROUND', (0, idx), (-1, idx), COR_ALT)

    table = Table(rows, colWidths=col_w, repeatRows=1)
    table.setStyle(ts)

    # --- Título e sub-cabeçalho ---
    periodo_str = ''
    if exame:
        pi = _to_date(exame.periodo_inicio)
        pf = _to_date(exame.periodo_fim)
        if pi and pf:
            periodo_str = f"{pi.strftime('%d/%m/%y')} à {pf.strftime('%d/%m/%y')}"

    toque_str = data_toque.strftime('%d/%m/%Y') if data_toque else ''

    title_table = Table(
        [[Paragraph('DESEMPENHO REPRODUTIVO DE MATRIZES', s_title)]],
        colWidths=[USABLE],
    )
    title_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), COR_AMARELO),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX',           (0, 0), (-1, -1), 1, colors.black),
    ]))

    sub_text = f'<b>DATA DO TOQUE:</b>   {toque_str}      <b>FAZENDA ALMAS</b>      {periodo_str}'

    # --- Montar documento ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=PAGE,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
    )

    story = [
        title_table,
        Spacer(1, 3 * mm),
        Paragraph(sub_text, s_sub),
        Spacer(1, 4 * mm),
        table,
    ]

    doc.build(story)
    buffer.seek(0)

    filename = f"desempenho_reprodutivo_{toque_str.replace('/', '')}.pdf"
    return StreamingResponse(
        buffer,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )
