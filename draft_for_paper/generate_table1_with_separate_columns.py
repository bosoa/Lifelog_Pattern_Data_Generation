"""
Table 1 생성: 데이터셋 기본 특성 (타겟별 특징변수 통계를 별도 컬럼으로)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("Table 1: 데이터셋 기본 특성 생성 (타겟별 컬럼 구분)")
print("=" * 70)

# 계산된 통계 로드
stats_dir = Path("figures/phenotyping")
stats_data = {}

for target in ['anxiety', 'depression', 'stress']:
    file_path = stats_dir / f'{target}_feature_statistics.csv'
    if file_path.exists():
        df_stats = pd.read_csv(file_path)
        stats_data[target] = df_stats
        print(f"✓ {target} 통계 로드: {len(df_stats)}개 특징")

# 특징변수 그룹 (실제 데이터에 있는 것만)
feature_info = {
    '수면 지표': [
        ('total_sleep', '총 수면시간', 'min'),
        ('rem_sleep', 'REM 수면', 'min'),
    ],
    '심혈관 지표': [
        ('heart_beat', '심박수', 'bpm'),
        ('hrv', '심박변이도', 'ms'),
    ],
    '활동 지표': [
        ('walk', '걸음수', 'steps'),
        ('stick_sensor', '센서 활동', 'count'),
    ],
    '대사/체온 지표': [
        ('body_temperature', '체온', '°C'),
        ('skin_temperature', '피부온도', '°C'),
    ],
    '기타': [
        ('oxygen_saturation', '산소포화도', '%'),
    ]
}

# 데이터셋 정보 (4컬럼: 특성, Anxiety, Depression, Stress)
data = {
    '특성 (Characteristics)': [
        '전체 샘플 수 (명)',
        '',
        '타겟별 분포',
        '  Train',
        '  Validation',
        '  Test',
        '  이벤트 비율 (%)',
        '',
        '특징 변수',
        '(정상군 → 이벤트군)',
    ],
    'Anxiety': [
        '281,138',
        '',
        '',
        '176,160 (62.7%)',
        '50,332 (17.9%)',
        '25,166 (8.9%)',
        '6.6',
        '',
        '',
        '',
    ],
    'Depression': [
        '',
        '',
        '',
        '10,358 (3.7%)',
        '2,960 (1.1%)',
        '1,480 (0.5%)',
        '47.4',
        '',
        '',
        '',
    ],
    'Stress': [
        '',
        '',
        '',
        '10,276 (3.7%)',
        '2,937 (1.0%)',
        '1,469 (0.5%)',
        '24.6',
        '',
        '',
        '',
    ]
}

# 특징변수별 통계 추가
for group_name, features in feature_info.items():
    # 그룹 헤더
    data['특성 (Characteristics)'].append(f'  - {group_name}')
    data['Anxiety'].append('')
    data['Depression'].append('')
    data['Stress'].append('')

    # 각 특징
    for feature_id, feature_name, unit in features:
        # 특징 이름
        data['특성 (Characteristics)'].append(f'    • {feature_name}')

        # 각 타겟별 통계
        for target in ['anxiety', 'depression', 'stress']:
            target_col = target.capitalize()

            if target in stats_data:
                df_target = stats_data[target]
                row = df_target[df_target['Feature'] == feature_id]

                if not row.empty:
                    normal_mean = row.iloc[0]['Normal_Mean']
                    event_mean = row.iloc[0]['Event_Mean']

                    # 소수점 자리수 결정
                    if unit == '%':
                        value_text = f"{normal_mean:.1f} → {event_mean:.1f} {unit}"
                    elif unit in ['min', 'steps', 'count']:
                        value_text = f"{normal_mean:.0f} → {event_mean:.0f} {unit}"
                    else:  # bpm, ms, °C
                        value_text = f"{normal_mean:.1f} → {event_mean:.1f} {unit}"

                    data[target_col].append(value_text)
                else:
                    data[target_col].append('N/A')
            else:
                data[target_col].append('N/A')

    # 그룹 간 빈 줄
    data['특성 (Characteristics)'].append('')
    data['Anxiety'].append('')
    data['Depression'].append('')
    data['Stress'].append('')

# 총 특징 변수 수
data['특성 (Characteristics)'].append('  총 특징 변수 (개)')
data['Anxiety'].append('9')
data['Depression'].append('9')
data['Stress'].append('9')

data['특성 (Characteristics)'].append('')
data['Anxiety'].append('')
data['Depression'].append('')
data['Stress'].append('')

# 데이터 전처리
data['특성 (Characteristics)'].extend([
    '데이터 전처리',
    '  - 결측치 처리',
    '  - 이상치 처리',
    '  - 표준화 방법',
])
data['Anxiety'].extend([
    '',
    '중앙값 대체',
    'IQR 기반 클리핑',
    'StandardScaler',
])
data['Depression'].extend([
    '',
    '(Median imputation)',
    '(Q1-1.5×IQR, Q3+1.5×IQR)',
    '(μ=0, σ=1)',
])
data['Stress'].extend([
    '',
    '',
    '',
    '',
])

df = pd.DataFrame(data)

# 그림 생성 (더 넓게)
fig, ax = plt.subplots(figsize=(18, 14))
ax.axis('tight')
ax.axis('off')

# 테이블 생성 (4컬럼)
table = ax.table(
    cellText=df.values,
    colLabels=['특성 (Characteristics)', 'Anxiety', 'Depression', 'Stress'],
    cellLoc='left',
    loc='center',
    colWidths=[0.35, 0.22, 0.22, 0.21]
)

table.auto_set_font_size(False)
table.set_fontsize(8.5)
table.scale(1, 2.0)

# 헤더 스타일
for i in range(4):
    cell = table[(0, i)]
    cell.set_facecolor('#667eea')
    cell.set_text_props(weight='bold', color='white', ha='center' if i > 0 else 'left')
    cell.set_height(0.08)

# 섹션 찾기
section_rows = []
subsection_rows = []
feature_group_rows = []

for i, text in enumerate(df['특성 (Characteristics)']):
    if text in ['전체 샘플 수 (명)', '타겟별 분포', '특징 변수', '데이터 전처리']:
        section_rows.append(i)
    elif text == '(정상군 → 이벤트군)':
        subsection_rows.append(i)
    elif text.startswith('  - ') and not text.startswith('    •'):
        feature_group_rows.append(i)

# 행 스타일링
for i in range(len(df)):
    for j in range(4):
        cell = table[(i+1, j)]

        # 섹션 헤더
        if i in section_rows:
            cell.set_facecolor('#e8eaf6')
            if j == 0:
                cell.set_text_props(weight='bold', fontsize=10)
            else:
                cell.set_text_props(ha='center')

        # 서브섹션
        elif i in subsection_rows:
            cell.set_facecolor('#f3f4f9')
            cell.set_text_props(fontsize=8, style='italic', ha='center' if j > 0 else 'left')

        # 특징변수 그룹
        elif i in feature_group_rows:
            cell.set_facecolor('#f8f9fa')
            if j == 0:
                cell.set_text_props(weight='bold', fontsize=9)

        # 일반 행
        else:
            if i % 2 == 0:
                cell.set_facecolor('#ffffff')
            else:
                cell.set_facecolor('#fafafa')

            # 통계 값 중앙 정렬
            if j > 0 and '→' in str(df.iloc[i, j]):
                cell.set_text_props(ha='center')

        # 빈 행
        if df.iloc[i, 0] == '':
            cell.set_facecolor('#ffffff')
            cell.set_height(0.015)

        # 들여쓰기된 항목
        if df.iloc[i, 0].startswith('    •'):
            if j == 0:
                cell.set_text_props(fontsize=8.5)
            else:
                cell.set_text_props(fontsize=8)

        # Train/Validation/Test 행 중앙 정렬
        if df.iloc[i, 0].strip() in ['Train', 'Validation', 'Test', '이벤트 비율 (%)']:
            if j > 0:
                cell.set_text_props(ha='center')

# 제목
title = fig.text(0.5, 0.97, 'Table 1: 데이터셋의 기본 특성 및 타겟별 특징변수 통계 (N=281,138)',
                ha='center', va='top',
                fontsize=14, fontweight='bold')

subtitle = fig.text(0.5, 0.945,
                   'Basic Characteristics and Target-Specific Feature Statistics (N=281,138)',
                   ha='center', va='top',
                   fontsize=11, color='#666')

# 각주
footnote = fig.text(0.1, 0.02,
                   '주: KLOSDOM (Korea Lifelog Observatory for Sustainable Dementia Outcome Management) 전처리 데이터셋 (version 20260622)\n' +
                   '이벤트: 셀프체크 점수 ≥ 4점으로 정의. 특징변수는 정상군(score<4) 평균 → 이벤트군(score≥4) 평균 형식으로 표시.',
                   ha='left', va='bottom',
                   fontsize=8, color='#666', style='italic')

plt.tight_layout(rect=[0, 0.05, 1, 0.94])

# 저장
output_dir = Path("figures/phenotyping")
output_file = output_dir / 'table1_dataset_characteristics_with_stats.png'

plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Table 1 이미지 저장: {output_file}")
print(f"  크기: {output_file.stat().st_size / 1024:.1f} KB")

plt.close()

# CSV로도 저장
csv_file = output_dir / 'table1_dataset_characteristics_with_stats.csv'
df.to_csv(csv_file, index=False, encoding='utf-8-sig')
print(f"✓ Table 1 CSV 저장: {csv_file}")

print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
