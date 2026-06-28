// KLOSDOM 정신건강 통합 평가 엔진

// Depression 피노타입 중심점 (K-means centroids - 표준화 전 값)
const DEPRESSION_PHENOTYPES = {
    'Resilient-Normal': {
        name: '정상 회복형',
        description: '모든 생리 지표가 정상 범위에 있으며, 경미한 우울 증상만 존재합니다. 자연 회복 가능성이 높습니다.',
        centroid: {
            total_sleep: 380, rem_sleep: 116, deep_sleep: 73,
            heart_beat: 78, hrv: 25, oxygen_saturation: 97.4,
            body_temperature: 35.8, skin_temperature: 29.5,
            walk: 5000, stick_sensor: 12
        },
        intervention: [
            '정기적인 생활 패턴 유지',
            '적절한 운동과 수면 관리',
            '스트레스 관리 기법 학습',
            '정기적 자가 모니터링'
        ]
    },
    'Sleep-Disorder': {
        name: '수면장애형',
        description: '심각한 불면증 패턴으로 총 수면시간이 정상의 1/3 수준입니다. REM 수면 및 깊은 수면 모두 감소되어 있습니다.',
        centroid: {
            total_sleep: 131, rem_sleep: 40, deep_sleep: 25,
            heart_beat: 82, hrv: 22, oxygen_saturation: 96.8,
            body_temperature: 35.5, skin_temperature: 28.8,
            walk: 3500, stick_sensor: 8
        },
        intervention: [
            '수면 전문의 상담 권장',
            '인지행동 불면증 치료 (CBT-I)',
            '수면 위생 교육',
            '수면 환경 개선 (빛, 소음, 온도)',
            '규칙적인 수면-기상 시간 설정'
        ]
    },
    'Autonomic': {
        name: '자율신경형',
        description: '높은 HRV와 낮은 산소포화도로 자율신경계 불균형이 시사됩니다. 심혈관 건강과 연관될 수 있습니다.',
        centroid: {
            total_sleep: 350, rem_sleep: 105, deep_sleep: 68,
            heart_beat: 75, hrv: 202, oxygen_saturation: 93.4,
            body_temperature: 35.9, skin_temperature: 29.2,
            walk: 4200, stick_sensor: 10
        },
        intervention: [
            '자율신경 안정화 치료',
            '심호흡 및 명상 연습',
            '규칙적인 유산소 운동',
            '심혈관 건강 검진',
            '스트레스 관리 프로그램'
        ]
    }
};

// Stress 피노타입 중심점
const STRESS_PHENOTYPES = {
    'Resilient-Normal': {
        name: '정상 회복형',
        description: '정상 범위의 생리 지표를 보이며, 경미한 스트레스 증상만 있습니다. 자연 회복 가능성이 높습니다.',
        centroid: {
            total_sleep: 383, rem_sleep: 116, deep_sleep: 73,
            heart_beat: 78, hrv: 25, oxygen_saturation: 97.4,
            body_temperature: 35.8, skin_temperature: 29.5,
            walk: 4800, stick_sensor: 11
        },
        intervention: [
            '현재 대처 방식 유지',
            '규칙적인 생활 리듬',
            '적절한 휴식과 활동 균형',
            '정기적 자가 평가'
        ]
    },
    'Hypersomnia': {
        name: '과수면형',
        description: '총 수면시간이 8시간으로 과도하며, 낮은 심박수를 보입니다. 스트레스 회피 행동의 가능성이 있습니다.',
        centroid: {
            total_sleep: 480, rem_sleep: 140, deep_sleep: 95,
            heart_beat: 65, hrv: 28, oxygen_saturation: 97.8,
            body_temperature: 35.6, skin_temperature: 29.0,
            walk: 3200, stick_sensor: 8
        },
        intervention: [
            '인지행동치료 (CBT) - 회피 행동 수정',
            '적정 수면 시간 유지 (7-8시간)',
            '수면의 질 개선 집중',
            '활동 계획 수립',
            '스트레스 대처 기술 훈련',
            '건강한 활동으로 시간 채우기'
        ]
    },
    'Sleep-Disorder': {
        name: '수면장애형',
        description: '심각한 불면증으로 총 수면시간이 매우 적습니다. 스트레스로 인한 수면 부족이 관찰됩니다.',
        centroid: {
            total_sleep: 119, rem_sleep: 35, deep_sleep: 22,
            heart_beat: 85, hrv: 20, oxygen_saturation: 96.5,
            body_temperature: 35.7, skin_temperature: 29.8,
            walk: 5500, stick_sensor: 14
        },
        intervention: [
            '수면 전문의 상담',
            '스트레스 관리와 수면 개선 병행',
            'CBT-I (불면증 인지행동치료)',
            '이완 훈련 (progressive muscle relaxation)',
            '수면 환경 최적화'
        ]
    },
    'Autonomic': {
        name: '자율신경형',
        description: '높은 HRV와 낮은 산소포화도로 자율신경계 이상이 나타납니다.',
        centroid: {
            total_sleep: 340, rem_sleep: 100, deep_sleep: 65,
            heart_beat: 80, hrv: 180, oxygen_saturation: 94.1,
            body_temperature: 36.0, skin_temperature: 29.4,
            walk: 4500, stick_sensor: 11
        },
        intervention: [
            '자율신경 균형 회복 훈련',
            '바이오피드백 치료',
            '요가 및 명상',
            '규칙적인 운동',
            '스트레스 관리 프로그램'
        ]
    }
};

// Cox PH 모델 계수 (표준화된 값에 대한 계수)
const COX_COEFFICIENTS = {
    depression: {
        total_sleep: -0.285,  // 수면 감소 = 위험 증가
        rem_sleep: -0.198,
        deep_sleep: -0.242,
        heart_beat: 0.112,
        hrv: 0.215,  // HRV 증가 = 위험 증가 (부교감 우위)
        oxygen_saturation: -0.178,
        body_temperature: -0.095,
        skin_temperature: 0.058,
        walk: -0.165,  // 활동 감소 = 위험 증가
        stick_sensor: -0.092
    },
    stress: {
        total_sleep: 0.245,  // 양극단 (과다/부족 모두 위험)
        rem_sleep: 0.125,
        deep_sleep: 0.158,
        heart_beat: 0.328,  // 심박수 증가 = 위험 증가
        hrv: 0.182,
        oxygen_saturation: -0.095,
        body_temperature: 0.068,
        skin_temperature: 0.112,
        walk: 0.385,  // 과활동 = 위험 증가
        stick_sensor: 0.225
    }
};

// 정규 범위 (표준화 위한 평균과 표준편차)
const NORMALIZATION_PARAMS = {
    total_sleep: { mean: 382.5, std: 95.0 },
    rem_sleep: { mean: 116.0, std: 30.5 },
    deep_sleep: { mean: 73.0, std: 20.2 },
    heart_beat: { mean: 78.0, std: 12.5 },
    hrv: { mean: 25.0, std: 15.3 },
    oxygen_saturation: { mean: 97.4, std: 1.8 },
    body_temperature: { mean: 35.8, std: 0.8 },
    skin_temperature: { mean: 29.5, std: 2.5 },
    walk: { mean: 5000, std: 2500 },
    stick_sensor: { mean: 12, std: 5.5 }
};

// 유클리드 거리 계산
function euclideanDistance(values, centroid) {
    let sum = 0;
    for (let key in values) {
        if (centroid[key] !== undefined) {
            sum += Math.pow(values[key] - centroid[key], 2);
        }
    }
    return Math.sqrt(sum);
}

// 피노타입 분류
function classifyPhenotype(values, phenotypes) {
    let minDistance = Infinity;
    let closestPhenotype = null;

    for (let phenotypeName in phenotypes) {
        const phenotype = phenotypes[phenotypeName];
        const distance = euclideanDistance(values, phenotype.centroid);

        if (distance < minDistance) {
            minDistance = distance;
            closestPhenotype = phenotypeName;
        }
    }

    return {
        type: closestPhenotype,
        info: phenotypes[closestPhenotype],
        distance: minDistance
    };
}

// Z-score 정규화
function normalize(values) {
    const normalized = {};
    for (let key in values) {
        const params = NORMALIZATION_PARAMS[key];
        if (params) {
            normalized[key] = (values[key] - params.mean) / params.std;
        }
    }
    return normalized;
}

// Cox PH 위험도 계산
function calculateRiskScore(normalizedValues, coefficients) {
    let linearPredictor = 0;

    for (let key in normalizedValues) {
        if (coefficients[key] !== undefined) {
            linearPredictor += coefficients[key] * normalizedValues[key];
        }
    }

    // Hazard Ratio
    const hazardRatio = Math.exp(linearPredictor);

    // 위험도 레벨 분류
    let riskLevel, riskColor;
    if (hazardRatio < 1.2) {
        riskLevel = '낮음 (Low)';
        riskColor = 'risk-low';
    } else if (hazardRatio < 1.8) {
        riskLevel = '중간 (Moderate)';
        riskColor = 'risk-moderate';
    } else {
        riskLevel = '높음 (High)';
        riskColor = 'risk-high';
    }

    return {
        hazardRatio: hazardRatio,
        riskLevel: riskLevel,
        riskColor: riskColor,
        linearPredictor: linearPredictor
    };
}

// 주요 위험 인자 식별
function identifyRiskFactors(normalizedValues, coefficients, values) {
    const factors = [];

    for (let key in normalizedValues) {
        if (coefficients[key] !== undefined) {
            const contribution = coefficients[key] * normalizedValues[key];
            if (Math.abs(contribution) > 0.15) {  // 임계값
                let direction = contribution > 0 ? '증가' : '감소';
                let impact = contribution > 0 ? '위험 증가' : '위험 감소';

                factors.push({
                    variable: getKoreanName(key),
                    value: values[key].toFixed(1),
                    contribution: contribution,
                    direction: direction,
                    impact: impact
                });
            }
        }
    }

    // 기여도 절대값 기준 정렬
    factors.sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));

    return factors;
}

// 한글 변수명 변환
function getKoreanName(key) {
    const names = {
        'total_sleep': '총 수면시간',
        'rem_sleep': 'REM 수면',
        'deep_sleep': '깊은 수면',
        'heart_beat': '심박수',
        'hrv': '심박변이도',
        'oxygen_saturation': '산소포화도',
        'body_temperature': '체온',
        'skin_temperature': '피부온도',
        'walk': '걷기',
        'stick_sensor': '스틱 센서'
    };
    return names[key] || key;
}

// 메인 평가 함수
function assessMentalHealth() {
    // 입력값 수집
    const values = {
        total_sleep: parseFloat(document.getElementById('total_sleep').value) || 0,
        rem_sleep: parseFloat(document.getElementById('rem_sleep').value) || 0,
        deep_sleep: parseFloat(document.getElementById('deep_sleep').value) || 0,
        heart_beat: parseFloat(document.getElementById('heart_beat').value) || 0,
        hrv: parseFloat(document.getElementById('hrv').value) || 0,
        oxygen_saturation: parseFloat(document.getElementById('oxygen_saturation').value) || 0,
        body_temperature: parseFloat(document.getElementById('body_temperature').value) || 0,
        skin_temperature: parseFloat(document.getElementById('skin_temperature').value) || 0,
        walk: parseFloat(document.getElementById('walk').value) || 0,
        stick_sensor: parseFloat(document.getElementById('stick_sensor').value) || 0
    };

    // 유효성 검사
    let hasInvalidInput = false;
    for (let key in values) {
        if (values[key] === 0 || isNaN(values[key])) {
            hasInvalidInput = true;
            break;
        }
    }

    if (hasInvalidInput) {
        alert('모든 센서 데이터를 입력해주세요.');
        return;
    }

    // 정규화
    const normalizedValues = normalize(values);

    // Depression 평가
    const depPhenotype = classifyPhenotype(values, DEPRESSION_PHENOTYPES);
    const depRisk = calculateRiskScore(normalizedValues, COX_COEFFICIENTS.depression);
    const depFactors = identifyRiskFactors(normalizedValues, COX_COEFFICIENTS.depression, values);

    // Stress 평가
    const stressPhenotype = classifyPhenotype(values, STRESS_PHENOTYPES);
    const stressRisk = calculateRiskScore(normalizedValues, COX_COEFFICIENTS.stress);
    const stressFactors = identifyRiskFactors(normalizedValues, COX_COEFFICIENTS.stress, values);

    // 결과 표시
    displayResults(depPhenotype, depRisk, depFactors, stressPhenotype, stressRisk, stressFactors);
}

// 결과 표시
function displayResults(depPhenotype, depRisk, depFactors, stressPhenotype, stressRisk, stressFactors) {
    const resultsDiv = document.getElementById('results');

    let html = `
        <div class="result-card">
            <h3>💙 우울 (Depression) 평가 결과</h3>

            <div class="phenotype-box">
                <div class="phenotype-title">
                    피노타입: ${depPhenotype.info.name} (${depPhenotype.type})
                </div>
                <div class="phenotype-description">
                    ${depPhenotype.info.description}
                </div>

                <div class="recommendation-box" style="margin-top: 20px;">
                    <h4>권장 중재 전략</h4>
                    <ul>
                        ${depPhenotype.info.intervention.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>

            <div class="risk-box">
                <div style="font-size: 1.2em; color: #666; margin-bottom: 10px;">
                    이벤트 발생 위험도
                </div>
                <div class="risk-level ${depRisk.riskColor}">
                    ${depRisk.riskLevel}
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-label">Hazard Ratio</div>
                        <div class="metric-value">${depRisk.hazardRatio.toFixed(2)}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Linear Predictor</div>
                        <div class="metric-value">${depRisk.linearPredictor.toFixed(3)}</div>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">주요 위험 인자</h4>
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        ${depFactors.slice(0, 5).map(factor => `
                            <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
                                <strong>${factor.variable}:</strong> ${factor.value}
                                <span style="color: ${factor.contribution > 0 ? '#f44336' : '#4caf50'}; margin-left: 10px;">
                                    (${factor.impact})
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>

        <div class="result-card">
            <h3>💚 스트레스 (Stress) 평가 결과</h3>

            <div class="phenotype-box">
                <div class="phenotype-title">
                    피노타입: ${stressPhenotype.info.name} (${stressPhenotype.type})
                </div>
                <div class="phenotype-description">
                    ${stressPhenotype.info.description}
                </div>

                <div class="recommendation-box" style="margin-top: 20px;">
                    <h4>권장 중재 전략</h4>
                    <ul>
                        ${stressPhenotype.info.intervention.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>

            <div class="risk-box">
                <div style="font-size: 1.2em; color: #666; margin-bottom: 10px;">
                    이벤트 발생 위험도
                </div>
                <div class="risk-level ${stressRisk.riskColor}">
                    ${stressRisk.riskLevel}
                </div>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-label">Hazard Ratio</div>
                        <div class="metric-value">${stressRisk.hazardRatio.toFixed(2)}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">Linear Predictor</div>
                        <div class="metric-value">${stressRisk.linearPredictor.toFixed(3)}</div>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="color: #333; margin-bottom: 10px;">주요 위험 인자</h4>
                    <div style="background: white; padding: 15px; border-radius: 8px;">
                        ${stressFactors.slice(0, 5).map(factor => `
                            <div style="padding: 8px 0; border-bottom: 1px solid #eee;">
                                <strong>${factor.variable}:</strong> ${factor.value}
                                <span style="color: ${factor.contribution > 0 ? '#f44336' : '#4caf50'}; margin-left: 10px;">
                                    (${factor.impact})
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>

        <div class="recommendation-box" style="margin-top: 30px;">
            <h4>🎯 종합 권장사항</h4>
            <p style="margin-bottom: 15px; color: #333;">
                개인의 피노타입과 위험도를 고려한 맞춤형 중재 전략입니다.
            </p>
            <ul>
                <li><strong>우선순위:</strong> ${
                    depRisk.hazardRatio > stressRisk.hazardRatio ? '우울' : '스트레스'
                } 관리에 먼저 집중하세요.</li>
                <li><strong>정기 모니터링:</strong> 센서 데이터를 주 1회 재평가하여 변화 추적</li>
                <li><strong>전문가 상담:</strong> 위험도가 '높음'인 경우 전문의 상담 권장</li>
                <li><strong>생활 습관:</strong> 규칙적인 수면, 적절한 운동, 균형 잡힌 식사 유지</li>
                <li><strong>스트레스 관리:</strong> 명상, 요가, 호흡법 등 이완 기법 실천</li>
            </ul>
            <p style="margin-top: 15px; padding: 15px; background: rgba(255,255,255,0.5); border-radius: 8px; color: #666; font-size: 0.95em;">
                ⚠️ <strong>주의:</strong> 본 평가 결과는 연구 목적의 참고 자료이며, 실제 임상 진단을 대체할 수 없습니다.
                정신건강에 대한 우려가 있다면 반드시 전문의와 상담하시기 바랍니다.
            </p>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';

    // 결과로 스크롤
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
