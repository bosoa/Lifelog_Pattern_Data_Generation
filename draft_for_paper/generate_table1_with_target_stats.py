"""
Table 1 생성: 데이터셋 기본 특성 (타겟별 특징변수 통계 포함)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("Table 1: 데이터셋 기본 특성 생성 (타겟별 통계 포함)")
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

# 데이터셋 정보
data = {
    '특성 (Characteristics)': [
        '전체 샘플 수 (명)',
        '',
        '타겟별 분포',
        '  - Anxiety',
        '    • Train',
        '    • Validation',
        '    • Test',
        '    • 이벤트 비율 (%)',
        '',
        '  - Depression',
        '    • Train',
        '    • Validation',
        '    • Test',
        '    • 이벤트 비율 (%)',
        '',
        '  - Stress',
        '    • Train',
        '    • Validation',
        '    • Test',
        '    • 이벤트 비율 (%)',
        '',
        '특징 변수 (타겟별 평균: 정상군 → 이벤트군)',
    ],
    '값': [
        '281,138',
        '',
        '',
        '',
        '176,160 (62.7%)',
        '50,332 (17.9%)',
        '25,166 (8.9%)',
        '6.6',
        '',
        '',
        '10,358 (3.7%)',
        '2,960 (1.1%)',
        '1,480 (0.5%)',
        '47.4',
        '',
        '',
        '10,276 (3.7%)',
        '2,937 (1.0%)',
        '1,469 (0.5%)',
        '24.6',
        '',
        '',
    ]
}

# 특징변수별 통계 추가
for group_name, features in feature_info.items():
    # 그룹 헤더
    data['특성 (Characteristics)'].append(f'  - {group_name}')
    data['값'].append('')

    # 각 특징
    for feature_id, feature_name, unit in features:
        # 특징 이름
        data['특성 (Characteristics)'].append(f'    • {feature_name}')

        # 세 타겟의 통계를 한 줄에
        stats_text = []
        for target in ['anxiety', 'depression', 'stress']:
            if target in stats_data:
                df_target = stats_data[target]
                row = df_target[df_target['Feature'] == feature_id]
                if not row.empty:
                    normal_mean = row.iloc[0]['Normal_Mean']
                    event_mean = row.iloc[0]['Event_Mean']

                    # 타겟 약자
                    target_abbr = {'anxiety': 'Anx', 'depression': 'Dep', 'stress': 'Str'}[target]

                    # 소수점 자리수 결정
                    if unit == '%':
                        stats_text.append(f"{target_abbr}: {normal_mean:.1f}→{event_mean:.1f}")
                    elif unit in ['min', 'steps', 'count']:
                        stats_text.append(f"{target_abbr}: {normal_mean:.0f}→{event_mean:.0f}")
                    else:  # bpm, ms, °C
                        stats_text.append(f"{target_abbr}: {normal_mean:.1f}→{event_mean:.1f}")

        value_text = ' | '.join(stats_text) + f' {unit}'
        data['값'].append(value_text)

    # 그룹 간 빈 줄
    data['특성 (Characteristics)'].append('')
    data['값'].append('')

# 총 특징 변수 수
data['특성 (Characteristics)'].append('  - 총 특징 변수 (개)')
data['값'].append('9')
data['특성 (Characteristics)'].append('')
data['값'].append('')

# 데이터 전처리
data['특성 (Characteristics)'].extend([
    '데이터 전처리',
    '  - 결측치 처리',
    '  - 이상치 처리',
    '  - 표준화 방법',
])
data['값'].extend([
    '',
    '중앙값 대체 (Median imputation)',
    'IQR 기반 클리핑 (Q1-1.5×IQR, Q3+1.5×IQR)',
    'StandardScaler (μ=0, σ=1)',
])

df = pd.DataFrame(data)

# 그림 생성
fig, ax = plt.subplots(figsize=(16, 14))
ax.axis('tight')
ax.axis('off')

# 테이블 생성
table = ax.table(
    cellText=df.values,
    colLabels=['특성 (Characteristics)', '값'],
    cellLoc='left',
    loc='center',
    colWidths=[0.45, 0.55]
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2.0)

# 헤더 스타일
for i in range(2):
    cell = table[(0, i)]
    cell.set_facecolor('#667eea')
    cell.set_text_props(weight='bold', color='white', ha='center')
    cell.set_height(0.08)

# 섹션 찾기
section_rows = []
subsection_rows = []
feature_group_rows = []

for i, text in enumerate(df['특성 (Characteristics)']):
    if text in ['전체 샘플 수 (명)', '타겟별 분포', '특징 변수 (타겟별 평균: 정상군 → 이벤트군)', '데이터 전처리']:
        section_rows.append(i)
    elif text.startswith('  - ') and not text.startswith('    •'):
        if 'Anxiety' in text or 'Depression' in text or 'Stress' in text:
            subsection_rows.append(i)
        else:
            feature_group_rows.append(i)

# 행 스타일링
for i in range(len(df)):
    for j in range(2):
        cell = table[(i+1, j)]

        # 섹션 헤더
        if i in section_rows:
            cell.set_facecolor('#e8eaf6')
            if j == 0:
                cell.set_text_props(weight='bold', fontsize=10)

        # 하위섹션 (Anxiety, Depression, Stress)
        elif i in subsection_rows:
            cell.set_facecolor('#f3f4f9')
            if j == 0:
                cell.set_text_props(weight='bold', fontsize=9)

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

        # 빈 행
        if df.iloc[i, 0] == '':
            cell.set_facecolor('#ffffff')
            cell.set_height(0.015)

        # 들여쓰기된 항목 (작은 글씨)
        if df.iloc[i, 0].startswith('    •'):
            if j == 0:
                cell.set_text_props(fontsize=8)
            else:
                cell.set_text_props(fontsize=7.5)

# 제목
title = fig.text(0.5, 0.97, 'Table 1: 데이터셋의 기본 특성 및 타겟별 특징변수 통계 (N=281,138)',
                ha='center', va='top',
                fontsize=13, fontweight='bold')

subtitle = fig.text(0.5, 0.945,
                   'Basic Characteristics and Target-Specific Feature Statistics (N=281,138)',
                   ha='center', va='top',
                   fontsize=10, color='#666')

# 각주
footnote = fig.text(0.1, 0.02,
                   '주: KLOSDOM (Korea Lifelog Observatory for Sustainable Dementia Outcome Management) 전처리 데이터셋 (version 20260622)\n' +
                   '이벤트: 셀프체크 점수 ≥ 4점으로 정의. 특징변수 평균값은 정상군(score<4) → 이벤트군(score≥4) 순으로 표시.\n' +
                   'Anx=Anxiety, Dep=Depression, Str=Stress',
                   ha='left', va='bottom',
                   fontsize=7, color='#666', style='italic')

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
