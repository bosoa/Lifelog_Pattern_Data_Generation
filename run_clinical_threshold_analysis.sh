#!/bin/bash
#
# 정신과 설문 기반 Threshold 재분석 스크립트
# Anxiety: 2점 이상, Depression: 4점 이상, Stress: 3점 이상
#
# 사용법:
#   ./run_clinical_threshold_analysis.sh
#

set -e

echo "======================================================================="
echo "🏥 정신과 설문 기반 Threshold 재분석"
echo "Anxiety ≥2, Depression ≥4, Stress ≥3"
echo "시작 시각: $(date)"
echo "======================================================================="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="clinical_threshold_results_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "📁 결과 디렉토리: $OUTPUT_DIR"
echo ""

# 1. 이진 분류 데이터 재생성
echo "======================================================================="
echo "[1/3] 이진 분류 데이터 재생성 (정신과 설문 기준)"
echo "======================================================================="

python3 << 'PYTHON_EOF' | tee "$OUTPUT_DIR/01_binary_classification.log"
import sys
sys.path.insert(0, 'src')
from binary_classification_converter import BinaryClassificationConverter

# 정신과 설문 기반 threshold
thresholds = {
    'anxiety': 2.0,
    'depression': 4.0,
    'stress': 3.0
}

results = {}

for target, threshold in thresholds.items():
    print(f"\n{'='*60}")
    print(f"Processing {target.upper()} (threshold={threshold})")
    print(f"{'='*60}")

    converter = BinaryClassificationConverter(threshold=threshold)

    # 해당 타겟만 변환
    import pandas as pd
    import glob
    from pathlib import Path

    files = glob.glob(f"hierarchical_data/{target}_*_hierarchical_data.csv")
    if files:
        data = pd.read_csv(files[0])
        data = converter.convert_to_binary(data, target)
        stats = converter.analyze_distribution(data, target)

        # 저장
        output_file = f"hierarchical_data/{target}_binary_classification_clinical.csv"
        data.to_csv(output_file, index=False)

        print(f"\n✅ {target} 완료:")
        print(f"   발생: {stats['positive_count']}명 ({stats['positive_ratio']*100:.1f}%)")
        print(f"   저장: {output_file}")

        results[target] = stats

print("\n" + "="*60)
print("✅ 이진 분류 데이터 재생성 완료!")
print("="*60)

PYTHON_EOF

echo ""
echo "✅ 1단계 완료: $(date)"

# 2. 기존 결과와 비교
echo ""
echo "======================================================================="
echo "[2/3] 기존 결과 (6점 기준)와 비교"
echo "======================================================================="

python3 << 'PYTHON_EOF' | tee "$OUTPUT_DIR/02_comparison.log"
import pandas as pd

print("\n📊 Threshold 비교 분석\n")
print("="*70)

results = []

for target in ['anxiety', 'depression', 'stress']:
    # 6점 기준
    df_old = pd.read_csv(f'hierarchical_data/{target}_binary_classification.csv')
    old_rate = (df_old[f'{target}_binary'] == 1).mean()
    old_count = (df_old[f'{target}_binary'] == 1).sum()

    # 정신과 설문 기준
    df_new = pd.read_csv(f'hierarchical_data/{target}_binary_classification_clinical.csv')
    new_rate = (df_new[f'{target}_binary'] == 1).mean()
    new_count = (df_new[f'{target}_binary'] == 1).sum()

    results.append({
        'Target': target.upper(),
        'Old_Threshold': '6점 이상',
        'Old_Rate': f'{old_rate*100:.1f}%',
        'Old_Count': old_count,
        'New_Threshold': f'{[2,4,3][["anxiety","depression","stress"].index(target)]}점 이상',
        'New_Rate': f'{new_rate*100:.1f}%',
        'New_Count': new_count,
        'Change': f'{(new_rate-old_rate)*100:+.1f}%p'
    })

df_results = pd.DataFrame(results)
print(df_results.to_string(index=False))

# CSV 저장
df_results.to_csv(f'{OUTPUT_DIR}/threshold_comparison.csv', index=False)

print("\n" + "="*70)

PYTHON_EOF

echo ""
echo "✅ 2단계 완료: $(date)"

# 3. HTML 보고서 생성
echo ""
echo "======================================================================="
echo "[3/3] HTML 보고서 생성"
echo "======================================================================="

python3 << 'PYTHON_EOF' | tee "$OUTPUT_DIR/03_html_report.log"
import sys
sys.path.insert(0, 'src')

print("📄 HTML 보고서 생성 중...")
print("(구현 예정)")

PYTHON_EOF

echo ""
echo "✅ 3단계 완료: $(date)"

# 완료
echo ""
echo "======================================================================="
echo "🎉 정신과 설문 기반 Threshold 재분석 완료!"
echo "종료 시각: $(date)"
echo "======================================================================="
echo ""
echo "📊 결과 파일:"
echo "  - hierarchical_data/anxiety_binary_classification_clinical.csv"
echo "  - hierarchical_data/depression_binary_classification_clinical.csv"
echo "  - hierarchical_data/stress_binary_classification_clinical.csv"
echo "  - $OUTPUT_DIR/threshold_comparison.csv"
echo ""
