# ==============================================================
# ClearCover Insurance — 클레임 데이터 품질 파이프라인
# Lakeflow Spark Declarative Pipelines
# ==============================================================
#
# 아래 연습 문제를 완료하여 모든 계층에서 데이터 품질 제약을
# 적용하는 파이프라인을 구축하세요.
# ==============================================================

from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, sum as spark_sum


# --------------------------------------------------------------
# 연습 3: Null 허용 여부 및 상태 검증
#
# 아래 claims_validated() 함수에 다음을 수행하도록 expectation을 추가하세요:
#
#   3a) claim_id IS NULL 인 레코드를 DROP
#   3b) customer_id IS NULL 인 레코드를 DROP
#   3c) status 가 ('OPEN', 'PENDING', 'CLOSED') 에 포함되지 않은
#       레코드를 WARN (유지)
#   3d) coverage_amount <= 0 인 레코드가 있으면 파이프라인을 FAIL
#
# 다음 데코레이터를 사용하세요:
#   @dp.expect_or_drop(name, condition)   — 위반 행을 드롭함
#   @dp.expect(name, condition)           — 경고하며 모든 행을 유지함
#   @dp.expect_or_fail(name, condition)   — 파이프라인을 실패시킴
#
# 🤖 Genie Code에게 질문하기:
#   "Show me how to add expect_or_drop, expect, and expect_or_fail
#    decorators to a Lakeflow Spark Declarative Pipelines Python
#    function to enforce nullability and status constraints"
# --------------------------------------------------------------

@dp.table(name='silver.claims_validated')
# TODO 연습 3: 위의 지침에 설명된 대로 여기에 @dp.expect_or_drop 및 기타 expectation 데코레이터를 추가하세요.
def claims_validated():
    '''Silver: 품질 제약이 적용된 검증된 보험 클레임.'''

    # TODO 연습 4: return 앞에 col().cast() 를 사용하는 withColumn 호출을 여기에 추가하세요.
    # 이 함수를 수정하기 전에 아래 연습 4 지침을 참고하세요.

    return spark.readStream.table('insurance_lab.bronze.claims_raw')


# --------------------------------------------------------------
# 연습 5: 스키마 드리프트 — Rescued 데이터
#
# readStream을 다음과 같이 구성하세요:
#   - /Volumes/insurance_lab/bronze/raw_files/ 에서 읽기
#   - cloudFiles.format = csv 로 cloudFiles 형식 사용
#   - cloudFiles.schemaLocation 을 볼륨 내부 경로로 설정:
#       /Volumes/insurance_lab/bronze/raw_files/_schema
#   - cloudFiles.schemaEvolutionMode 을 'rescue' 로 설정
#   - rescuedDataColumn 을 '_rescued_data' 로 설정
#   - cloudFiles.inferColumnTypes 을 'true' 로 설정
#   - header 를 'true' 로 설정
#
# 소스 파일이 예상 스키마와 일치하면 _rescued_data 는 NULL이
# 됩니다. 예상치 못한 새 컬럼은 파이프라인을 중단시키는 대신
# 해당 컬럼에 JSON으로 캡처됩니다.
#
# 🤖 Genie Code에게 질문하기:
#   "Write a PySpark Auto Loader readStream using cloudFiles format
#    csv with schemaEvolutionMode rescue and a _rescued_data column
#    to capture unexpected new columns from schema drift"
# --------------------------------------------------------------

@dp.table(name='silver.claims_rescued')
def claims_rescued():
    '''Silver: rescue 스키마 진화와 함께 Auto Loader를 통해 로드된 원시 클레임.'''
    # TODO 연습 5: 아래 pass 문을 위의 지침에 설명된 대로 Auto Loader
    # readStream 구현으로 교체하세요.
    pass


# --------------------------------------------------------------
# Gold: 클레임 요약 — 제공됨, 변경 불필요
#
# 이 테이블은 검증된 silver 클레임을 클레임 유형과 상태별로
# 집계하여 보고 대시보드용 요약을 생성합니다.
# --------------------------------------------------------------

@dp.table(name='gold.claims_summary')
@dp.table(name='gold.claims_summary')
def claims_summary():
    '''Gold: 유형 및 상태별 클레임 건수와 총액을 집계합니다.'''
    return (
        spark.read.table('insurance_lab.silver.claims_validated')
        .groupBy('claim_type', 'status')
        .agg(
            count('claim_id').alias('claim_count'),
            spark_sum('claim_amount').alias('total_claim_amount')
        )
    )