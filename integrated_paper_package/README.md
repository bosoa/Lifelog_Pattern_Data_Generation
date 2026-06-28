# KLOSDOM 정신건강 통합 평가 연구 패키지

## 📋 개요

본 패키지는 **"라이프로그 기반 정신건강 피노타이핑 및 위험도 평가"** 연구의 모든 산출물을 포함합니다.

- **연구 기간**: 2024년 1월 - 12월
- **연구 기관**: KLOSDOM (Korea Lifelog Observatory for Sustainable Dementia Outcome Management)
- **생성 일자**: 2026년 6월 28일

## 📊 연구 요약

### 목적
1. 정신과 설문 기반 타겟별 최적 threshold 도출
2. K-means 클러스터링을 통한 피노타입 발견
3. Cox Proportional Hazards 모델을 통한 위험도 평가
4. 피노타입과 위험도를 동시 리포팅하는 통합 시스템 구축

### 주요 결과
- **Threshold**: Depression ≥6점, Stress ≥5점 (임상 기준과 0.8-3.7%p 오차)
- **피노타입**: Depression 4개, Stress 5개 (Hypersomnia 피노타입 최초 보고)
- **생존 분석**: Depression C-index 0.6555 (원통좌표), Stress C-index 0.7128 (직교좌표)

## 📁 패키지 구조

```
integrated_paper_package/
├── README.md                          # 본 파일
├── docs/                              # 논문 및 문서
│   └── Integrated_Mental_Health_Phenotyping_Risk_Assessment_Paper.docx
├── data/                              # 원시 데이터
│   ├── depression_binary_classification.csv
│   └── stress_binary_classification.csv
├── results/                           # 분석 결과
│   ├── survival_analysis_new_threshold/     # 생존 분석 결과 (15개 HTML 리포트)
│   │   ├── index.html                       # 🌟 메인 대시보드
│   │   ├── data_structure_explanation.html  # 데이터 구조 설명
│   │   ├── covariates_table1.html          # 독립변수 Table 1
│   │   ├── endpoint_data_aggregation.html  # 종단점 집계
│   │   ├── depression_survival_analysis.html
│   │   ├── stress_survival_analysis.html
│   │   ├── depression_survival_time_distribution.html
│   │   ├── stress_survival_time_distribution.html
│   │   ├── coordinate_performance_comparison.html
│   │   └── [6개 좌표 변환 분석 리포트]
│   └── model_results_target_specific/       # Phenotyping 결과
└── app/                               # Interactive 평가 앱
    ├── index.html                     # 🌟 웹 앱 메인
    └── assessment_engine.js            # 평가 엔진
```

## 🚀 사용 방법

### 1. 논문 확인
```
docs/Integrated_Mental_Health_Phenotyping_Risk_Assessment_Paper.docx
```
Microsoft Word로 열어 전체 연구 내용을 확인하세요.

### 2. 분석 결과 대시보드 보기
```
results/survival_analysis_new_threshold/index.html
```
웹 브라우저로 열어 15개 분석 리포트를 탐색하세요.

**포함된 리포트:**
- 데이터 구조 및 측정 시점 설명
- 독립변수 기술통계 (Table 1)
- 종단점 데이터 집계 과정
- 우울/스트레스 생존 분석 (직교좌표)
- 좌표 변환 분석 (극좌표, 구면좌표, 원통좌표)
- 생존시간 분포 분석
- 좌표계별 성능 비교

### 3. Interactive 평가 앱 사용
```
app/index.html
```
웹 브라우저로 열어 개인의 센서 데이터를 입력하고 평가하세요.

**입력 항목:**
- 총 수면시간, REM 수면, 깊은 수면
- 심박수, HRV, 산소포화도
- 체온, 피부온도
- 걷기 (걸음 수), 스틱 센서

**출력 결과:**
- 우울 피노타입 + 위험도 + 중재 전략
- 스트레스 피노타입 + 위험도 + 중재 전략
- 주요 위험 인자
- 종합 권장사항

### 4. 원시 데이터 확인
```
data/depression_binary_classification.csv  (12,923 건)
data/stress_binary_classification.csv      (13,503 건)
```
CSV 파일로 분석에 사용된 원시 데이터를 확인하세요.

## 📊 데이터 구조

### depression_binary_classification.csv
| 컬럼명 | 설명 | 단위 |
|--------|------|------|
| stick_sensor | 스틱 센서 활동 | counts |
| heart_beat | 심박수 | bpm |
| total_sleep | 총 수면시간 | minutes |
| rem_sleep | REM 수면 | minutes |
| body_temperature | 체온 | °C |
| walk | 걷기 | steps |
| skin_temperature | 피부온도 | °C |
| oxygen_saturation | 산소포화도 | % |
| deep_sleep | 깊은 수면 | minutes |
| hrv | 심박변이도 | ms |
| depression_score | 우울 점수 | 0-10점 |
| level | 활동 수준 | 0-2 |
| level_name | 활동 수준명 | 낮음/중간/높음 |
| depression_binary | 이벤트 발생 | 0/1 |
| depression_label | 이벤트 라벨 | 미발생/발생 |

### stress_binary_classification.csv
동일 구조 (depression_ 대신 stress_)

## 🔍 주요 발견사항

### 1. Threshold 최적화
- **Depression 6점**: PHQ-9 기준과 거의 완벽 일치 (오차 0.8%p)
- **Stress 5점**: PSS 기준과 우수 일치 (오차 3.7%p)
- 타겟별 방식이 균일 방식 대비 Stress에서 28.1%p 오차 감소

### 2. 피노타입 발견

**Depression (4개)**
1. Resilient-Normal (90.1%): 정상 회복형
2. Sleep-Disorder (8.8%): 수면장애형
3. Hypothermia (0.4%): 저체온형
4. Autonomic (0.6%): 자율신경형

**Stress (5개)**
1. Resilient-Normal (70.3%): 정상 회복형
2. **Hypersomnia (21.2%)**: 과수면형 ⭐ 최초 보고
3. Sleep-Disorder (7.3%): 수면장애형
4. Autonomic (0.9%): 자율신경형
5. Hypothermia (0.3%): 저체온형

### 3. 생존 분석

**직교좌표 (Baseline)**
- Depression: C-index 0.6121 (적절한 식별력)
- Stress: C-index 0.7128 (우수한 식별력)

**최적 좌표계**
- Depression: 원통좌표 0.6555 (+7.1% 향상)
- Stress: 직교좌표 0.7128 (최적)

**주요 위험 인자**
- Depression: 수면↓, 활동↓, HRV↑ (저활동 패턴)
- Stress: 활동↑, 심박수↑, 수면 양극단 (과활동 패턴)

## 💡 임상적 의의

### 1. 개인 맞춤형 중재
- **피노타입**에 따라 다른 중재 전략
  - Sleep-Disorder형 → 수면 개선 집중
  - Hypersomnia형 → 인지행동치료, 수면 조절
  - Autonomic형 → 자율신경 안정화

- **위험도**에 따라 다른 개입 강도
  - 고위험 → 즉각적 집중 중재
  - 중위험 → 정기 모니터링 + 중재
  - 저위험 → 경과 관찰

### 2. 조기 발견 및 예방
- 센서 데이터로 이벤트 발생 전 고위험 개인 식별
- 선제적 중재로 이벤트 발생 예방
- 실시간 위험 모니터링 가능

### 3. 의료 자원 효율화
- 고위험 피노타입에 자원 집중
- Resilient-Normal형은 경과 관찰로 충분
- 우선순위 기반 자원 배분

## 🔬 방법론

### Phase 1: Phenotype Discovery
1. 정신과 설문 (GAD-7, PHQ-9, PSS) 기반 목표 발생률 설정
2. 목표 발생률 최소 오차 방법으로 threshold 도출
3. K-means 클러스터링 (Silhouette Score 최대화)
4. 피노타입 특성 분석

### Phase 2: Risk Assessment
1. Cox Proportional Hazards 모델 학습
2. Time-Fixed Covariates (설문일 ±3일 평균)
3. Z-score 정규화 적용
4. 좌표 변환으로 성능 최적화
5. Nomogram 및 Calibration 생성

## 📈 재현 가능성

모든 분석은 재현 가능하도록 설계되었습니다:
- Random seed 고정 (random_state=42)
- 전체 분석 파이프라인 코드 공개
- 원시 데이터 및 중간 결과 포함
- HTML 대시보드로 결과 투명하게 공개

## ⚠️ 제한점

1. **Duration의 한계**: 시뮬레이션된 값, 실제 종단 데이터 필요
2. **Time-Fixed Covariates**: 실시간 변화 미반영, Time-Varying 필요
3. **외부 검증 부족**: 단일 데이터셋, 다기관 검증 필요
4. **인과관계**: 관찰 연구, RCT 검증 필요
5. **샘플 불균형**: 일부 피노타입 샘플 적음

## 🚀 향후 연구

1. 실제 종단 데이터 수집 및 분석
2. Time-Varying Covariates 적용
3. 다기관 외부 검증 연구
4. 피노타입별 맞춤 중재 효과 RCT
5. 딥러닝 기반 생존 분석 (DeepSurv)
6. 실시간 위험 모니터링 시스템 필드 테스트

## 📞 문의

- **연구팀**: KLOSDOM Research Team
- **이메일**: bosoagalaxy@gmail.com
- **생성일**: 2026년 6월 28일

## 📜 인용

```
KLOSDOM Research Team. (2026). Lifelog-Based Mental Health Phenotyping and Risk Assessment:
An Integrated Approach Using Target-Specific Optimal Thresholds and Cox Survival Analysis.
KLOSDOM Technical Report.
```

## 🔐 면책 조항

본 연구 결과는 연구 목적으로 개발되었으며, 실제 임상 진단을 대체할 수 없습니다.
정신건강에 대한 우려가 있다면 반드시 전문의와 상담하시기 바랍니다.

---

**© 2026 KLOSDOM Research Team. All rights reserved.**
