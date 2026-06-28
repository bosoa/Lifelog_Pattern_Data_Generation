#!/bin/bash
#
# 타겟별 최적 Threshold 재분석 스크립트
# Depression ≥6점, Stress ≥5점 (Anxiety 제외)
#
# 사용법:
#   ./run_target_specific_threshold_analysis.sh
#

set -e

echo "======================================================================="
echo "🎯 타겟별 최적 Threshold 재분석"
echo "Depression ≥6, Stress ≥5 (Anxiety 제외 - threshold 1점으로 너무 낮음)"
echo "시작 시각: $(date)"
echo "======================================================================="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="target_specific_results_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo ""
echo "📁 결과 디렉토리: $OUTPUT_DIR"
echo ""

# Phase 1: 이진 분류 데이터 재생성
echo "======================================================================="
echo "Phase 1: 이진 분류 데이터 재생성"
echo "======================================================================="

python3 << 'PYTHON_EOF' | tee "$OUTPUT_DIR/01_binary_classification.log"
import sys
sys.path.insert(0, 'src')
from binary_classification_converter import BinaryClassificationConverter
import pandas as pd
import glob

# 타겟별 최적 threshold
thresholds = {
    'depression': 6.0,
    'stress': 5.0
}

print("\n타겟별 Threshold 설정:")
print("  - Depression: ≥6점")
print("  - Stress: ≥5점")
print("  - Anxiety: 제외 (threshold 1점으로 너무 낮음)")
print("")

for target, threshold in thresholds.items():
    print(f"\n{'='*60}")
    print(f"Processing {target.upper()} (threshold={threshold})")
    print(f"{'='*60}")

    converter = BinaryClassificationConverter(threshold=threshold)

    # 데이터 로드 및 변환
    files = glob.glob(f"hierarchical_data/{target}_*_hierarchical_data.csv")
    if files:
        data = pd.read_csv(files[0])
        data = converter.convert_to_binary(data, target)
        stats = converter.analyze_distribution(data, target)

        # 저장 (기존 파일 백업)
        output_file = f"hierarchical_data/{target}_binary_classification.csv"
        backup_file = f"hierarchical_data/{target}_binary_classification_backup_{TIMESTAMP}.csv"

        # 기존 파일이 있으면 백업
        import os
        if os.path.exists(output_file):
            import shutil
            shutil.copy2(output_file, backup_file)
            print(f"   백업: {backup_file}")

        data.to_csv(output_file, index=False)

        print(f"\n✅ {target} 완료:")
        print(f"   발생: {stats['positive_count']}명 ({stats['positive_ratio']*100:.1f}%)")
        print(f"   저장: {output_file}")

print("\n" + "="*60)
print("✅ Phase 1 완료!")
print("="*60)

PYTHON_EOF

echo ""
echo "✅ Phase 1 완료: $(date)"

# Phase 2: 좌표 변환 데이터 재생성
echo ""
echo "======================================================================="
echo "Phase 2: 좌표 변환 데이터 재생성"
echo "======================================================================="

# 2-1. 극좌표 변환
echo ""
echo "[2-1] 극좌표 변환..."
cd src
python3 << 'PYTHON_EOF' 2>&1 | tee "../$OUTPUT_DIR/02_polar_transform.log"
import sys
sys.path.insert(0, '.')
from polar_binary_classification_converter import PolarBinaryClassificationConverter

thresholds = {'depression': 6.0, 'stress': 5.0}

converter = PolarBinaryClassificationConverter()
for target, threshold in thresholds.items():
    print(f"\n극좌표 변환: {target} (threshold={threshold})")
    df = converter.create_binary_classification_data(target, threshold=threshold)
    print(f"✅ {target}: {len(df)} samples")

print("\n극좌표 변환 완료!")
PYTHON_EOF
cd ..

# 2-2. 원통좌표 변환
echo ""
echo "[2-2] 원통좌표 변환..."
cd src
python3 << 'PYTHON_EOF' 2>&1 | tee "../$OUTPUT_DIR/03_cylindrical_transform.log"
import sys
sys.path.insert(0, '.')
from cylindrical_binary_classification_converter import CylindricalBinaryClassificationConverter

thresholds = {'depression': 6.0, 'stress': 5.0}

converter = CylindricalBinaryClassificationConverter()
for target, threshold in thresholds.items():
    print(f"\n원통좌표 변환: {target} (threshold={threshold})")
    df = converter.create_binary_classification_data(target, threshold=threshold)
    print(f"✅ {target}: {len(df)} samples")

print("\n원통좌표 변환 완료!")
PYTHON_EOF
cd ..

# 2-3. 구면좌표 변환
echo ""
echo "[2-3] 구면좌표 변환..."
cd src
python3 << 'PYTHON_EOF' 2>&1 | tee "../$OUTPUT_DIR/04_spherical_transform.log"
import sys
sys.path.insert(0, '.')
from spherical_binary_classification_converter import SphericalBinaryClassificationConverter

thresholds = {'depression': 6.0, 'stress': 5.0}

converter = SphericalBinaryClassificationConverter()
for target, threshold in thresholds.items():
    print(f"\n구면좌표 변환: {target} (threshold={threshold})")
    df = converter.create_binary_classification_data(target, threshold=threshold)
    print(f"✅ {target}: {len(df)} samples")

print("\n구면좌표 변환 완료!")
PYTHON_EOF
cd ..

echo ""
echo "✅ Phase 2 완료: $(date)"

# Phase 3: 모델 비교 분석
echo ""
echo "======================================================================="
echo "Phase 3: 모델 비교 분석"
echo "======================================================================="

for target in depression stress; do
    echo ""
    echo "[3-1] $target 원본 데이터 모델 비교..."
    python3 src/model_comparison.py --target "$target" > "$OUTPUT_DIR/05_model_${target}.log" 2>&1

    echo "[3-2] $target 극좌표 모델 비교..."
    # 극좌표 모델 비교는 polar_model_comparison.py에서 처리

    echo "[3-3] $target 생존 분석..."
    python3 src/survival_analysis.py --target "$target" > "$OUTPUT_DIR/06_survival_${target}.log" 2>&1
done

# 좌표 변환 통합 모델 비교
echo ""
echo "[3-4] 좌표 변환 통합 모델 비교..."
python3 src/polar_model_comparison.py > "$OUTPUT_DIR/07_polar_models.log" 2>&1 || echo "Warning: polar_model_comparison.py may need adjustment"
python3 src/cylindrical_model_comparison.py > "$OUTPUT_DIR/08_cylindrical_models.log" 2>&1 || echo "Warning: cylindrical_model_comparison.py may need adjustment"
python3 src/spherical_model_comparison.py > "$OUTPUT_DIR/09_spherical_models.log" 2>&1 || echo "Warning: spherical_model_comparison.py may need adjustment"

echo ""
echo "✅ Phase 3 완료: $(date)"

# 완료
echo ""
echo "======================================================================="
echo "🎉 타겟별 최적 Threshold 재분석 완료!"
echo "종료 시각: $(date)"
echo "======================================================================="
echo ""
echo "📊 생성된 파일:"
echo "  - hierarchical_data/depression_binary_classification.csv (threshold=6)"
echo "  - hierarchical_data/stress_binary_classification.csv (threshold=5)"
echo "  - hierarchical_data_polar/depression_binary_classification_polar.csv"
echo "  - hierarchical_data_polar/stress_binary_classification_polar.csv"
echo "  - hierarchical_data_cylinder/*"
echo "  - hierarchical_data_sphere/*"
echo ""
echo "📁 로그 파일: $OUTPUT_DIR/"
echo ""
echo "⚠️  주의: Phase 4 (피노타이핑 및 비교)는 별도로 실행해야 합니다."
echo ""
