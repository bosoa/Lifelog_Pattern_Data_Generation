"""
타겟별 특징변수 통계 계산
불안, 우울, 스트레스 각각에 대해 이벤트군 vs 정상군의 평균값 계산
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("타겟별 특징변수 통계 계산")
print("=" * 70)

# 데이터 경로
base_dir = Path("/Users/jihwanpark/claude/KLOSDOM/Lifelog_Pattern_Data_Generation/hierarchical_data")

# 최신 파일 경로
files = {
    'anxiety': base_dir / 'anxiety_20260622_104913_hierarchical_data.csv',
    'depression': base_dir / 'depression_20260622_104920_hierarchical_data.csv',
    'stress': base_dir / 'stress_20260622_104927_hierarchical_data.csv'
}

# 특징변수 리스트 (Table1에서 사용할 순서)
# 논문의 2.1.2 섹션 참고
feature_groups = {
    '수면 지표': ['total_sleep', 'rem_sleep', 'light_sleep'],
    '심혈관 지표': ['heart_beat', 'hrv'],
    '활동 지표': ['walk', 'stick_sensor'],
    '대사 지표': ['blood_sugar', 'body_temperature'],
    '기타': ['skin_temperature', 'oxygen_saturation']
}

# 모든 특징 리스트
all_features = []
for features in feature_groups.values():
    all_features.extend(features)

results = {}

for target, file_path in files.items():
    print(f"\n[{target.upper()}] 데이터 로드 중...")

    try:
        df = pd.read_csv(file_path)
        print(f"  - 전체 샘플 수: {len(df):,}")

        # 컬럼 확인
        print(f"  - 컬럼: {df.columns.tolist()}")

        # score 컬럼 찾기 (anxiety_score, depression_score, stress_score)
        score_col = f"{target}_score"
        if score_col not in df.columns:
            print(f"  ⚠️  score 컬럼({score_col})을 찾을 수 없습니다.")
            continue

        # 이벤트 정의: 셀프체크 점수 >= 4
        # 이벤트군과 정상군 구분
        event_group = df[df[score_col] >= 4]
        normal_group = df[df[score_col] < 4]

        print(f"  - 이벤트군: {len(event_group):,} ({len(event_group)/len(df)*100:.2f}%)")
        print(f"  - 정상군: {len(normal_group):,} ({len(normal_group)/len(df)*100:.2f}%)")

        # 각 특징변수가 데이터에 있는지 확인
        available_features = [f for f in all_features if f in df.columns]
        missing_features = [f for f in all_features if f not in df.columns]

        if missing_features:
            print(f"  ⚠️  누락된 특징: {missing_features}")

        # 통계 계산
        stats = {}
        for feature in available_features:
            event_mean = event_group[feature].mean()
            normal_mean = normal_group[feature].mean()
            event_std = event_group[feature].std()
            normal_std = normal_group[feature].std()

            stats[feature] = {
                'event_mean': event_mean,
                'event_std': event_std,
                'normal_mean': normal_mean,
                'normal_std': normal_std,
                'diff_pct': ((event_mean - normal_mean) / normal_mean * 100) if normal_mean != 0 else 0
            }

        results[target] = {
            'stats': stats,
            'n_event': len(event_group),
            'n_normal': len(normal_group),
            'event_rate': len(event_group) / len(df) * 100,
            'available_features': available_features
        }

        print(f"  ✓ 통계 계산 완료: {len(available_features)}개 특징")

    except Exception as e:
        print(f"  ✗ 에러: {e}")
        continue

# 결과 출력
print("\n" + "=" * 70)
print("결과 요약")
print("=" * 70)

for target, data in results.items():
    print(f"\n[{target.upper()}]")
    print(f"이벤트율: {data['event_rate']:.2f}%")
    print(f"\n{'특징변수':<25} {'정상군 평균':<15} {'이벤트군 평균':<15} {'차이(%)':<10}")
    print("-" * 70)

    for feature in data['available_features']:
        stat = data['stats'][feature]
        print(f"{feature:<25} {stat['normal_mean']:>10.2f}±{stat['normal_std']:>6.2f} "
              f"{stat['event_mean']:>10.2f}±{stat['event_std']:>6.2f} "
              f"{stat['diff_pct']:>8.1f}%")

# CSV 저장
print("\n" + "=" * 70)
print("CSV 파일 저장")
print("=" * 70)

output_dir = Path("/Users/jihwanpark/claude/KLOSDOM/Lifelog_Pattern_Data_Generation/draft_for_paper/figures/phenotyping")
output_dir.mkdir(parents=True, exist_ok=True)

for target, data in results.items():
    rows = []
    for feature in data['available_features']:
        stat = data['stats'][feature]
        rows.append({
            'Target': target,
            'Feature': feature,
            'Normal_Mean': stat['normal_mean'],
            'Normal_Std': stat['normal_std'],
            'Event_Mean': stat['event_mean'],
            'Event_Std': stat['event_std'],
            'Diff_Percent': stat['diff_pct']
        })

    df_out = pd.DataFrame(rows)
    output_file = output_dir / f'{target}_feature_statistics.csv'
    df_out.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✓ {output_file}")

# 통합 CSV
all_rows = []
for target, data in results.items():
    for feature in data['available_features']:
        stat = data['stats'][feature]
        all_rows.append({
            'Target': target,
            'Feature': feature,
            'Normal_Mean': stat['normal_mean'],
            'Normal_Std': stat['normal_std'],
            'Event_Mean': stat['event_mean'],
            'Event_Std': stat['event_std'],
            'Diff_Percent': stat['diff_pct']
        })

df_all = pd.DataFrame(all_rows)
output_file = output_dir / 'all_targets_feature_statistics.csv'
df_all.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"✓ 통합 파일: {output_file}")

print("\n" + "=" * 70)
print("완료!")
print("=" * 70)
