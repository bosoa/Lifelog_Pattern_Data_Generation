#!/usr/bin/env python3
"""
종단점까지의 생존시간 분포 시각화
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import base64
from io import BytesIO
from datetime import datetime
import sys

sys.path.append('src')
from survival_analysis import SurvivalAnalyzer

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

def create_survival_time_plots(surv_data, target, threshold):
    """생존시간 분포 시각화"""

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle(f'{target.upper()} 종단점까지의 생존시간 분포 (임계값 ≥{threshold}점)',
                 fontsize=18, fontweight='bold', y=0.995)

    # 1. Duration 전체 분포 (히스토그램)
    ax = axes[0, 0]
    ax.hist(surv_data['duration'], bins=50, color='#667eea', alpha=0.7, edgecolor='black')
    ax.axvline(surv_data['duration'].mean(), color='red', linestyle='--',
               linewidth=2, label=f'평균: {surv_data["duration"].mean():.2f}일')
    ax.axvline(surv_data['duration'].median(), color='orange', linestyle='--',
               linewidth=2, label=f'중앙값: {surv_data["duration"].median():.2f}일')
    ax.set_xlabel('Duration (일)', fontsize=12, fontweight='bold')
    ax.set_ylabel('빈도', fontsize=12, fontweight='bold')
    ax.set_title('(A) 생존시간 전체 분포', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 2. Event 발생 여부별 Duration 분포 (박스플롯)
    ax = axes[0, 1]
    event_data = [surv_data[surv_data['event'] == 0]['duration'],
                  surv_data[surv_data['event'] == 1]['duration']]
    bp = ax.boxplot(event_data, labels=['Censored (미발생)', 'Event (발생)'],
                    patch_artist=True, widths=0.6)
    bp['boxes'][0].set_facecolor('#4caf50')
    bp['boxes'][1].set_facecolor('#f44336')
    ax.set_ylabel('Duration (일)', fontsize=12, fontweight='bold')
    ax.set_title('(B) 이벤트 발생 여부별 생존시간', fontsize=13, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

    # 3. Level별 Duration 분포 (바이올린 플롯)
    ax = axes[0, 2]
    level_data = [surv_data[surv_data['level'] == level]['duration']
                  for level in sorted(surv_data['level'].unique())]
    parts = ax.violinplot(level_data, positions=sorted(surv_data['level'].unique()),
                          showmeans=True, showmedians=True)
    for pc in parts['bodies']:
        pc.set_facecolor('#667eea')
        pc.set_alpha(0.7)
    ax.set_xlabel('Activity Level', fontsize=12, fontweight='bold')
    ax.set_ylabel('Duration (일)', fontsize=12, fontweight='bold')
    ax.set_title('(C) 활동 수준별 생존시간 분포', fontsize=13, fontweight='bold')
    ax.set_xticks(sorted(surv_data['level'].unique()))
    ax.set_xticklabels([f'Level {l}' for l in sorted(surv_data['level'].unique())])
    ax.grid(axis='y', alpha=0.3)

    # 4. Level별 Event 발생률 (스택 바 차트)
    ax = axes[1, 0]
    event_by_level = surv_data.groupby(['level', 'event']).size().unstack(fill_value=0)
    event_by_level_pct = event_by_level.div(event_by_level.sum(axis=1), axis=0) * 100

    event_by_level_pct.plot(kind='bar', stacked=True, ax=ax,
                            color=['#4caf50', '#f44336'], width=0.7)
    ax.set_xlabel('Activity Level', fontsize=12, fontweight='bold')
    ax.set_ylabel('비율 (%)', fontsize=12, fontweight='bold')
    ax.set_title('(D) 활동 수준별 이벤트 발생률', fontsize=13, fontweight='bold')
    ax.set_xticklabels([f'Level {l}' for l in sorted(surv_data['level'].unique())],
                       rotation=0)
    ax.legend(['Censored', 'Event'], loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    # 5. Duration vs Score (산점도)
    ax = axes[1, 1]
    score_col = f'{target}_score'
    event_mask = surv_data['event'] == 1
    ax.scatter(surv_data[~event_mask]['duration'],
               surv_data[~event_mask][score_col],
               c='#4caf50', alpha=0.5, s=30, label='Censored')
    ax.scatter(surv_data[event_mask]['duration'],
               surv_data[event_mask][score_col],
               c='#f44336', alpha=0.7, s=50, marker='^', label='Event')
    ax.axhline(threshold, color='red', linestyle='--', linewidth=2,
               label=f'임계값 = {threshold}')
    ax.set_xlabel('Duration (일)', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{target.capitalize()} Score', fontsize=12, fontweight='bold')
    ax.set_title('(E) 생존시간 vs 점수', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 6. 누적 이벤트 발생 곡선
    ax = axes[1, 2]
    event_times = surv_data[surv_data['event'] == 1]['duration'].sort_values()
    cumulative_events = np.arange(1, len(event_times) + 1)
    ax.plot(event_times, cumulative_events, linewidth=2.5, color='#667eea',
            marker='o', markersize=4, markerfacecolor='white', markeredgewidth=1.5)
    ax.fill_between(event_times, 0, cumulative_events, alpha=0.3, color='#667eea')
    ax.set_xlabel('Duration (일)', fontsize=12, fontweight='bold')
    ax.set_ylabel('누적 이벤트 발생 수', fontsize=12, fontweight='bold')
    ax.set_title('(F) 누적 이벤트 발생 곡선', fontsize=13, fontweight='bold')
    ax.grid(alpha=0.3)

    plt.tight_layout()

    # Base64 인코딩
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close(fig)

    return f'data:image/png;base64,{image_base64}'

def create_summary_statistics_table(surv_data, target, threshold):
    """생존시간 요약 통계 테이블 생성"""

    stats = []

    # 전체
    stats.append({
        'Group': '전체',
        'N': len(surv_data),
        'Events': surv_data['event'].sum(),
        'Event Rate': f"{surv_data['event'].mean()*100:.2f}%",
        'Mean Duration': f"{surv_data['duration'].mean():.2f}",
        'Median Duration': f"{surv_data['duration'].median():.2f}",
        'SD Duration': f"{surv_data['duration'].std():.2f}"
    })

    # Event 발생 그룹
    event_group = surv_data[surv_data['event'] == 1]
    stats.append({
        'Group': 'Event 발생',
        'N': len(event_group),
        'Events': event_group['event'].sum(),
        'Event Rate': '100.00%',
        'Mean Duration': f"{event_group['duration'].mean():.2f}",
        'Median Duration': f"{event_group['duration'].median():.2f}",
        'SD Duration': f"{event_group['duration'].std():.2f}"
    })

    # Censored 그룹
    censored_group = surv_data[surv_data['event'] == 0]
    stats.append({
        'Group': 'Censored',
        'N': len(censored_group),
        'Events': 0,
        'Event Rate': '0.00%',
        'Mean Duration': f"{censored_group['duration'].mean():.2f}",
        'Median Duration': f"{censored_group['duration'].median():.2f}",
        'SD Duration': f"{censored_group['duration'].std():.2f}"
    })

    # Level별
    for level in sorted(surv_data['level'].unique()):
        level_data = surv_data[surv_data['level'] == level]
        level_name = level_data['level_name'].iloc[0] if 'level_name' in level_data.columns else f'Level {level}'
        stats.append({
            'Group': f'Level {level} ({level_name})',
            'N': len(level_data),
            'Events': level_data['event'].sum(),
            'Event Rate': f"{level_data['event'].mean()*100:.2f}%",
            'Mean Duration': f"{level_data['duration'].mean():.2f}",
            'Median Duration': f"{level_data['duration'].median():.2f}",
            'SD Duration': f"{level_data['duration'].std():.2f}"
        })

    return pd.DataFrame(stats)

def generate_html_report(target, threshold):
    """HTML 리포트 생성"""

    print(f"\n{'='*70}")
    print(f"{target.upper()} 생존시간 분포 분석")
    print(f"{'='*70}")

    # 데이터 로드
    data_path = Path("hierarchical_data") / f"{target}_binary_classification.csv"
    df = pd.read_csv(data_path)

    # 이진화
    df[f'{target}_binary'] = (df[f'{target}_score'] >= threshold).astype(int)

    print(f"   ✓ 데이터 로드: {len(df):,} 행")

    # 생존 데이터 준비
    analyzer = SurvivalAnalyzer()
    surv_data = analyzer.prepare_survival_data(df, target)

    print(f"   ✓ 생존 데이터 준비 완료")

    # 시각화 생성
    print(f"   📊 생존시간 분포 시각화 생성 중...")
    survival_time_plot = create_survival_time_plots(surv_data, target, threshold)

    # 통계 테이블 생성
    stats_table = create_summary_statistics_table(surv_data, target, threshold)

    # HTML 생성
    html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target.upper()} 생존시간 분포 분석</title>
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
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            border-radius: 12px;
            box-shadow: 0 6px 12px rgba(0,0,0,0.1);
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
            <h1>⏱️ {target.upper()} 생존시간 분포 분석</h1>
            <p>Survival Time Distribution Analysis</p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                임계값: {target.capitalize()} Score ≥ {threshold}점 |
                생성 일시: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")}
            </p>
        </div>

        <div class="content">
            <!-- 개요 -->
            <div class="section">
                <h2>📋 분석 개요</h2>
                <div class="info-box">
                    <h4>생존시간(Duration)이란?</h4>
                    <p>
                        생존 분석에서 생존시간(Duration)은 관측 시작부터 이벤트 발생(또는 관측 종료)까지의 시간을 의미합니다.
                        본 분석에서는 활동 수준(Level)에 따라 차등화된 관측 기간을 설정하였습니다:
                    </p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>Level 0 (낮은 활동):</strong> 10-40일 범위</li>
                        <li><strong>Level 1 (중간 활동):</strong> 40-70일 범위</li>
                        <li><strong>Level 2 (높은 활동):</strong> 70-93일 범위</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>이벤트 정의</h4>
                    <p>
                        {target.capitalize()} 점수가 <strong>{threshold}점 이상</strong>일 때 이벤트 발생으로 정의합니다.
                        이는 임상적으로 의미있는 {'중등도 이상 우울 증상' if target == 'depression' else '중간 이상 스트레스 수준'}을 나타냅니다.
                    </p>
                </div>
            </div>

            <!-- 요약 통계 -->
            <div class="section">
                <h2>📊 생존시간 요약 통계</h2>
                <div style="overflow-x: auto;">
                    {stats_table.to_html(index=False, border=0)}
                </div>

                <div class="info-box" style="margin-top: 30px;">
                    <h4>해석 가이드</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>N:</strong> 샘플 수</li>
                        <li><strong>Events:</strong> 이벤트 발생 건수</li>
                        <li><strong>Event Rate:</strong> 이벤트 발생률 (Events/N × 100%)</li>
                        <li><strong>Mean Duration:</strong> 평균 생존시간 (일)</li>
                        <li><strong>Median Duration:</strong> 중앙 생존시간 (일)</li>
                        <li><strong>SD Duration:</strong> 생존시간의 표준편차</li>
                    </ul>
                </div>
            </div>

            <!-- 시각화 -->
            <div class="section">
                <h2>📈 생존시간 분포 시각화</h2>
                <div class="chart-container">
                    <img src="{survival_time_plot}" alt="Survival Time Distribution" />
                </div>

                <div class="info-box" style="margin-top: 30px;">
                    <h4>그래프 해석</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>(A) 전체 분포:</strong> 모든 관측치의 생존시간 히스토그램. 평균과 중앙값으로 중심경향 파악</li>
                        <li><strong>(B) 이벤트별 분포:</strong> 이벤트 발생 여부에 따른 생존시간 차이. 박스플롯으로 중앙값과 사분위수 비교</li>
                        <li><strong>(C) 활동 수준별:</strong> Level별 생존시간 분포. 바이올린 플롯으로 분포의 형태 시각화</li>
                        <li><strong>(D) 이벤트 발생률:</strong> 각 Level에서의 이벤트 발생 비율. 활동 수준과 이벤트 발생의 관계 확인</li>
                        <li><strong>(E) 시간 vs 점수:</strong> 생존시간과 {target} 점수의 관계. 임계값을 기준으로 이벤트 발생 패턴 관찰</li>
                        <li><strong>(F) 누적 곡선:</strong> 시간에 따른 누적 이벤트 발생 수. 이벤트 발생 속도 파악</li>
                    </ul>
                </div>
            </div>

            <!-- 주요 발견사항 -->
            <div class="section">
                <h2>💡 주요 발견사항</h2>

                <div class="info-box">
                    <h4>1. 생존시간 분포</h4>
                    <p>
                        평균 생존시간: <strong>{surv_data['duration'].mean():.2f}일</strong><br>
                        중앙 생존시간: <strong>{surv_data['duration'].median():.2f}일</strong><br>
                        범위: <strong>{surv_data['duration'].min():.2f} - {surv_data['duration'].max():.2f}일</strong>
                    </p>
                </div>

                <div class="info-box">
                    <h4>2. 이벤트 발생</h4>
                    <p>
                        총 이벤트 발생: <strong>{surv_data['event'].sum():,}건</strong><br>
                        이벤트 발생률: <strong>{surv_data['event'].mean()*100:.2f}%</strong><br>
                        Censored (미발생): <strong>{(~surv_data['event'].astype(bool)).sum():,}건</strong>
                    </p>
                </div>

                <div class="info-box">
                    <h4>3. 활동 수준별 차이</h4>
"""

    # Level별 통계 추가
    for level in sorted(surv_data['level'].unique()):
        level_data = surv_data[surv_data['level'] == level]
        html_content += f"""
                    <p style="margin-top: 10px;">
                        <strong>Level {level}:</strong><br>
                        • 평균 생존시간: {level_data['duration'].mean():.2f}일<br>
                        • 이벤트 발생률: {level_data['event'].mean()*100:.2f}%<br>
                        • 샘플 수: {len(level_data):,}건
                    </p>
"""

    html_content += """
                </div>
            </div>

            <!-- 데이터 구조 설명 -->
            <div class="section">
                <h2>🔍 데이터 구조 설명</h2>

                <div class="info-box">
                    <h4>Cox PH 모델 입력 데이터 형태</h4>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li><strong>각 행 = 하나의 독립적인 관측 단위</strong></li>
                        <li><strong>각 센서 변수 = 변수당 하나의 값 (스칼라)</strong></li>
                        <li><strong>Cross-sectional 데이터</strong> (특정 시점의 측정값)</li>
                        <li><strong>Time-Fixed Covariates</strong> (시간에 따라 변하지 않는 공변량)</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h4>시간 의존적 공변량과의 차이</h4>
                    <p><strong>현재 방식 (Time-Fixed):</strong></p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>각 관측치는 고정된 센서 값을 가짐</li>
                        <li>계산이 간단하고 해석이 용이함</li>
                        <li>특정 시점의 상태를 기반으로 위험 예측</li>
                    </ul>

                    <p style="margin-top: 15px;"><strong>대안 (Time-Varying Covariates):</strong></p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>시간에 따라 센서 값이 변화하는 것을 반영</li>
                        <li>더 복잡하지만 실시간 변화 포착 가능</li>
                        <li>향후 연구에서 고려 가능</li>
                    </ul>
                </div>
            </div>
        </div>

        <div style="background: #f8f9fa; text-align: center; padding: 40px; color: #666;">
            <p><strong>KLOSDOM Lifelog Pattern Data Generation System</strong></p>
            <p>Survival Time Distribution Analysis</p>
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
    print("생존시간 분포 분석 리포트 생성")
    print("="*80)

    output_dir = Path("survival_analysis_new_threshold")
    output_dir.mkdir(exist_ok=True)

    # 임계값
    thresholds = {
        'depression': 6,
        'stress': 5
    }

    for target, threshold in thresholds.items():
        html_content = generate_html_report(target, threshold)

        output_path = output_dir / f"{target}_survival_time_distribution.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"   ✅ {target.upper()} 리포트 생성 완료: {output_path}")

    print(f"\n" + "="*80)
    print("✅ 모든 생존시간 분포 분석 완료!")
    print(f"   📁 결과 디렉토리: {output_dir.absolute()}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
