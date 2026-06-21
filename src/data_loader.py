"""
데이터 로드 및 전처리 모듈
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List


class KLOSDOMDataLoader:
    """KLOSDOM 데이터셋 로더"""

    def __init__(self, data_dir: str = "KLOSDOM_Preprocessed_Dataset"):
        self.data_dir = Path(data_dir)

        # 센서 데이터 파일 목록 (독립변수)
        self.sensor_files = {
            'hrv': 'whole_a01_hrv_20260621.csv',
            'walk': 'whole_a02_walk_20260621.csv',
            'stick_sensor': 'whole_a03_stick_sensor_activity_20260621.csv',
            'deep_sleep': 'whole_a04_deep_sleep_20260621.csv',
            'rem_sleep': 'whole_a05_rem_sleep_20260621.csv',
            'oxygen_saturation': 'whole_a06_oxygen_saturation_20260621.csv',
            'screen_time': 'whole_a07_screen_time_20260621.csv',
            'heart_beat': 'whole_a08_heart_beat_20260621.csv',
            'body_temperature': 'whole_a09_body_temperature_20260621.csv',
            'light_sleep': 'whole_a10_light_sleep_time_20260621.csv',
            'moving_distance': 'whole_a11_moving_distance_20260621.csv',
            'wakeup_time': 'whole_a12_wakeup_time_20260621.csv',
            'bed_time': 'whole_a13_bed_time_20260621.csv',
            'lux_sensor': 'whole_a14_lux_sensor_20260621.csv',
            'total_sleep': 'whole_a15_total_sleep_time_20260621.csv',
            'skin_temperature': 'whole_a16_skin_temperature_20260621.csv',
            'blood_sugar': 'whole_a17_blood_sugar_20260621.csv',
            'blood_pressure': 'whole_a18_blood_pressure_20260621.csv',
        }

        # 설문 데이터 파일 목록 (종속변수)
        self.survey_files = {
            'anxiety': 'whole_e01_anxiety_20260621.csv',
            'depression': 'whole_e02_depression_20260621.csv',
            'sleep_quality': 'whole_e03_sleep_20260621.csv',
            'stress': 'whole_e04_stress_20260621.csv',
        }

    def load_sensor_data(self) -> Dict[str, pd.DataFrame]:
        """모든 센서 데이터 로드"""
        sensor_data = {}
        for name, filename in self.sensor_files.items():
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
            # 0을 NaN으로 변환
            df = df.replace(0, np.nan)
            sensor_data[name] = df
        return sensor_data

    def load_survey_data(self) -> Dict[str, pd.DataFrame]:
        """모든 설문 데이터 로드"""
        survey_data = {}
        for name, filename in self.survey_files.items():
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
            # 0을 NaN으로 변환
            df = df.replace(0, np.nan)
            survey_data[name] = df
        return survey_data

    def wide_to_long(self, df: pd.DataFrame, value_name: str) -> pd.DataFrame:
        """Wide format을 Long format으로 변환"""
        df_long = df.melt(
            id_vars=['ID'],
            var_name='date',
            value_name=value_name
        )
        df_long['date'] = pd.to_datetime(df_long['date'])
        return df_long

    def prepare_pca_data(
        self,
        target_variable: str = 'anxiety',
        min_data_points: int = 10
    ) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        PCA 분석을 위한 데이터 준비

        Args:
            target_variable: 종속변수 ('anxiety', 'depression', 'stress')
            min_data_points: 최소 데이터 포인트 수

        Returns:
            X: 센서 데이터 (독립변수)
            y: 타겟 변수 (종속변수)
            feature_names: 특징 이름 리스트
        """
        # 센서 데이터와 설문 데이터 로드
        sensor_data = self.load_sensor_data()
        survey_data = self.load_survey_data()

        # 타겟 변수 선택
        if target_variable not in survey_data:
            raise ValueError(f"타겟 변수 '{target_variable}'가 존재하지 않습니다.")

        target_df = survey_data[target_variable]

        # Long format으로 변환
        target_long = self.wide_to_long(target_df, f'{target_variable}_score')

        sensor_long_dict = {}
        for name, df in sensor_data.items():
            sensor_long_dict[name] = self.wide_to_long(df, name)

        # 모든 센서 데이터 병합
        merged_data = target_long.copy()
        for name, df in sensor_long_dict.items():
            merged_data = merged_data.merge(
                df,
                on=['ID', 'date'],
                how='left'
            )

        # 결측치 제거 (타겟 변수가 있는 행만 유지)
        merged_data = merged_data.dropna(subset=[f'{target_variable}_score'])

        # 사용자별로 충분한 데이터가 있는지 확인
        user_counts = merged_data.groupby('ID').size()
        valid_users = user_counts[user_counts >= min_data_points].index
        merged_data = merged_data[merged_data['ID'].isin(valid_users)]

        # 특징과 타겟 분리
        feature_cols = list(sensor_data.keys())
        X = merged_data[feature_cols]
        y = merged_data[f'{target_variable}_score']

        # 다단계 결측치 처리
        # 1단계: 각 컬럼의 평균값으로 채우기
        X = X.fillna(X.mean())

        # 2단계: 여전히 NaN이 있는 경우 (컬럼 전체가 NaN인 경우) 0으로 채우기
        X = X.fillna(0)

        # 3단계: 혹시 모를 inf 값도 0으로 변환
        X = X.replace([np.inf, -np.inf], 0)

        # 4단계: 최종 확인 - NaN이 있는 행 제거 (안전장치)
        if X.isna().any().any():
            print(f"⚠️ 경고: {X.isna().sum().sum()}개의 NaN 값을 발견했습니다. 해당 행을 제거합니다.")
            valid_idx = ~X.isna().any(axis=1)
            X = X[valid_idx]
            y = y[valid_idx]

        return X, y, feature_cols

    def get_dataset_info(self) -> Dict:
        """데이터셋 기본 정보 반환"""
        sensor_data = self.load_sensor_data()
        survey_data = self.load_survey_data()

        # 첫 번째 파일에서 사용자 수와 날짜 수 확인
        first_sensor = list(sensor_data.values())[0]
        n_users = len(first_sensor) - 1  # 헤더 제외
        n_dates = len(first_sensor.columns) - 1  # ID 컬럼 제외

        return {
            'n_users': n_users,
            'n_dates': n_dates,
            'n_sensors': len(sensor_data),
            'n_surveys': len(survey_data),
            'sensor_names': list(sensor_data.keys()),
            'survey_names': list(survey_data.keys()),
        }
