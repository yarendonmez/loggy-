import random
from datetime import datetime, timedelta

# Büyük test dosyası oluştur
log_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL', 'DEBUG']
actions = ['User login', 'Database query', 'API request', 'File upload', 'System backup', 'Cache update', 'Memory cleanup', 'Network check', 'Security scan', 'Data sync']
errors = ['Connection timeout', 'Authentication failed', 'File not found', 'Permission denied', 'Memory overflow', 'Disk full', 'Network unreachable', 'Service unavailable']

start_time = datetime(2024, 1, 15, 10, 0, 0)
lines = []

for i in range(1000):  # 1000 satırlık dosya
    time = start_time + timedelta(minutes=i)
    
    # %15 hata, %25 warning, %60 info
    if i % 7 == 0:  # ERROR
        level = 'ERROR'
        message = f'{random.choice(errors)} - code: {random.randint(400, 599)}'
    elif i % 13 == 0:  # CRITICAL
        level = 'CRITICAL'
        message = f'System failure: {random.choice(errors)}'
    elif i % 4 == 0:  # WARNING
        level = 'WARNING'
        message = f'{random.choice(actions)} - performance degraded'
    else:  # INFO
        level = 'INFO'
        message = f'{random.choice(actions)} successful - user_id: {random.randint(100, 999)}'
    
    line = f'{time.strftime("%Y-%m-%d %H:%M:%S")} {level} {message}'
    lines.append(line)

with open('data/large_test_1000.log', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'1000 satırlık test dosyası oluşturuldu: data/large_test_1000.log')
