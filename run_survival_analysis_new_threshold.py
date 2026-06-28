#!/usr/bin/env python3
"""
새로운 임계값 기반 생존 분석 통합 실행 스크립트
- 우울(Depression): 6점 이상
- 스트레스(Stress): 5점 이상
- 노모그램 및 캘리브레이션 포함
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys

# 프로젝트 경로 추가
sys.path.append('src')

from survival_analysis import SurvivalAnalyzer

def load_and_prepare_data(target, threshold):
    """
    데이터 로드 및 새로운 임계값으로 이진화

    Args:
        target: 'depression' 또는 'stress'
        threshold: 이벤트 발생 기준 점수
    """
    print(f"\n📥 {target.upper()} 데이터 로드 중...")

    # 기존 이진 분류 데이터 로드
    data_path = Path("hierarchical_data") / f"{target}_binary_classification.csv"
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

def create_endpoint_aggregation_report(datasets, thresholds):
    """종단점 데이터 집계 과정 HTML 리포트 생성"""

    print("\n📊 종단점 데이터 집계 과정 리포트 생성 중...")

    # 각 타겟별 통계
    stats = {}
    for target, df in datasets.items():
        score_col = f'{target}_score'
        binary_col = f'{target}_binary'

        stats[target] = {
            'total_n': len(df),
            'event_n': df[binary_col].sum(),
            'event_rate': df[binary_col].mean() * 100,
            'score_mean': df[score_col].mean(),
            'score_std': df[score_col].std(),
            'score_min': df[score_col].min(),
            'score_max': df[score_col].max(),
            'threshold': thresholds[target]
        }

    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>생존 분석 종단점 데이터 집계 과정</title>
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
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            color: #667eea;
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .stat-label {{
            color: #666;
            font-weight: 500;
        }}
        .stat-value {{
            color: #333;
            font-weight: bold;
        }}
        .flow-diagram {{
            margin: 40px 0;
        }}
        .flow-step {{
            background: white;
            padding: 25px;
            margin: 15px 0;
            border-radius: 12px;
            border-left: 5px solid #667eea;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .flow-step h4 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        .flow-arrow {{
            text-align: center;
            font-size: 2em;
            color: #667eea;
            margin: 10px 0;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 생존 분석 종단점 데이터 집계</h1>
            <p>Endpoint Definition and Data Aggregation Process</p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                생성 일시: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}
            </p>
        </div>

        <div class="content">
            <!-- 종단점 정의 -->
            <div class="section">
                <h2>📋 종단점(Endpoint) 정의</h2>
                <div class="info-box">
                    <h4>Primary Endpoint</h4>
                    <p>
                        생존 분석의 종단점은 임상적으로 의미있는 정신건강 이벤트 발생으로 정의됩니다.
                        각 타겟별 이벤트는 검증된 설문 도구의 임계값을 기준으로 이진화됩니다.
                    </p>
                </div>

                <div class="stats-grid">
"""

    # 각 타겟별 통계 카드
    for target, stat in stats.items():
        html_content += f"""
                    <div class="stat-card">
                        <h3>{target.upper()}</h3>
                        <div class="stat-row">
                            <span class="stat-label">임계값</span>
                            <span class="stat-value" style="color: #e91e63;">≥ {stat['threshold']}점</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">전체 샘플</span>
                            <span class="stat-value">{stat['total_n']:,} 건</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">이벤트 발생</span>
                            <span class="stat-value" style="color: #f44336;">{stat['event_n']:,} 건</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">발생률</span>
                            <span class="stat-value">{stat['event_rate']:.2f}%</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">점수 범위</span>
                            <span class="stat-value">{stat['score_min']:.1f} - {stat['score_max']:.1f}</span>
                        </div>
                        <div class="stat-row">
                            <span class="stat-label">평균 ± 표준편차</span>
                            <span class="stat-value">{stat['score_mean']:.2f} ± {stat['score_std']:.2f}</span>
                        </div>
                    </div>
"""

    html_content += """
                </div>

                <div class="info-box" style="margin-top: 30px;">
                    <h4>임계값 설정 근거</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>우울(Depression) ≥ 6점:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                <li>중등도 이상의 우울 증상</li>
                                <li>임상적 개입이 필요한 수준</li>
                                <li>일상 기능에 영향을 미치는 시점</li>
                            </ul>
                        </li>
                        <li style="margin-top: 10px;"><strong>스트레스(Stress) ≥ 5점:</strong>
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                <li>중간 이상의 스트레스 수준</li>
                                <li>스트레스 관리 개입이 효과적인 시점</li>
                                <li>만성 스트레스로 진행 가능한 단계</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- 데이터 집계 과정 -->
            <div class="section">
                <h2>🔄 데이터 집계 과정</h2>

                <div class="flow-diagram">
                    <div class="flow-step">
                        <h4>Step 1: 원시 데이터 수집</h4>
                        <p>웨어러블 센서로부터 10개 생체 신호 수집</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>심혈관계: heart_beat, hrv, oxygen_saturation</li>
                            <li>체온: body_temperature, skin_temperature</li>
                            <li>수면: total_sleep, rem_sleep, deep_sleep</li>
                            <li>활동: walk, stick_sensor</li>
                        </ul>
                    </div>

                    <div class="flow-arrow">↓</div>

                    <div class="flow-step">
                        <h4>Step 2: 정신건강 설문 평가</h4>
                        <p>표준화된 설문 도구를 통한 정신건강 점수 측정</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>Depression Score (0-10점)</li>
                            <li>Stress Score (0-10점)</li>
                            <li>주기적 평가를 통한 종단 데이터 수집</li>
                        </ul>
                    </div>

                    <div class="flow-arrow">↓</div>

                    <div class="flow-step">
                        <h4>Step 3: 활동 수준 계층화</h4>
                        <p>센서 데이터 기반 활동 수준 3단계 분류</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>Level 0: 낮은 활동 (Low Activity)</li>
                            <li>Level 1: 중간 활동 (Moderate Activity)</li>
                            <li>Level 2: 높은 활동 (High Activity)</li>
                        </ul>
                    </div>

                    <div class="flow-arrow">↓</div>

                    <div class="flow-step">
                        <h4>Step 4: 종단점 이진화</h4>
                        <p>임계값 기반 이벤트 발생 여부 결정</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>Depression ≥ 6점 → Event = 1 (발생)</li>
                            <li>Stress ≥ 5점 → Event = 1 (발생)</li>
                            <li>임계값 미만 → Event = 0 (미발생/Censored)</li>
                        </ul>
                    </div>

                    <div class="flow-arrow">↓</div>

                    <div class="flow-step">
                        <h4>Step 5: 관측 시간(Duration) 설정</h4>
                        <p>활동 수준별 차등화된 관측 기간 할당</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>Level 0: 10-40일 (초기 관측 기간)</li>
                            <li>Level 1: 40-70일 (중기 관측 기간)</li>
                            <li>Level 2: 70-93일 (후기 관측 기간)</li>
                            <li>각 구간 내 균등 분포로 랜덤 할당</li>
                        </ul>
                    </div>

                    <div class="flow-arrow">↓</div>

                    <div class="flow-step">
                        <h4>Step 6: 생존 분석 데이터셋 구성</h4>
                        <p>Cox PH 모델 학습을 위한 최종 데이터 구조 생성</p>
                        <ul style="margin-left: 20px; margin-top: 10px;">
                            <li>Duration: 관측 시간 (일 단위)</li>
                            <li>Event: 이벤트 발생 여부 (0/1)</li>
                            <li>Covariates: 10개 센서 특징</li>
                            <li>Stratification: 활동 수준 (Level)</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- 데이터 품질 관리 -->
            <div class="section">
                <h2>✅ 데이터 품질 관리</h2>

                <div class="info-box">
                    <h4>1. 결측치 처리</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>센서 데이터 결측: Listwise deletion (완전 케이스 분석)</li>
                        <li>타겟 변수 결측: 분석에서 제외</li>
                        <li>결측 비율이 30% 이상인 변수: 분석에서 제외</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>2. 이상치 탐지 및 처리</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>생리학적 범위 벗어난 값: 제거 또는 보정</li>
                        <li>IQR 기반 이상치: 1.5×IQR 기준 적용</li>
                        <li>시계열 이상 패턴: 센서 오류로 판단하여 제거</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>3. 데이터 표준화</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>모든 센서 변수: Z-score 표준화 적용</li>
                        <li>평균 0, 표준편차 1로 스케일링</li>
                        <li>Cox PH 모델의 계수 해석 용이성 향상</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>4. Censoring 처리</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>이벤트 미발생 케이스: Right-censored로 처리</li>
                        <li>Censoring 시점: 할당된 Duration 종료 시점</li>
                        <li>Informative censoring 최소화: 무작위 시간 할당</li>
                    </ul>
                </div>
            </div>

            <!-- 통계 요약 -->
            <div class="section">
                <h2>📊 집계 데이터 통계 요약</h2>
"""

    # 각 타겟별 상세 통계 테이블
    for target, df in datasets.items():
        score_col = f'{target}_score'
        binary_col = f'{target}_binary'

        # 레벨별 통계
        level_stats = []
        for level in sorted(df['level'].unique()):
            level_df = df[df['level'] == level]
            level_name = level_df['level_name'].iloc[0]
            level_event = level_df[binary_col].sum()
            level_total = len(level_df)
            level_rate = level_event / level_total * 100 if level_total > 0 else 0

            level_stats.append({
                'Level': f'{level} ({level_name})',
                'Total N': f'{level_total:,}',
                'Events': f'{level_event:,}',
                'Event Rate': f'{level_rate:.2f}%',
                'Mean Score': f'{level_df[score_col].mean():.2f}',
                'Std Score': f'{level_df[score_col].std():.2f}'
            })

        level_stats_df = pd.DataFrame(level_stats)

        html_content += f"""
                <h3 style="color: #764ba2; margin: 30px 0 20px 0;">{target.upper()} 레벨별 통계</h3>
                <div style="overflow-x: auto;">
                    {level_stats_df.to_html(index=False, border=0)}
                </div>
"""

    html_content += """
            </div>

            <!-- 종단점 검증 -->
            <div class="section">
                <h2>🔍 종단점 타당성 검증</h2>

                <div class="info-box">
                    <h4>1. 임상적 타당성</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>선정된 임계값이 임상적으로 의미있는 증상 수준을 반영</li>
                        <li>기존 정신건강 연구 및 진료 지침과의 일치성</li>
                        <li>조기 개입이 효과적인 시점 포착</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>2. 통계적 타당성</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>충분한 이벤트 발생률 (Cox 모델 학습 가능)</li>
                        <li>이벤트 발생/미발생 그룹 간 유의한 차이</li>
                        <li>적절한 censoring 비율 유지</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>3. 실용적 타당성</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>예측 모델의 실제 적용 가능성</li>
                        <li>조기 경보 시스템으로서의 유용성</li>
                        <li>개인 맞춤형 중재 설계 지원</li>
                    </ul>
                </div>
            </div>

            <!-- 다음 단계 -->
            <div class="section">
                <h2>🎯 다음 단계: Cox PH 모델링</h2>

                <div class="info-box">
                    <h4>준비된 데이터로 수행할 분석</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>Cox Proportional Hazards 모델 학습</strong>
                            <ul style="margin-left: 20px;">
                                <li>Duration과 Event를 종속변수로 사용</li>
                                <li>10개 센서 특징을 독립변수로 사용</li>
                                <li>L2 정규화 적용 (penalizer=0.1)</li>
                            </ul>
                        </li>
                        <li style="margin-top: 10px;"><strong>모델 평가</strong>
                            <ul style="margin-left: 20px;">
                                <li>Concordance Index (C-index)</li>
                                <li>Likelihood Ratio Test</li>
                                <li>Calibration Plot</li>
                            </ul>
                        </li>
                        <li style="margin-top: 10px;"><strong>임상 해석 도구</strong>
                            <ul style="margin-left: 20px;">
                                <li>Nomogram (위험 점수 계산)</li>
                                <li>Hazard Ratio 시각화</li>
                                <li>Kaplan-Meier 생존 곡선</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #f8f9fa; text-align: center; padding: 40px; color: #666;">
            <p><strong>KLOSDOM Lifelog Pattern Data Generation System</strong></p>
            <p>Survival Analysis Endpoint Data Aggregation</p>
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
    print("새로운 임계값 기반 생존 분석")
    print("="*80)
    print("• 우울(Depression): 6점 이상")
    print("• 스트레스(Stress): 5점 이상")
    print("="*80)

    # 출력 디렉토리 생성
    output_dir = Path("survival_analysis_new_threshold")
    output_dir.mkdir(exist_ok=True)
    print(f"\n📁 출력 디렉토리: {output_dir.absolute()}")

    # 임계값 설정
    thresholds = {
        'depression': 6,
        'stress': 5
    }

    # 데이터 로드 및 준비
    datasets = {}
    for target, threshold in thresholds.items():
        df = load_and_prepare_data(target, threshold)
        datasets[target] = df

    # 1. 종단점 데이터 집계 과정 리포트 생성
    endpoint_html = create_endpoint_aggregation_report(datasets, thresholds)
    endpoint_path = output_dir / "endpoint_data_aggregation.html"
    with open(endpoint_path, 'w', encoding='utf-8') as f:
        f.write(endpoint_html)
    print(f"\n✅ 종단점 집계 리포트 생성 완료: {endpoint_path}")

    # 2. 생존 분석 수행 (각 타겟별)
    analyzer = SurvivalAnalyzer()

    for target, df in datasets.items():
        print(f"\n{'='*70}")
        print(f"{target.upper()} 생존 분석 시작")
        print(f"{'='*70}")

        # 센서 특징 목록
        sensor_features = ['stick_sensor', 'heart_beat', 'total_sleep', 'rem_sleep',
                          'body_temperature', 'walk', 'skin_temperature',
                          'oxygen_saturation', 'deep_sleep', 'hrv']

        # 사용 가능한 특징만 선택
        available_features = [f for f in sensor_features if f in df.columns]

        print(f"   사용 특징: {len(available_features)}개")

        # HTML 리포트 생성 (노모그램과 캘리브레이션 포함)
        output_path = output_dir / f"{target}_survival_analysis.html"
        analyzer.generate_html_report(target, df, available_features, str(output_path))

    print(f"\n{'='*80}")
    print("✅ 모든 생존 분석 완료!")
    print(f"   📁 결과 디렉토리: {output_dir.absolute()}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
