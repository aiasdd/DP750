# 호텔업 파이프라인 — 노트북 기반 파이프라인 (절차적 접근 방식)
# 모듈: 데이터 파이프라인 설계 및 구현
# 단원: 노트북 및 작업(Task) 간 의존성을 활용한 파이프라인 생성
#
# 산업적 배경:
#   StayWell Hotels는 숙소별 예약 취소율을 계산하는 일일 보고서가 필요합니다.
#   취소 사유를 분류하기 위해 사용자 정의 파이썬 함수가 필요한데,
#   이는 선언적(declarative) 방식으로 표현하기 어렵기 때문에
#   해당 처리 단계를 Lakeflow 작업(Job) 내의 노트북 작업(Notebook Task)으로 구현합니다.
#
# 데모 목표:
#   - 절차적(procedural) 노트북 접근 방식(읽기 → 변환 → 쓰기)을 보여줍니다.
#   - 런타임 매개변수를 위한 `dbutils.widgets` 사용법을 시연합니다.
#   - 작업의 성공/실패 여부를 알리기 위해 `dbutils.notebook.exit()`를 사용하는 방법을 보여줍니다.
#   - `dbutils.jobs.taskValues`를 사용하여 작업 간 매개변수를 전달하는 방법을 보여줍니다.
#   - 이 노트북은 Lakeflow 작업 내의 '작업(Task)'으로 실행하기 위한 것이며,
#     단독으로 실행해서는 안 됩니다. 강사는 두 개의 노트북 작업으로 구성된 작업을 생성해야 합니다:
#       작업 1: 본 파일 (ingest_cancellations)
#       작업 2: 출력 테이블을 읽어오는 별도의 노트북
#     또한, 작업 2가 작업 1에 의존하도록 설정해야 합니다.
#
# 참고: 이 파일은 강사 참고용으로 작성된 일반 파이썬 스크립트입니다.
#       데모 진행 시 코드 블록을 복사하여 별도의 워크스페이스 노트북에 붙여넣으세요.

# ── 셀 1: 위젯 / 매개변수 설정 ─────────────────────────────────────────
# 강사: 매개변수를 통해 노트북을 어떻게 유연하고 재사용 가능하게 만들 수 있는지 보여주세요.

dbutils.widgets.text("process_date",  "", "Process Date (YYYY-MM-DD)")
dbutils.widgets.text("property_id",   "ALL", "Property ID (or ALL)")

process_date = dbutils.widgets.get("process_date") or str(spark.sql("SELECT current_date()").collect()[0][0])
property_id  = dbutils.widgets.get("property_id")

print(f"Processing cancellations for: {process_date}, property: {property_id}")


# ── CELL 2: Read from Silver reservations ────────────────────────────────────
# Trainer: in a notebook pipeline we explicitly read → transform → write.

from pyspark.sql import functions as F

reservations = spark.read.table("trainer_demo.demo_10.silver_reservations")

# Filter to cancelled reservations on the process date
cancelled = reservations.filter(
    (F.col("status") == "cancelled") &
    (F.col("check_in_date") == process_date)
)

if property_id != "ALL":
    cancelled = cancelled.filter(F.col("property_id") == property_id)

print(f"Found {cancelled.count()} cancelled reservations")


# ── CELL 3: Custom business logic (reason for cancellation) ──────────────────
# Trainer: this logic is the reason we chose a notebook over Lakeflow Pipelines.
# Complex Python branching is hard to express declaratively.

from pyspark.sql.types import StringType

def classify_cancellation_reason(days_before_checkin):
    """Classify cancellation reason based on lead time."""
    if days_before_checkin is None:
        return "unknown"
    elif days_before_checkin <= 1:
        return "last_minute"
    elif days_before_checkin <= 7:
        return "short_term"
    elif days_before_checkin <= 30:
        return "medium_term"
    else:
        return "long_term"

classify_udf = F.udf(classify_cancellation_reason, StringType())

from datetime import date

enriched = (
    cancelled
    .withColumn(
        "days_before_checkin",
        F.datediff(F.col("check_in_date"), F.lit(date.today()))
    )
    .withColumn("cancellation_reason", classify_udf(F.col("days_before_checkin")))
)


# ── CELL 4: Write output and signal job task result ───────────────────────────
# Trainer: show dbutils.notebook.exit() — downstream tasks can read this value.

try:
    (
        enriched
        .select("reservation_id", "guest_id", "property_id",
                "check_in_date", "total_amount",
                "cancellation_reason", "days_before_checkin")
        .write
        .format("delta")
        .mode("append")
        .partitionBy("check_in_date")
        .saveAsTable("trainer_demo.demo_10.cancellation_analysis")
    )
    records = enriched.count()
    # Pass record count to downstream tasks via task values
    dbutils.jobs.taskValues.set(key="cancellations_processed", value=records)
    dbutils.notebook.exit(f"SUCCESS: Processed {records} cancellation records for {process_date}")

except Exception as e:
    dbutils.notebook.exit(f"FAILED: {str(e)}")
