#!/usr/bin/env python3
"""
정신과 설문 기반 Threshold 분석 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 출력 디렉토리
OUTPUT_DIR = 'model_results/threshold_analysis'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 정신과 설문 데이터 로드
survey_dir = 'MentalHealth_Questionaire'
files = [f for f in os.listdir(survey_dir) if f.endswith('.xlsx')]
excel_file = os.path.join(survey_dir, files[0])

xl = pd.ExcelFile(excel_file)
df_survey = pd.read_excel(excel_file, sheet_name=xl.sheet_names[0])

# 정신과 설문 기준
criteria = {
    'GAD-7 (불안)': ('GAD7_Score', 10, 'anxiety'),
    'PHQ-9 (우울)': ('PHQ9_Score', 10, 'depression'),
    'PSS (스트레스)': ('PSS_score', 17, 'stress')
}

# 1. 정신과 설문 발생률 계산
print("="*70)
print("📊 정신과 설문 발생률 계산")
print("="*70)

prevalence_data = []

for name, (col, threshold, target) in criteria.items():
    total = df_survey[col].notna().sum()
    positive = (df_survey[col] >= threshold).sum()
    rate = positive / total * 100

    prevalence_data.append({
        'Target': name,
        'Column': col,
        'Threshold': threshold,
        'Positive': positive,
        'Total': total,
        'Rate': rate,
        'target_key': target
    })

    print(f"{name}: {threshold}점 이상 → {positive}/{total} = {rate:.1f}%")

df_prevalence = pd.DataFrame(prevalence_data)

# 2. 셀프체크 점수 분포 및 최적 threshold 찾기
print("\n" + "="*70)
print("🔍 셀프체크 점수 기반 최적 Threshold 탐색")
print("="*70)

threshold_analysis = []

for _, row in df_prevalence.iterrows():
    target = row['target_key']
    target_rate = row['Rate']

    # 라이프로그 데이터 로드
    files = glob.glob(f'hierarchical_data/{target}_*_hierarchical_data.csv')
    if not files:
        continue

    df = pd.read_csv(files[0])
    score_col = f'{target}_score'

    # 각 threshold 테스트
    for threshold in range(1, 7):
        actual_rate = (df[score_col] >= threshold).mean() * 100
        error = abs(actual_rate - target_rate)
        count = (df[score_col] >= threshold).sum()

        threshold_analysis.append({
            'Target': target,
            'Target_Rate': target_rate,
            'Threshold': threshold,
            'Actual_Rate': actual_rate,
            'Error': error,
            'Count': count,
            'Total': len(df)
        })

df_threshold = pd.DataFrame(threshold_analysis)

# 최적 threshold 찾기
optimal_thresholds = {}
for target in ['anxiety', 'depression', 'stress']:
    df_t = df_threshold[df_threshold['Target'] == target]
    best_row = df_t.loc[df_t['Error'].idxmin()]
    optimal_thresholds[target] = {
        'threshold': int(best_row['Threshold']),
        'rate': best_row['Actual_Rate'],
        'target_rate': best_row['Target_Rate'],
        'error': best_row['Error']
    }
    print(f"{target.upper()}: {int(best_row['Threshold'])}점 이상 " +
          f"(실제: {best_row['Actual_Rate']:.1f}%, 목표: {best_row['Target_Rate']:.1f}%, 오차: {best_row['Error']:.1f}%p)")

# 3. 시각화 생성

# 3-1. 정신과 설문 발생률 비교
fig, ax = plt.subplots(figsize=(10, 6))
targets = ['GAD-7 (불안)', 'PHQ-9 (우울)', 'PSS (스트레스)']
rates = df_prevalence['Rate'].values
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

bars = ax.bar(targets, rates, color=colors, alpha=0.7, edgecolor='black')
ax.set_ylabel('발생률 (%)', fontsize=12)
ax.set_title('정신과 설문 기반 발생률 (GAD-7≥10, PHQ-9≥10, PSS≥17)', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(rates) * 1.2)

# 값 표시
for bar, rate in zip(bars, rates):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{rate:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/psychiatric_survey_prevalence.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✅ 시각화 1: {OUTPUT_DIR}/psychiatric_survey_prevalence.png")

# 3-2. Threshold 별 발생률 비교 (3개 서브플롯)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

target_names = {
    'anxiety': '불안 (Anxiety)',
    'depression': '우울 (Depression)',
    'stress': '스트레스 (Stress)'
}

for idx, target in enumerate(['anxiety', 'depression', 'stress']):
    ax = axes[idx]
    df_t = df_threshold[df_threshold['Target'] == target]

    # 실제 발생률
    ax.plot(df_t['Threshold'], df_t['Actual_Rate'], 'o-',
            linewidth=2, markersize=8, label='실제 발생률', color=colors[idx])

    # 목표 발생률 (수평선)
    target_rate = df_t['Target_Rate'].iloc[0]
    ax.axhline(y=target_rate, color='red', linestyle='--',
               linewidth=2, label=f'목표 발생률 ({target_rate:.1f}%)')

    # 최적 threshold 표시
    opt = optimal_thresholds[target]
    ax.axvline(x=opt['threshold'], color='green', linestyle=':',
               linewidth=2, alpha=0.5, label=f'최적 {opt["threshold"]}점')

    ax.set_xlabel('Threshold (점)', fontsize=11)
    ax.set_ylabel('발생률 (%)', fontsize=11)
    ax.set_title(target_names[target], fontsize=12, fontweight='bold')
    ax.set_xticks(range(1, 7))
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/threshold_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ 시각화 2: {OUTPUT_DIR}/threshold_comparison.png")

# 3-3. 셀프체크 점수 분포 (히스토그램)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, target in enumerate(['anxiety', 'depression', 'stress']):
    ax = axes[idx]

    # 데이터 로드
    files = glob.glob(f'hierarchical_data/{target}_*_hierarchical_data.csv')
    df = pd.read_csv(files[0])
    score_col = f'{target}_score'

    # 히스토그램
    counts, bins, patches = ax.hist(df[score_col], bins=np.arange(0.5, 7.5, 1),
                                     color=colors[idx], alpha=0.7, edgecolor='black')

    # 최적 threshold 선
    opt_threshold = optimal_thresholds[target]['threshold']
    ax.axvline(x=opt_threshold - 0.5, color='red', linestyle='--',
               linewidth=2, label=f'최적 Threshold: {opt_threshold}점')

    ax.set_xlabel('셀프체크 점수', fontsize=11)
    ax.set_ylabel('빈도', fontsize=11)
    ax.set_title(f'{target_names[target]} 점수 분포', fontsize=12, fontweight='bold')
    ax.set_xticks(range(1, 7))
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    # 통계 정보
    mean_score = df[score_col].mean()
    ax.text(0.98, 0.98, f'평균: {mean_score:.2f}점',
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/score_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ 시각화 3: {OUTPUT_DIR}/score_distribution.png")

# 3-4. 오차 비교 (막대 그래프)
fig, ax = plt.subplots(figsize=(10, 6))

target_labels = ['불안\n(Anxiety)', '우울\n(Depression)', '스트레스\n(Stress)']
errors = [optimal_thresholds[t]['error'] for t in ['anxiety', 'depression', 'stress']]
thresholds = [optimal_thresholds[t]['threshold'] for t in ['anxiety', 'depression', 'stress']]

bars = ax.bar(target_labels, errors, color=colors, alpha=0.7, edgecolor='black')
ax.set_ylabel('오차 (%p)', fontsize=12)
ax.set_title('최적 Threshold의 목표 발생률 대비 오차', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(errors) * 1.3)

# 값 및 threshold 표시
for bar, error, threshold in zip(bars, errors, thresholds):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{error:.1f}%p\n({threshold}점 이상)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/threshold_error.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"✅ 시각화 4: {OUTPUT_DIR}/threshold_error.png")

# 4. 요약 통계 CSV 저장
summary_data = []
for target in ['anxiety', 'depression', 'stress']:
    opt = optimal_thresholds[target]
    summary_data.append({
        'Target': target.upper(),
        'Survey': ['GAD-7 ≥10', 'PHQ-9 ≥10', 'PSS ≥17'][['anxiety', 'depression', 'stress'].index(target)],
        'Target_Rate': f"{opt['target_rate']:.1f}%",
        'Optimal_Threshold': f"{opt['threshold']}점 이상",
        'Actual_Rate': f"{opt['rate']:.1f}%",
        'Error': f"{opt['error']:.1f}%p"
    })

df_summary = pd.DataFrame(summary_data)
df_summary.to_csv(f'{OUTPUT_DIR}/threshold_summary.csv', index=False, encoding='utf-8-sig')
print(f"✅ 요약 통계: {OUTPUT_DIR}/threshold_summary.csv")

# 5. 상세 분석 CSV 저장
df_threshold.to_csv(f'{OUTPUT_DIR}/threshold_detailed_analysis.csv', index=False, encoding='utf-8-sig')
print(f"✅ 상세 분석: {OUTPUT_DIR}/threshold_detailed_analysis.csv")

print("\n" + "="*70)
print("🎉 시각화 생성 완료!")
print("="*70)
