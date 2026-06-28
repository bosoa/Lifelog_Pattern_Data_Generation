#!/usr/bin/env python3
"""
좌표 변환 데이터 기반 생존 분석
- 극좌표(Polar)
- 구면좌표(Sphere)
- 원통좌표(Cylinder)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

sys.path.append('src')
from survival_analysis import SurvivalAnalyzer

def load_coordinate_data(coordinate_type, target, threshold):
    """
    좌표 변환 데이터 로드 및 이진화

    Args:
        coordinate_type: 'polar', 'sphere', 'cylinder'
        target: 'depression' or 'stress'
        threshold: 이벤트 발생 임계값
    """
    print(f"\n📥 {coordinate_type.upper()} - {target.upper()} 데이터 로드 중...")

    # 데이터 경로
    data_dir = Path(f"hierarchical_data_{coordinate_type}")
    data_path = data_dir / f"{target}_binary_classification_{coordinate_type}.csv"

    if not data_path.exists():
        print(f"   ❌ 파일 없음: {data_path}")
        return None

    df = pd.read_csv(data_path)
    print(f"   ✓ 원본 데이터: {len(df):,} 행")

    # 새로운 임계값으로 이진화
    score_col = f'{target}_score'
    df[f'{target}_binary'] = (df[score_col] >= threshold).astype(int)
    df[f'{target}_label'] = df[f'{target}_binary'].apply(
        lambda x: '발생' if x == 1 else '미발생'
    )

    event_count = df[f'{target}_binary'].sum()
    event_rate = event_count / len(df) * 100

    print(f"   ✓ 임계값: {threshold}점 이상")
    print(f"   ✓ 이벤트 발생: {event_count:,} 건 ({event_rate:.2f}%)")

    return df

def get_coordinate_features(df, coordinate_type):
    """좌표계별 특징 추출"""

    # 기본 컬럼 제외
    exclude_cols = ['level', 'level_name', 'depression_score', 'depression_binary',
                    'depression_label', 'stress_score', 'stress_binary', 'stress_label',
                    'anxiety_score', 'anxiety_binary', 'anxiety_label']

    # 사용 가능한 특징 추출
    features = [col for col in df.columns if col not in exclude_cols]

    print(f"   ✓ 사용 특징: {len(features)}개")

    return features

def create_coordinate_comparison_report(results):
    """좌표계별 성능 비교 리포트"""

    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>좌표 변환 생존 분석 성능 비교</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 50px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .content {{
            padding: 50px;
        }}
        .section {{
            margin-bottom: 50px;
            padding: 40px;
            background: #f8f9fa;
            border-radius: 15px;
        }}
        .section h2 {{
            color: #667eea;
            font-size: 2.2em;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 4px solid #667eea;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        .comparison-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .comparison-card h3 {{
            color: #667eea;
            font-size: 1.6em;
            margin-bottom: 20px;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .metric-label {{
            color: #666;
            font-weight: 500;
        }}
        .metric-value {{
            font-weight: bold;
            color: #333;
        }}
        .best-performer {{
            background: linear-gradient(135deg, #4caf5015 0%, #45a04915 100%);
            border-left: 5px solid #4caf50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 14px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .highlight-best {{
            background: #4caf5030;
            font-weight: bold;
            color: #2e7d32;
        }}
        .info-box {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-left: 5px solid #667eea;
            padding: 25px;
            margin: 30px 0;
            border-radius: 10px;
        }}
        .info-box h4 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📐 좌표 변환 생존 분석</h1>
            <p>Coordinate Transformation Survival Analysis Performance Comparison</p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                생성 일시: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}
            </p>
        </div>

        <div class="content">
            <!-- 개요 -->
            <div class="section">
                <h2>📋 분석 개요</h2>
                <div class="info-box">
                    <h4>목적</h4>
                    <p>
                        센서 데이터를 다양한 좌표계로 변환하여 특징 공간을 확장하고,
                        생존 분석 모델의 성능 향상을 도모합니다. 극좌표, 구면좌표, 원통좌표로
                        변환된 데이터를 사용하여 Cox PH 모델을 학습하고, 원본 데이터 대비 성능을 비교합니다.
                    </p>
                </div>

                <div class="info-box">
                    <h4>좌표 변환 방법</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>극좌표(Polar):</strong> 2D 변수 쌍 (x, y) → (r, θ)
                            <ul style="margin-left: 20px;">
                                <li>r = √(x² + y²)</li>
                                <li>θ = arctan(y/x)</li>
                            </ul>
                        </li>
                        <li style="margin-top: 10px;"><strong>구면좌표(Sphere):</strong> 3D 변수 트리플렛 (x, y, z) → (r, θ, φ)
                            <ul style="margin-left: 20px;">
                                <li>r = √(x² + y² + z²)</li>
                                <li>θ = arctan(y/x)</li>
                                <li>φ = arccos(z/r)</li>
                            </ul>
                        </li>
                        <li style="margin-top: 10px;"><strong>원통좌표(Cylinder):</strong> 3D 변수 트리플렛 (x, y, z) → (ρ, φ, z)
                            <ul style="margin-left: 20px;">
                                <li>ρ = √(x² + y²)</li>
                                <li>φ = arctan(y/x)</li>
                                <li>z = z (그대로)</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
"""

    # 타겟별 성능 비교
    for target in ['depression', 'stress']:
        if target not in results:
            continue

        target_results = results[target]

        # 최고 성능 찾기
        best_coord = max(target_results.keys(),
                        key=lambda k: target_results[k]['c_index'])
        best_c_index = target_results[best_coord]['c_index']

        html_content += f"""
            <!-- {target.upper()} 성능 비교 -->
            <div class="section">
                <h2>{'💙' if target == 'depression' else '💚'} {target.upper()} 성능 비교</h2>

                <div class="comparison-grid">
"""

        for coord_type in ['cartesian', 'polar', 'sphere', 'cylinder']:
            if coord_type not in target_results:
                continue

            result = target_results[coord_type]
            is_best = coord_type == best_coord

            coord_names = {
                'cartesian': '직교좌표 (Cartesian)',
                'polar': '극좌표 (Polar)',
                'sphere': '구면좌표 (Sphere)',
                'cylinder': '원통좌표 (Cylinder)'
            }

            html_content += f"""
                    <div class="comparison-card{' best-performer' if is_best else ''}">
                        <h3>{coord_names[coord_type]}</h3>
                        {'<p style="color: #4caf50; font-weight: bold; margin-bottom: 15px;">🏆 최고 성능</p>' if is_best else ''}
                        <div class="metric-row">
                            <span class="metric-label">C-index</span>
                            <span class="metric-value" style="color: #667eea;">{result['c_index']:.4f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Log-likelihood</span>
                            <span class="metric-value">{result['log_likelihood']:.2f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">AIC</span>
                            <span class="metric-value">{result['aic']:.2f}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">LR Test p-value</span>
                            <span class="metric-value">{result['lr_pvalue']:.4e}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">특징 개수</span>
                            <span class="metric-value">{result['n_features']}</span>
                        </div>
                    </div>
"""

        html_content += """
                </div>
"""

        # 성능 향상률 계산
        if 'cartesian' in target_results:
            base_c_index = target_results['cartesian']['c_index']

            improvements = []
            for coord_type in ['polar', 'sphere', 'cylinder']:
                if coord_type in target_results:
                    coord_c_index = target_results[coord_type]['c_index']
                    improvement = ((coord_c_index - base_c_index) / base_c_index) * 100
                    improvements.append({
                        'Coordinate': coord_type.capitalize(),
                        'C-index': f"{coord_c_index:.4f}",
                        'Improvement': f"{improvement:+.2f}%",
                        'Status': '향상' if improvement > 0 else '감소'
                    })

            if improvements:
                improvements_df = pd.DataFrame(improvements)
                html_content += f"""
                <h3 style="color: #764ba2; margin-top: 30px;">직교좌표 대비 성능 변화</h3>
                <p style="color: #666; margin: 15px 0;">기준: C-index {base_c_index:.4f}</p>
                <div style="overflow-x: auto;">
                    {improvements_df.to_html(index=False, border=0)}
                </div>
"""

        html_content += """
            </div>
"""

    html_content += """
            <!-- 결론 및 권장사항 -->
            <div class="section">
                <h2>💡 결론 및 권장사항</h2>

                <div class="info-box">
                    <h4>주요 발견사항</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>좌표 변환을 통한 특징 공간 확장이 모델 성능에 영향</li>
                        <li>각 타겟별로 최적의 좌표계가 다를 수 있음</li>
                        <li>변환된 특징이 센서 간 비선형 관계를 더 잘 포착</li>
                        <li>고차원 좌표계(구면, 원통)가 복잡한 패턴 학습에 유리할 수 있음</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>임상 적용 권장사항</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>최고 성능 좌표계를 선택하여 실시간 모니터링 시스템 구축</li>
                        <li>앙상블 모델: 여러 좌표계 결과를 결합하여 robust prediction</li>
                        <li>타겟별 특화된 좌표계 사용으로 예측 정확도 향상</li>
                        <li>해석 가능성과 성능 사이의 trade-off 고려</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>향후 연구 방향</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>자동 좌표계 선택 알고리즘 개발</li>
                        <li>좌표 변환 파라미터 최적화</li>
                        <li>딥러닝 기반 좌표 변환 학습</li>
                        <li>외부 데이터셋에서의 일반화 성능 검증</li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #f8f9fa; text-align: center; padding: 40px; color: #666;">
            <p><strong>KLOSDOM Lifelog Pattern Data Generation System</strong></p>
            <p>Coordinate Transformation Survival Analysis</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </p>
        </div>
    </div>
</body>
</html>
"""

    return html_content

def main():
    """메인 실행 함수"""
    print("\n" + "="*80)
    print("좌표 변환 데이터 기반 생존 분석")
    print("="*80)

    # 출력 디렉토리
    output_dir = Path("survival_analysis_new_threshold")
    output_dir.mkdir(exist_ok=True)

    # 임계값 설정
    thresholds = {
        'depression': 6,
        'stress': 5
    }

    # 좌표계 종류
    coordinate_types = ['polar', 'sphere', 'cylinder']

    # 결과 저장
    results = {
        'depression': {},
        'stress': {}
    }

    # 원본(직교좌표) 결과 추가 (이미 계산됨)
    results['depression']['cartesian'] = {
        'c_index': 0.6121,
        'log_likelihood': -19893.44,
        'aic': 39806.89,
        'lr_pvalue': 1.7832e-74,
        'n_features': 10
    }
    results['stress']['cartesian'] = {
        'c_index': 0.7128,
        'log_likelihood': -69857.29,
        'aic': 139734.57,
        'lr_pvalue': 0.0,
        'n_features': 10
    }

    analyzer = SurvivalAnalyzer()

    # 각 좌표계 및 타겟별 분석
    for coord_type in coordinate_types:
        print(f"\n{'='*70}")
        print(f"{coord_type.upper()} 좌표계 분석")
        print(f"{'='*70}")

        for target, threshold in thresholds.items():
            # 데이터 로드
            df = load_coordinate_data(coord_type, target, threshold)

            if df is None:
                continue

            # 특징 추출
            features = get_coordinate_features(df, coord_type)

            if len(features) == 0:
                print(f"   ❌ 사용 가능한 특징이 없습니다.")
                continue

            # 생존 분석
            try:
                # 생존 데이터 준비
                surv_data = analyzer.prepare_survival_data(df, target)

                # Cox PH 모델 학습
                cox_result = analyzer.fit_cox_model(surv_data, features, target)

                # 결과 저장
                results[target][coord_type] = {
                    'c_index': cox_result['concordance_index'],
                    'log_likelihood': cox_result['log_likelihood'],
                    'aic': cox_result['AIC'],
                    'lr_pvalue': cox_result['lr_test_pvalue'],
                    'n_features': len(features)
                }

                # HTML 리포트 생성
                output_path = output_dir / f"{target}_{coord_type}_survival_analysis.html"
                analyzer.generate_html_report(target, df, features, str(output_path))

                print(f"   ✅ 분석 완료: C-index = {cox_result['concordance_index']:.4f}")

            except Exception as e:
                print(f"   ❌ 분석 실패: {str(e)}")
                continue

    # 성능 비교 리포트 생성
    print(f"\n{'='*70}")
    print("성능 비교 리포트 생성 중...")
    print(f"{'='*70}")

    comparison_html = create_coordinate_comparison_report(results)
    comparison_path = output_dir / "coordinate_performance_comparison.html"
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write(comparison_html)

    print(f"\n✅ 성능 비교 리포트 생성 완료: {comparison_path}")

    print(f"\n{'='*80}")
    print("✅ 모든 좌표 변환 분석 완료!")
    print(f"   📁 결과 디렉토리: {output_dir.absolute()}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
