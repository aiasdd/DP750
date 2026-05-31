# ==============================================================
# ClearCover Insurance — Claims Data Quality Pipeline
# INSTRUCTOR ANSWER KEY
# 한글 번역본
# ==============================================================

from pyspark import pipelines as dp
from pyspark.sql.functions import expr, col, count, sum as spark_sum


# --------------------------------------------------------------
# Exercise 3 + 4: Nullability, Status, and Data Type Validation
# 연습 3 + 4: Null 여부, 상태 및 데이터 유형 검증
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
    '''Silver: validated insurance claims with full quality constraints applied.
    Silver: 전체 품질 제약 조건이 적용된 검증된 보험 청구.'''
    return (
        spark.readStream
        .table('insurance_lab.bronze.claims_raw')
        .withColumn('claim_date',   expr('try_cast(claim_date AS date)'))
        .withColumn('claim_amount', expr('try_cast(claim_amount AS decimal(12,2))'))
    )


# --------------------------------------------------------------
# Exercise 5: Schema Drift — Rescued Data
# 연습 5: 스키마 드리프트 — 구조 변경 데이터
# --------------------------------------------------------------

@dp.table(name='silver.claims_rescued')
def claims_rescued():
    '''Silver: raw claims loaded via Auto Loader with rescue schema evolution.
    Silver: Auto Loader로 로드된 원본 청구(스키마 진화 복구 포함).'''
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
# Gold: Claims Summary
# 금색: 청구 요약
# --------------------------------------------------------------

@dp.table(name='gold.claims_summary')
def claims_summary():
    '''Gold: aggregate claim counts and total amounts per type and status.
    Gold: 유형 및 상태별 청구 수 및 총액 집계.'''
    return (
        spark.read.table('insurance_lab.silver.claims_validated')
        .groupBy('claim_type', 'status')
        .agg(
            count('claim_id').alias('claim_count'),
            spark_sum('claim_amount').alias('total_claim_amount')
        )
    )
