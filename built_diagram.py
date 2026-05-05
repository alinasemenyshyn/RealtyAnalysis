import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_data(filter_date=None):
    with sqlite3.connect('result_by_AI.db') as conn:
        conn.execute("ATTACH DATABASE 'pages.db' AS pages_db")

        if filter_date:
            rows = conn.execute('''
                SELECT p.publication_data, p.price, r.percent_scam, r.verdict, r.analysed_at, r.page_id
                FROM results_analyse r
                JOIN pages_db.pages p ON r.page_id = p.id
                WHERE DATE(r.analysed_at) = ?
                ORDER BY p.publication_data
            ''', (filter_date,)).fetchall()
        else:
            rows = conn.execute('''
                SELECT p.publication_data, p.price, r.percent_scam, r.verdict, r.analysed_at, r.page_id
                FROM results_analyse r
                JOIN pages_db.pages p ON r.page_id = p.id
                WHERE DATE(r.analysed_at) = (SELECT DATE(MAX(analysed_at)) FROM results_analyse)
                ORDER BY p.publication_data
            ''').fetchall()

    return [
        {'date': row[0], 'price': row[1], 'percent_scam': row[2],
         'verdict': row[3], 'analysed_at': row[4], 'page_id': row[5]}
        for row in rows
    ]


def build_figure(data):
    dates    = [d['date']         for d in data]
    percents = [d['percent_scam'] for d in data]
    prices   = [d['price']        for d in data]
    verdicts = [d['verdict']      for d in data]

    def color(p):
        return '#e74c3c' if p >= 51 else '#f39c12' if p >= 21 else '#2ecc71'

    colors = [color(p) for p in percents]
    avg = round(sum(percents) / len(percents), 1) if percents else 0

    verdict_counts = {}
    for v in verdicts:
        verdict_counts[v] = verdict_counts.get(v, 0) + 1

    pie_colors = []
    for label in verdict_counts:
        if label == 'Шахрайство':
            pie_colors.append('#e74c3c')
        elif label == 'Сумнівно':
            pie_colors.append('#f39c12')
        else:
            pie_colors.append('#2ecc71')

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Тренд ризику по датах публікації',
            'Розподіл вердиктів',
            'Ціна vs Ризик шахрайства',
            'Ризик по кожному оголошенню',
        ),
        specs=[[{'type': 'scatter'}, {'type': 'pie'}],
               [{'type': 'scatter'}, {'type': 'bar'}]],
        vertical_spacing=0.18,
        horizontal_spacing=0.1,
    )

    fig.add_trace(go.Scatter(
        x=dates, y=percents, mode='lines+markers',
        marker=dict(color=colors, size=10, line=dict(width=1, color='white')),
        line=dict(color='#3498db', width=2),
        text=verdicts,
        hovertemplate='<b>Дата:</b> %{x}<br><b>Ризик:</b> %{y}%<br><b>Вердикт:</b> %{text}<extra></extra>',
        name='Ризик %',
    ), row=1, col=1)

    fig.add_hline(y=avg, line_dash='dash', line_color='gray',
                  annotation_text=f'Середнє: {avg}%',
                  annotation_position='right', row=1, col=1)

    fig.add_trace(go.Pie(
        labels=list(verdict_counts.keys()),
        values=list(verdict_counts.values()),
        marker_colors=pie_colors,
        textinfo='label+percent', hole=0.35,
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=prices, y=percents, mode='markers',
        marker=dict(color=colors, size=12, opacity=0.8),
        text=verdicts,
        hovertemplate='<b>Ціна:</b> $%{x:,}<br><b>Ризик:</b> %{y}%<br><b>Вердикт:</b> %{text}<extra></extra>',
        name='Ціна vs Ризик',
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=[f'#{i+1}' for i in range(len(percents))],
        y=percents, marker_color=colors,
        text=percents, textposition='outside',
        hovertemplate='<b>Оголошення:</b> %{x}<br><b>Ризик:</b> %{y}%<extra></extra>',
        name='Ризик %',
    ), row=2, col=2)

    fig.update_layout(
        title=dict(
            text=f'Аналіз нерухомості — {len(data)} оголошень | Середній ризик: {avg}%',
            font=dict(size=16),
        ),
        showlegend=False, height=750,
        paper_bgcolor='white', plot_bgcolor='#f8f9fa',
    )
    fig.update_xaxes(title_text='Дата публікації', row=1, col=1, showgrid=True, gridcolor='#eee')
    fig.update_yaxes(title_text='Ризик (%)', range=[0, 105], row=1, col=1)
    fig.update_xaxes(title_text='Ціна (USD)', row=2, col=1)
    fig.update_yaxes(title_text='Ризик (%)', range=[0, 105], row=2, col=1)
    fig.update_xaxes(title_text='Оголошення', row=2, col=2)
    fig.update_yaxes(title_text='Ризик (%)', range=[0, 115], row=2, col=2)

    return fig


if __name__ == '__main__':
    data = get_data()
    fig = build_figure(data)
    fig.show()