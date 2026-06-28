#!/usr/bin/env python3
"""
생존 분석 데이터 취합 과정 및 Table 1 생성
논문용 상세 HTML 리포트 작성
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy import stats

def load_survival_data():
    """생존 분석용 데이터 로드"""
    data_dir = Path("hierarchical_data")

    datasets = {}
    for target in ['depression', 'stress', 'anxiety']:
        file_path = data_dir / f"{target}_binary_classification.csv"
        if file_path.exists():
            df = pd.read_csv(file_path)
            datasets[target] = df
            print(f"✓ {target.upper()} 데이터 로드: {len(df):,} 행")

    return datasets

def calculate_descriptive_statistics(df, target, event_col):
    """기술 통계 계산"""

    # 전체 통계
    total_n = len(df)
    event_n = df[event_col].sum()
    event_rate = event_n / total_n * 100

    # 센서 변수 목록
    sensor_vars = ['stick_sensor', 'heart_beat', 'total_sleep', 'rem_sleep',
                   'body_temperature', 'walk', 'skin_temperature',
                   'oxygen_saturation', 'deep_sleep', 'hrv']

    # 타겟 점수 변수
    score_var = f'{target}_score'

    # 그룹별 통계
    stats_by_group = {}

    # 이벤트 발생 여부로 그룹화
    event_group = df[df[event_col] == 1]
    no_event_group = df[df[event_col] == 0]

    stats_data = []

    # 기본 정보
    stats_data.append({
        'Variable': 'N',
        'Overall': f'{total_n:,}',
        'Event': f'{len(event_group):,}',
        'No Event': f'{len(no_event_group):,}',
        'P-value': '-'
    })

    stats_data.append({
        'Variable': 'Event Rate (%)',
        'Overall': f'{event_rate:.2f}%',
        'Event': '-',
        'No Event': '-',
        'P-value': '-'
    })

    # 타겟 점수 통계
    overall_score = df[score_var]
    event_score = event_group[score_var]
    no_event_score = no_event_group[score_var]

    # T-test
    t_stat, p_val = stats.ttest_ind(event_score, no_event_score)

    stats_data.append({
        'Variable': f'{target.capitalize()} Score',
        'Overall': f'{overall_score.mean():.2f} ± {overall_score.std():.2f}',
        'Event': f'{event_score.mean():.2f} ± {event_score.std():.2f}',
        'No Event': f'{no_event_score.mean():.2f} ± {no_event_score.std():.2f}',
        'P-value': f'{p_val:.4f}' if p_val >= 0.0001 else '<0.0001'
    })

    # 센서 변수 통계
    for var in sensor_vars:
        if var in df.columns:
            overall = df[var].dropna()
            event_vals = event_group[var].dropna()
            no_event_vals = no_event_group[var].dropna()

            if len(event_vals) > 0 and len(no_event_vals) > 0:
                t_stat, p_val = stats.ttest_ind(event_vals, no_event_vals)

                stats_data.append({
                    'Variable': var.replace('_', ' ').title(),
                    'Overall': f'{overall.mean():.2f} ± {overall.std():.2f}',
                    'Event': f'{event_vals.mean():.2f} ± {event_vals.std():.2f}',
                    'No Event': f'{no_event_vals.mean():.2f} ± {no_event_vals.std():.2f}',
                    'P-value': f'{p_val:.4f}' if p_val >= 0.0001 else '<0.0001'
                })

    # Level 분포
    if 'level' in df.columns:
        level_counts_overall = df['level'].value_counts().sort_index()
        level_counts_event = event_group['level'].value_counts().sort_index()
        level_counts_no_event = no_event_group['level'].value_counts().sort_index()

        for level in sorted(df['level'].unique()):
            overall_pct = level_counts_overall.get(level, 0) / total_n * 100
            event_pct = level_counts_event.get(level, 0) / len(event_group) * 100 if len(event_group) > 0 else 0
            no_event_pct = level_counts_no_event.get(level, 0) / len(no_event_group) * 100 if len(no_event_group) > 0 else 0

            # Chi-square test
            contingency_table = pd.crosstab(df['level'] == level, df[event_col])
            chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)

            level_name = df[df['level'] == level]['level_name'].iloc[0] if len(df[df['level'] == level]) > 0 else f'Level {level}'

            stats_data.append({
                'Variable': f'Level {level} ({level_name})',
                'Overall': f'{level_counts_overall.get(level, 0):,} ({overall_pct:.1f}%)',
                'Event': f'{level_counts_event.get(level, 0):,} ({event_pct:.1f}%)',
                'No Event': f'{level_counts_no_event.get(level, 0):,} ({no_event_pct:.1f}%)',
                'P-value': f'{p_val:.4f}' if p_val >= 0.0001 else '<0.0001'
            })

    return pd.DataFrame(stats_data)

def create_data_flow_diagram():
    """데이터 취합 과정 다이어그램 HTML"""

    flow_html = """
    <div class="data-flow">
        <div class="flow-step" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <div class="step-number">1</div>
            <h3>원시 센서 데이터 수집</h3>
            <ul>
                <li>웨어러블 센서: 심박수, 산소포화도, 피부온도, 체온</li>
                <li>활동 센서: 걷기, 수면 (총수면, REM, 깊은수면)</li>
                <li>기타: 스틱 센서, HRV</li>
            </ul>
            <div class="step-output">→ 10개 센서 변수</div>
        </div>

        <div class="flow-arrow">↓</div>

        <div class="flow-step" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="step-number">2</div>
            <h3>정신건강 설문 평가</h3>
            <ul>
                <li>우울(Depression) 점수: 0-10점</li>
                <li>불안(Anxiety) 점수: 0-10점</li>
                <li>스트레스(Stress) 점수: 0-10점</li>
            </ul>
            <div class="step-output">→ 3개 타겟 변수</div>
        </div>

        <div class="flow-arrow">↓</div>

        <div class="flow-step" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="step-number">3</div>
            <h3>활동 수준 계층화</h3>
            <ul>
                <li>Level 0: 낮은 활동 (Low Activity)</li>
                <li>Level 1: 중간 활동 (Moderate Activity)</li>
                <li>Level 2: 높은 활동 (High Activity)</li>
            </ul>
            <div class="step-output">→ 계층 변수 (level, level_name)</div>
        </div>

        <div class="flow-arrow">↓</div>

        <div class="flow-step" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <div class="step-number">4</div>
            <h3>이벤트 정의 (이진화)</h3>
            <ul>
                <li><strong>우울 이벤트:</strong> Depression Score ≥ 6</li>
                <li><strong>스트레스 이벤트:</strong> Stress Score ≥ 5</li>
                <li><strong>불안 이벤트:</strong> Anxiety Score ≥ 7 (기존 기준)</li>
            </ul>
            <div class="step-output">→ 이진 이벤트 변수 (0: 미발생, 1: 발생)</div>
        </div>

        <div class="flow-arrow">↓</div>

        <div class="flow-step" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);">
            <div class="step-number">5</div>
            <h3>생존 분석 데이터 구성</h3>
            <ul>
                <li><strong>Duration:</strong> 관측 시간 생성
                    <ul style="margin-left: 20px; margin-top: 5px;">
                        <li>Level 0: 10-40일 (초기 관측)</li>
                        <li>Level 1: 40-70일 (중기 관측)</li>
                        <li>Level 2: 70-93일 (후기 관측)</li>
                    </ul>
                </li>
                <li><strong>Event:</strong> 이벤트 발생 여부 (1: 발생, 0: Censored)</li>
                <li><strong>Covariates:</strong> 10개 센서 특징 변수</li>
            </ul>
            <div class="step-output">→ 생존 분석용 최종 데이터셋</div>
        </div>

        <div class="flow-arrow">↓</div>

        <div class="flow-step" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">
            <div class="step-number">6</div>
            <h3>Cox Proportional Hazards 모델링</h3>
            <ul>
                <li>종속변수: 이벤트 발생 시간 (Duration + Event)</li>
                <li>독립변수: 10개 센서 특징</li>
                <li>분석: Hazard Ratio, Concordance Index, 생존 곡선</li>
            </ul>
            <div class="step-output">→ 생존 분석 결과</div>
        </div>
    </div>
    """

    return flow_html

def generate_html_report(datasets):
    """상세 HTML 리포트 생성"""

    print("\n📊 Table 1 및 HTML 리포트 생성 중...")

    # 각 타겟별 통계 계산
    tables = {}
    for target, df in datasets.items():
        event_col = f'{target}_binary'
        if event_col in df.columns:
            print(f"   • {target.upper()} 통계 계산 중...")
            tables[target] = calculate_descriptive_statistics(df, target, event_col)

    # 데이터 흐름 다이어그램
    flow_diagram = create_data_flow_diagram()

    # HTML 생성
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>생존 분석 데이터 취합 과정 및 Table 1</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
                         'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }}

        .container {{
            max-width: 1800px;
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

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
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

        .section h3 {{
            color: #764ba2;
            font-size: 1.6em;
            margin: 30px 0 20px 0;
        }}

        /* 데이터 흐름 스타일 */
        .data-flow {{
            margin: 30px 0;
        }}

        .flow-step {{
            padding: 30px;
            margin: 20px 0;
            border-radius: 15px;
            color: white;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        }}

        .step-number {{
            display: inline-block;
            width: 50px;
            height: 50px;
            line-height: 50px;
            background: rgba(255,255,255,0.3);
            border-radius: 50%;
            text-align: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }}

        .flow-step h3 {{
            color: white;
            font-size: 1.8em;
            margin: 15px 0;
        }}

        .flow-step ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}

        .flow-step li {{
            margin: 8px 0;
            font-size: 1.05em;
        }}

        .step-output {{
            margin-top: 15px;
            padding: 12px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            font-size: 1.1em;
        }}

        .flow-arrow {{
            text-align: center;
            font-size: 3em;
            color: #667eea;
            margin: 10px 0;
            font-weight: bold;
        }}

        /* Table 스타일 */
        .table-container {{
            overflow-x: auto;
            margin: 30px 0;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95em;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 12px;
            text-align: left;
            font-weight: bold;
            font-size: 1.05em;
        }}

        td {{
            padding: 14px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tr:hover {{
            background: #f5f5f5;
        }}

        tr:nth-child(even) {{
            background: #fafafa;
        }}

        tr:nth-child(even):hover {{
            background: #f0f0f0;
        }}

        /* 강조 박스 */
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

        .info-box p {{
            margin: 10px 0;
            line-height: 1.8;
        }}

        .info-box ul {{
            margin: 15px 0;
            padding-left: 25px;
        }}

        .info-box li {{
            margin: 8px 0;
        }}

        /* 통계 카드 */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-card h4 {{
            color: #667eea;
            font-size: 0.95em;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 2.2em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}

        .stat-card .label {{
            font-size: 0.9em;
            color: #666;
        }}

        /* 강조 텍스트 */
        .highlight {{
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
        }}

        /* Footer */
        .footer {{
            background: #f8f9fa;
            text-align: center;
            padding: 40px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}

        .footer p {{
            margin: 5px 0;
        }}

        /* 반응형 */
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
            }}

            .content {{
                padding: 20px;
            }}

            .section {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 2em;
            }}

            table {{
                font-size: 0.85em;
            }}

            th, td {{
                padding: 10px 8px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 생존 분석 데이터 취합 과정</h1>
            <p>Cox Proportional Hazards Model을 위한 데이터 준비 및 기술통계</p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                생성 일시: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}
            </p>
        </div>

        <div class="content">
            <!-- 개요 -->
            <div class="section">
                <h2>📋 분석 개요</h2>
                <div class="info-box">
                    <h4>연구 목적</h4>
                    <p>
                        본 연구는 웨어러블 센서 데이터를 활용하여 정신건강 이벤트(우울, 불안, 스트레스) 발생을
                        예측하기 위한 Cox Proportional Hazards 생존 분석을 수행합니다.
                        이를 위해 다단계 데이터 취합 과정을 거쳐 생존 분석용 데이터셋을 구성하였습니다.
                    </p>
                </div>

                <div class="stats-grid">
"""

    # 데이터셋 통계 카드 추가
    for target, df in datasets.items():
        event_col = f'{target}_binary'
        total_n = len(df)
        event_n = df[event_col].sum() if event_col in df.columns else 0
        event_rate = event_n / total_n * 100 if total_n > 0 else 0

        html_content += f"""
                    <div class="stat-card">
                        <h4>{target.upper()} Dataset</h4>
                        <div class="value">{total_n:,}</div>
                        <div class="label">총 샘플 수</div>
                        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0;">
                            <strong style="color: #667eea;">{event_n:,}</strong> 이벤트 발생<br>
                            <strong style="color: #764ba2;">{event_rate:.2f}%</strong> 발생률
                        </div>
                    </div>
"""

    html_content += f"""
                </div>
            </div>

            <!-- 데이터 취합 과정 -->
            <div class="section">
                <h2>🔄 데이터 취합 과정</h2>
                <div class="info-box">
                    <h4>6단계 데이터 파이프라인</h4>
                    <p>
                        생존 분석을 위한 데이터는 원시 센서 데이터 수집부터 Cox PH 모델링까지
                        체계적인 6단계 과정을 통해 준비됩니다. 각 단계는 데이터의 품질과
                        분석의 타당성을 보장하기 위해 설계되었습니다.
                    </p>
                </div>

                {flow_diagram}

                <div class="info-box" style="margin-top: 40px;">
                    <h4>주요 특징</h4>
                    <ul>
                        <li><strong>계층화 전략:</strong> 활동 수준에 따른 3단계 계층화로 heterogeneity 고려</li>
                        <li><strong>이벤트 정의:</strong> 임상적으로 의미있는 임계값 기반 이진화
                            <ul style="margin-left: 20px; margin-top: 5px;">
                                <li>우울: ≥6점 (중등도 이상)</li>
                                <li>스트레스: ≥5점 (중간 이상)</li>
                                <li>불안: ≥7점 (높은 수준)</li>
                            </ul>
                        </li>
                        <li><strong>시간 구조:</strong> 계층별 차등화된 관측 기간 설정으로 realistic timeline 반영</li>
                        <li><strong>Censoring 처리:</strong> 이벤트 미발생 케이스는 관측 종료 시점에서 censored 처리</li>
                    </ul>
                </div>
            </div>
"""

    # 각 타겟별 Table 1 추가
    for target, table_df in tables.items():
        html_content += f"""
            <!-- {target.upper()} Table 1 -->
            <div class="section">
                <h2>📊 Table 1: {target.upper()} Dataset Characteristics</h2>
                <div class="info-box">
                    <h4>Baseline Characteristics by Event Status</h4>
                    <p>
                        {target.capitalize()} 이벤트 발생 여부에 따른 기저 특성 비교.
                        연속형 변수는 평균 ± 표준편차, 범주형 변수는 빈도 (백분율)로 표시.
                        P-value는 연속형 변수의 경우 independent t-test,
                        범주형 변수의 경우 chi-square test로 계산.
                    </p>
                </div>

                <div class="table-container">
                    {table_df.to_html(index=False, border=0, classes='data-table')}
                </div>

                <div class="info-box" style="margin-top: 20px;">
                    <h4>해석 가이드</h4>
                    <ul>
                        <li><strong>Overall:</strong> 전체 데이터셋의 기술통계</li>
                        <li><strong>Event:</strong> {target.capitalize()} 이벤트가 발생한 그룹</li>
                        <li><strong>No Event:</strong> {target.capitalize()} 이벤트가 발생하지 않은 그룹 (Censored)</li>
                        <li><strong>P-value &lt; 0.05:</strong> 통계적으로 유의한 차이 존재</li>
                    </ul>
                </div>
            </div>
"""

    # 생존 분석 데이터 구조 설명
    html_content += """
            <!-- 생존 분석 데이터 구조 -->
            <div class="section">
                <h2>🗂️ 생존 분석 데이터 구조</h2>

                <h3>필수 구성 요소</h3>
                <div class="info-box">
                    <h4>1. Duration (관측 시간)</h4>
                    <p>
                        각 샘플의 관측 시간을 나타내며, 활동 수준(Level)에 따라 차등화:
                    </p>
                    <ul>
                        <li><strong>Level 0 (낮은 활동):</strong> 10-40일 범위의 균등 분포</li>
                        <li><strong>Level 1 (중간 활동):</strong> 40-70일 범위의 균등 분포</li>
                        <li><strong>Level 2 (높은 활동):</strong> 70-93일 범위의 균등 분포</li>
                    </ul>
                    <p style="margin-top: 10px;">
                        이러한 계층화된 시간 구조는 활동 수준에 따른 이벤트 발생 시점의 차이를 반영합니다.
                    </p>
                </div>

                <div class="info-box">
                    <h4>2. Event (이벤트 발생 여부)</h4>
                    <p>
                        정신건강 점수가 임계값 이상인 경우를 이벤트 발생(1)으로 정의:
                    </p>
                    <ul>
                        <li><strong>우울(Depression):</strong> Score ≥ 6 → Event = 1</li>
                        <li><strong>스트레스(Stress):</strong> Score ≥ 5 → Event = 1</li>
                        <li><strong>불안(Anxiety):</strong> Score ≥ 7 → Event = 1</li>
                    </ul>
                    <p style="margin-top: 10px;">
                        임계값 미만인 경우는 이벤트 미발생(0)으로 처리되며, 이는 censored observation으로 간주됩니다.
                    </p>
                </div>

                <div class="info-box">
                    <h4>3. Covariates (공변량)</h4>
                    <p>
                        Cox PH 모델의 독립변수로 사용되는 10개 센서 특징:
                    </p>
                    <ul>
                        <li><strong>심혈관계:</strong> heart_beat (심박수), hrv (심박변이도), oxygen_saturation (산소포화도)</li>
                        <li><strong>체온:</strong> body_temperature (체온), skin_temperature (피부온도)</li>
                        <li><strong>수면:</strong> total_sleep (총 수면시간), rem_sleep (REM 수면), deep_sleep (깊은 수면)</li>
                        <li><strong>활동:</strong> walk (걷기), stick_sensor (스틱 센서)</li>
                    </ul>
                    <p style="margin-top: 10px;">
                        모든 공변량은 Cox PH 모델 학습 전에 표준화(standardization)를 거칩니다.
                    </p>
                </div>

                <h3 style="margin-top: 40px;">데이터 품질 관리</h3>
                <div class="info-box">
                    <h4>결측치 처리</h4>
                    <ul>
                        <li>센서 데이터 결측: 해당 관측치 제외 (listwise deletion)</li>
                        <li>타겟 변수 결측: 분석에서 제외</li>
                        <li>분산이 0이거나 매우 낮은 변수: 모델에서 제외</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>이상치 처리</h4>
                    <ul>
                        <li>생리학적으로 불가능한 값: 제거 또는 보정</li>
                        <li>극단값: IQR 기반 이상치 탐지 적용</li>
                        <li>센서 오류: 시계열 패턴 분석을 통한 식별 및 제거</li>
                    </ul>
                </div>
            </div>

            <!-- Cox PH 모델 설정 -->
            <div class="section">
                <h2>⚙️ Cox Proportional Hazards 모델 설정</h2>

                <div class="info-box">
                    <h4>모델 사양</h4>
                    <p>
                        <strong>기본 모델:</strong><br>
                        h(t|X) = h₀(t) × exp(β₁X₁ + β₂X₂ + ... + β₁₀X₁₀)
                    </p>
                    <ul style="margin-top: 15px;">
                        <li>h(t|X): 시점 t에서 공변량 X가 주어진 경우의 hazard 함수</li>
                        <li>h₀(t): baseline hazard 함수 (비모수적 추정)</li>
                        <li>β: 회귀 계수 (log hazard ratio)</li>
                        <li>X: 10개 센서 공변량</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>모델 파라미터</h4>
                    <ul>
                        <li><strong>Penalizer:</strong> 0.1 (L2 정규화, 다중공선성 완화)</li>
                        <li><strong>Duration Column:</strong> 'duration' (관측 시간)</li>
                        <li><strong>Event Column:</strong> 'event' (이벤트 발생 여부)</li>
                        <li><strong>최적화 알고리즘:</strong> Newton-Raphson</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>평가 지표</h4>
                    <ul>
                        <li><strong>Concordance Index (C-index):</strong> 모델의 식별력 평가
                            <ul style="margin-left: 20px;">
                                <li>C &gt; 0.7: 우수한 식별력</li>
                                <li>0.6 ≤ C ≤ 0.7: 적절한 식별력</li>
                                <li>C &lt; 0.6: 낮은 식별력</li>
                            </ul>
                        </li>
                        <li><strong>Log-likelihood:</strong> 모델 적합도</li>
                        <li><strong>AIC (Akaike Information Criterion):</strong> 모델 선택 기준</li>
                        <li><strong>Likelihood Ratio Test:</strong> 모델 유의성 검정
                            <ul style="margin-left: 20px;">
                                <li>H₀: β₁ = β₂ = ... = β₁₀ = 0</li>
                                <li>p &lt; 0.05: 모델이 통계적으로 유의미</li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- 방법론적 고려사항 -->
            <div class="section">
                <h2>💡 방법론적 고려사항</h2>

                <div class="info-box">
                    <h4>Proportional Hazards 가정</h4>
                    <p>
                        Cox PH 모델의 핵심 가정은 hazard ratio가 시간에 따라 일정하다는 것입니다.
                        이를 검증하기 위해 다음 방법들을 사용:
                    </p>
                    <ul>
                        <li>Schoenfeld residuals 검정</li>
                        <li>Log-log survival plot 시각화</li>
                        <li>시간-공변량 상호작용 항 검정</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>계층화의 이점</h4>
                    <p>
                        활동 수준에 따른 계층화는 다음과 같은 이점을 제공합니다:
                    </p>
                    <ul>
                        <li><strong>Heterogeneity 고려:</strong> 활동 수준에 따른 baseline hazard의 차이 반영</li>
                        <li><strong>Confounding 통제:</strong> 활동 수준이 이벤트 발생에 미치는 영향 통제</li>
                        <li><strong>Subgroup 분석:</strong> 계층별 hazard ratio 비교 가능</li>
                        <li><strong>모델 적합도 향상:</strong> 보다 정확한 위험 예측</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>임상적 의의</h4>
                    <p>
                        정의된 임계값(우울 6점, 스트레스 5점, 불안 7점)은 다음 근거에 기반:
                    </p>
                    <ul>
                        <li><strong>임상적 유의성:</strong> 중등도 이상의 증상 수준</li>
                        <li><strong>조기 개입 필요성:</strong> 예방적 중재가 효과적인 시점</li>
                        <li><strong>데이터 분포:</strong> 충분한 이벤트 발생 비율 확보</li>
                        <li><strong>선행 연구 일치성:</strong> 기존 정신건강 연구와의 비교 가능성</li>
                    </ul>
                </div>
            </div>

            <!-- 향후 분석 방향 -->
            <div class="section">
                <h2>🎯 향후 분석 방향</h2>

                <div class="info-box">
                    <h4>모델 확장</h4>
                    <ul>
                        <li><strong>시간 의존 공변량:</strong> 센서 데이터의 시간적 변화 반영</li>
                        <li><strong>경쟁 위험 모델:</strong> 여러 이벤트 유형 동시 고려</li>
                        <li><strong>층화 Cox 모델:</strong> PH 가정 위배 시 층화 접근</li>
                        <li><strong>기계학습 기반 생존 분석:</strong> Random Survival Forest, DeepSurv 등</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>추가 검증</h4>
                    <ul>
                        <li><strong>외부 검증:</strong> 독립적인 코호트에서의 모델 성능 평가</li>
                        <li><strong>교차 검증:</strong> K-fold cross-validation으로 과적합 평가</li>
                        <li><strong>보정 곡선:</strong> 예측 확률의 정확도 평가</li>
                        <li><strong>민감도 분석:</strong> 임계값 변화에 따른 결과 안정성 검토</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>KLOSDOM Lifelog Pattern Data Generation System</strong></p>
            <p>Survival Analysis Data Aggregation and Table 1</p>
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
    print("생존 분석 데이터 취합 과정 및 Table 1 생성")
    print("="*80)

    # 데이터 로드
    datasets = load_survival_data()

    if not datasets:
        print("\n❌ 데이터를 찾을 수 없습니다.")
        return

    # HTML 리포트 생성
    html_content = generate_html_report(datasets)

    # 저장
    output_path = Path("survival_data_table1_report.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ HTML 리포트 생성 완료!")
    print(f"   📄 파일: {output_path.absolute()}")
    print(f"\n" + "="*80)

if __name__ == "__main__":
    main()
