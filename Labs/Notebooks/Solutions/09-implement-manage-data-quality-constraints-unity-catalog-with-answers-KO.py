# ==============================================================
# ClearCover Insurance — 클레임 데이터 품질 파이프라인
# 강사용 정답 키
# ==============================================================

from pyspark import pipelines as dp
from pyspark.sql.functions import expr, col, count, sum as spark_sum


# --------------------------------------------------------------
# 연습 3 + 4: Null 허용 여부, 상태, 데이터 타입 검증
# --------------------------------------------------------------

@dp.table(name='silver.claims_validated')
@dp.expect_or_drop('valid_claim_id',      'claim_id IS NOT NULL')
@dp.expect_or_drop('valid_customer_id',   'customer_id IS NOT NULL')
@dp.expect(        'valid_status',        "status IN ('OPEN', 'PENDING', 'CLOSED')")
@dp.expect_or_fail('valid_coverage',      'coverage_amount > 0')
@dp.expect_or_drop('valid_claim_date',    'claim_date IS NOT NULL')
@dp.expect_or_drop('valid_claim_amount',  'claim_amount IS NOT NULL')
@dp.expect_or_drop('non_negative_amount', 'claim_amount >= 0')
def claims_validated():
    '''Silver: 전체 품질 제약 조건이 적용된 검증된 보험 클레임.'''
    return (
        spark.readStream
        .table('insurance_lab.bronze.claims_raw')
        .withColumn('claim_date',   expr('try_cast(claim_date AS date)'))
        .withColumn('claim_amount', expr('try_cast(claim_amount AS decimal(12,2))'))
    )


# --------------------------------------------------------------
# 연습 5: 스키마 드리프트 — 복구된 데이터
# --------------------------------------------------------------

@dp.table(name='silver.claims_rescued')
def claims_rescued():
    '''Silver: rescue 스키마 진화를 사용하여 Auto Loader로 로드된 원시 클레임.'''
    return (
        spark.readStream
        .format('cloudFiles')
        .option('cloudFiles.format',              'csv')
        .option('header',                          'true')
        .option('cloudFiles.schemaLocation',      '/Volumes/insurance_lab/bronze/raw_files/_schema')
        .option('cloudFiles.schemaEvolutionMode', 'rescue')
        .option('rescuedDataColumn',              '_rescued_data')
        .option('cloudFiles.inferColumnTypes',    'true')
        .load('/Volumes/insurance_lab/bronze/raw_files/')
    )


# --------------------------------------------------------------
# Gold: 클레임 요약
# --------------------------------------------------------------

@dp.table(name='gold.claims_summary')
def claims_summary():
    '''Gold: 유형 및 상태별 클레임 건수와 총 금액 집계.'''
    return (
        spark.read.table('insurance_lab.silver.claims_validated')
        .groupBy('claim_type', 'status')
        .agg(
            count('claim_id').alias('claim_count'),
            spark_sum('claim_amount').alias('total_claim_amount')
        )
    )
