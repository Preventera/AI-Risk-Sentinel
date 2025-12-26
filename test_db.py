import psycopg2
try:
    conn = psycopg2.connect(
        host='127.0.0.1',
        port=5432,
        user='ai_sentinel',
        password='sentinel_secure_2024',
        dbname='ai_risk_sentinel'
    )
    print('Connected successfully!')
    cur = conn.cursor()
    cur.execute('SELECT version();')
    print(cur.fetchone())
    conn.close()
except Exception as e:
    print(f'Error type: {type(e).__name__}')
    print(f'Error: {e}')
