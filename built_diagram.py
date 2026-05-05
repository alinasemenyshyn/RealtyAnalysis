import sqlite3
import plotly.graph_objects as go

with sqlite3.connect('result_by_AI.db') as conn:
    conn.execute("ATTACH DATABASE 'pages.db' AS pages_db")

    data = conn.execute('''
                        SELECT p.publication_data, r.percent_scam, r.verdict
                        FROM results_analyse r
                                 JOIN pages_db.pages p ON r.page_id = p.id
                        ORDER BY p.publication_data
                        ''').fetchall()

dates = [row[0] for row in data]
percents = [row[1] for row in data]
verdicts = [row[2] for row in data]

colors = ['#e74c3c' if p >= 50 else '#f39c12' if p >= 20 else '#2ecc71' for p in percents]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=percents,
    mode='lines+markers',
    marker=dict(color=colors, size=10),
    line=dict(color='#3498db'),
    text=verdicts,
    hovertemplate='<b>Дата:</b> %{x}<br><b>Ризик:</b> %{y}%<br><b>Вердикт:</b> %{text}<extra></extra>'
))

fig.update_layout(
    title='Тренд шахрайства по датах публікації',
    xaxis_title='Дата публікації',
    yaxis_title='Відсоток ризику (%)',
    yaxis=dict(range=[0, 100])
)

fig.show()