---
lab:
  index: 09
  title: Unity Catalog에서 데이터 품질 제약 조건 구현 및 관리
  module: Unity Catalog에서 데이터 품질 제약 조건 구현 및 관리
  module-url: https://learn.microsoft.com/training/wwl-databricks/implement-manage-data-quality-constraints-unity-catalog/
  notebook: https://github.com/aiasdd/DP750/blob/main/Labs/Notebooks/Allfiles/09-implement-manage-data-quality-constraints-unity-catalog-KO.ipynb
  description: 이 랩에서는 원본 청구 데이터에 대한 데이터 품질 제약 조건을 시행하는 ClearCover Insurance에 대한 Lakeflow Spark 선언형 파이프라인을 구축합니다. 파이프라인 예상을 사용하여 널 가능성 및 범위 검사를 구현하고, col().cast()를 사용하여 데이터 유형을 검증하며, Auto Loader의 구조 도움말 열을 사용하여 스키마 드리프트를 처리합니다. 그런 다음 Databricks UI에서 파이프라인을 생성하고 실행하며 데이터 품질 메트릭을 모니터링합니다.
  duration: 50분
  level: 300
  islab: true
  primarytopics:
    - Azure Databricks
---

---
|구분|내용|
|---|---|
|설명|이 랩에서는 원본 청구 데이터에 대한 데이터 품질 제약 조건을 시행하는 ClearCover Insurance에 대한 Lakeflow Spark 선언형 파이프라인을 구축합니다. 파이프라인 예상을 사용하여 널 가능성 및 범위 검사를 구현하고, col().cast()를 사용하여 데이터 유형을 검증하며, Auto Loader의 구조 도움말 열을 사용하여 스키마 드리프트를 처리합니다. 그런 다음 Databricks UI에서 파이프라인을 생성하고 실행하며 데이터 품질 메트릭을 모니터링합니다.|
|소요시간| 50분|
|난이도| 300|
---

# 랩 09: Unity Catalog에서 데이터 품질 제약 조건 구현 및 관리

## 소개

여러분은 가상의 보험사인 **ClearCover Insurance** 의 데이터 엔지니어입니다. 매일 지역 지사와 파트너 중개인으로부터 원시 보험 청구(claims) 데이터가 유입됩니다. 안타깝게도 이 데이터는 일관성이 부족합니다. 일부 레코드에는 필수 식별자가 누락되어 있고, 청구 금액이 문자열 형식으로 되어 있거나 음수 값을 포함하며, 날짜 형식이 잘못된 경우도 있습니다. 또한 시간이 지남에 따라 원본 스키마에 새로운 열이 예고 없이 추가되기도 합니다.

여러분의 임무는 파이프라인의 모든 단계에서 데이터 품질 제약 조건을 적용하는 **Lakeflow Spark 선언형 파이프라인(Declarative Pipeline)** 을 구축하는 것입니다. 이를 통해 보험 계리 모델이나 보고용 대시보드에 도달하기 전에 품질이 낮은 레코드를 사전에 차단해야 합니다.

다음과 같은 실습 과정을 진행하게 됩니다:

| 실습   | 주제                                                    |
| ---------- | -------------------------------------------------------- |
| 실습 1 | ClearCover Insurance 데이터 플랫폼 설정(노트북) |
| 실습 2 | Catalog Explorer에서 데이터 품질 문제 탐색        |
| 실습 3 | Null 허용 여부 및 상태 유효성 검사 구현            |
| 실습 4 | col().cast()를 사용하여 데이터 유형 검사 추가                  |
| 실습 5 | Rescued Data(구조에 맞지 않는 데이터)를 활용한 스키마 변경(schema drift) 처리                   |
| 실습 6 | 파이프라인 실행 및 모니터링                             |

---

## 🤖 Genie Code — 항상 사용하세요

이 랩의 모든 실습 전체에서 **Genie Code를 사용할 것을 강력히 권장합니다**. 모든 실습에는 시작할 제안 프롬프트가 포함되어 있습니다. Genie Code는 귀사의 페어 프로그래머입니다 — 코드를 생성하고, 오류를 이해하고, 대안을 탐색하는 데 사용하세요.

Genie Code를 열려면 모든 노트북 셀 오른쪽에 있는 ![assistant-icon](https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/media/genie-code.svg)을 선택하거나 키보드 단축키를 사용합니다.
---

## 필수 조건

- [랩 00: Azure Databricks 환경 설정](00-setup.md)을 사용하여 프로비저닝된 **Azure Databricks Premium 워크스페이스**이 있습니다.
- 기본 Python 및 PySpark 개념에 익숙합니다.
- 이 학습 경로의 이전 랩을 완료했습니다(또는 Unity Catalog 기본 사항이 편하다).

---

## 설정 노트북 가져오기

1. Databricks 워크스페이스에서 왼쪽 사이드바의 **워크스페이스** 을 클릭합니다.
2. 랩을 저장할 폴더로 이동하거나 생성합니다.
3. **⋮**(kebab) 메뉴를 클릭하거나 폴더를 마우스 오른쪽 단추로 클릭한 다음 **가져오기** 를 선택합니다.
4. **URL** 을 선택하고 다음 URL을 입력한 다음 **가져오기** 를 클릭합니다:

```
https://github.com/aiasdd/DP750/blob/main/Labs/Notebooks/09-implement-manage-data-quality-constraints-unity-catalog-KO.ipynb
```
5. 가져온 노트북을 열고 위쪽의 컴퓨팅 선택기에서 **서버리스** 컴퓨팅을 선택합니다.

---

## 실습 1: ClearCover Insurance 데이터 플랫폼 설정

설정 노트북 **09-implement-manage-data-quality-constraints-unity-catalog**의 모든 셀을 위에서 아래로 실행합니다.

노트북은 다음 개체를 생성합니다:

| 개체                                | 설명                                                  |
| ------------------------------------- | ------------------------------------------------------------ |
| insurance_lab 카탈로그	| ClearCover 보험 플랫폼을 위한 최상위 네임스페이스
| insurance_lab.bronze 스키마	| 소스 시스템에서 수신된 가공되지 않은 원본 보험금 청구 데이터
| insurance_lab.silver 스키마	| 검증 및 데이터 유형이 안전하게 처리된 레코드
| insurance_lab.gold 스키마	| 집계된 보고용 데이터
| insurance_lab.bronze.raw_files 볼륨	| 원본 CSV 보험금 청구 파일을 위한 랜딩 존(landing zone)
| insurance_lab.bronze.claims_raw 테이블	| 20개의 원본 보험금 청구 레코드를 포함하는 Delta 테이블

노트북 실행이 완료되면 다음 단계로 넘어가기 전에 Catalog Explorer에서 해당 객체들이 생성되었는지 확인합니다.


---

## 실습 2: 데이터 품질 문제 탐색

파이프라인 코드를 작성하기 전에 원본 데이터를 탐색하여 해결해야 할 품질 문제를 파악합니다.

### 작업 2.1: 원본 청구 테이블 쿼리

새 SQL 쿼리 편집기(또는 노트북 셀)를 열고 다음을 실행합니다:

```sql
SELECT *
FROM insurance_lab.bronze.claims_raw
ORDER BY claim_id NULLS LAST;
```

결과를 검토하고 다음의 각 각 문제에 대해 최소 한 행을 찾습니다:

| 문제                      | 확인할 컬럼                    |
| -------------------------- | -------------------------------------- |
| 누락된 기본 식별자 | claim_id 또는 customer_id가 NULL임      |
| 구문 분석할 수 없는 날짜           | claim_date에 날짜 형식이 아닌 문자열이 포함됨 |
| 구문 분석할 수 없는 금액         | claim_amount에 N/A 또는 공백 포함  |
| 음수 금액            | claim_amount가 음수임  |
| 유효하지 않은 상태             | status가 OPEN, PENDING, CLOSED 중 하나가 아님 |

![alt text](image-8.png)

### 작업 2.2: 스키마 검사

다음 명령을 실행하여 claim_date와 claim_amount가 STRING(문자열)으로 저장되어 있는지 확인합니다:

```sql
DESCRIBE TABLE insurance_lab.bronze.claims_raw;
```
![alt text](image-9.png)
이 컬럼들은 bronze 계층에서 의도적으로 문자열(string)로 설정되어 있습니다. 이후 파이프라인 실습 과정에서 silver 계층으로 데이터를 수집(ingestion)할 때 올바른 데이터 유형이 적용되도록 처리할 것입니다.

---

## 실습 3: Null 허용 여부 및 상태 유효성 검사

### 작업 3.0: ETL 파이프라인 생성 및 파이프라인 파일 가져오기

파이프라인 코드를 작성하기 전에 시작 파이프라인 파일을 가져오고 Databricks에서 Lakeflow Spark 선언형 파이프라인을 생성합니다.

**파이프라인 파일 가져오기:**

1. Databricks 워크스페이스에서 왼쪽 사이드바의 **워크스페이스** 을 클릭합니다.
2. 랩 노트북을 저장한 폴더로 이동합니다.
3. **⋮**(kebab) 메뉴를 클릭하거나 폴더를 마우스 오른쪽 단추로 클릭한 다음 **가져오기** 를 선택합니다.
4. **URL** 을 선택하고 다음 URL을 입력한 다음 **가져오기** 를 클릭합니다:
   `https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/09-implement-manage-data-quality-constraints-unity-catalog.py`
5. 파일은 워크스페이스에 Python 소스 파일로 표시됩니다 — 다음 단계를 위해 경로를 기록합니다.

**파이프라인 생성:**

1. Databricks 워크스페이스 왼쪽 사이드바에서 **작업 및 파이프라인** 을 클릭합니다.
2. **ETL 파이프라인 생성** 을 클릭합니다.
3. 다음 설정으로 파이프라인을 구성합니다:

   | 설정        | 값                                                                                              |
   | -------------- | -------------------------------------------------------------------------------------------------- |
   | 파이프라인 이름  | **ClearCover Claims Quality Pipeline**                                                             |
   | 파이프라인 모드  | **트리거됨**                                                                                      |
   | 대상 카탈로그 | **insurance_lab**, 스키마 **silver**                                                               |
   | 컴퓨팅        | **서버리스**                                                                                     |

파이프라인 편집기에서 왼쪽 창(에셋 브라우저)을 찾습니다. 메뉴를 열고 **가져오기**를 선택한 다음, 가져온 `09-implement-manage-data-quality-constraints.py` 파일을 찾아 파이프라인 소스 코드로 추가합니다.
가져온 파이프라인 파일을 열고 실습 3~5를 진행하는 동안 계속 열어 둡니다. 이제 데이터 품질 제약 조건을 추가하기 위해 이 파일을 편집하게 됩니다.

### 작업 3.1: `claims_validated()`에 Null 허용 여부 및 상태 관련 기대치(expectation) 추가

09-implement-manage-data-quality-constraints-unity-catalog.py를 열고 다음 예상을 *claims_validated()* 함수에 추가합니다. 모든 데코레이터를 `@dp.table(...)` 및 `def claims_validated():`사이에 배치합니다.

| 기대치 이름  | 조건                                 | 동작        |
| ----------------- | ----------------------------------------- | ------------- |
| valid_claim_id    | `claim_id IS NOT NULL`                    | Drop (삭제)          |
| valid_customer_id | `customer_id IS NOT NULL`                 | Drop (삭제)     |
| valid_status      | `status IN ('OPEN', 'PENDING', 'CLOSED')` | Warn (경고/유지)   |
| valid_coverage    | `coverage_amount > 0`                     | Fail pipeline (파이프라인 실패) |

조건을 위반하는 행을 삭제하려면 `@dp.expect_or_drop`을, 삭제하지 않고 경고만 하려면 `@dp.expect`를, 위반 시 파이프라인을 중단하려면 `@dp.expect_or_fail`을 사용합니다.

> 🤖 **Genie Code에 요청:**
> *"Lakeflow Spark 선언형 파이프라인 Python 함수에서 expect_or_drop, expect 및 expect_or_fail 데코레이터를 사용하는 방법을 보여주세요"*

---

## 실습 4: 데이터 유형 확인

`claim_date`와 `claim_amount` 열은 문자열(string) 형태로 들어옵니다. `col().cast()`는 값을 파싱할 수 없을 때 오류를 발생시키는 대신 `NULL`을 반환합니다. 이 동작을 활용하여 유효하지 않은 레코드를 식별하고 삭제할 수 있습니다.

### 작업 4.1: claims_validated() 내에서 col().cast() 적용

claims_validated() 함수 본문(**return 문 이전**)에서 두 개의 withColumn 호출을 추가합니다:

1. `col('claim_date').cast('date')`를 사용하여 claim_date를 STRING에서 DATE로 변환합니다.
2. `col('claim_amount').cast('decimal(12,2)')`를 사용하여 claim_amount를 STRING에서 DECIMAL(12,2)로 변환합니다.

변환된 열은 원본을 대체하므로 다운스트림 예상 및 소비자는 유형이 지정된 값을 봅니다.

> 🤖 **Genie Code에 요청:**
> *"PySpark에서 withColumn 및 col().cast()를 사용하여 스트리밍 데이터프레임 열을 STRING에서 DATE 유형으로 변환하고 다른 열을 STRING에서 DECIMAL(12,2)로 변환합니다. 전체 withColumn 구문을 보여주세요."*

### 작업 4.2: 파싱할 수 없는 날짜가 포함된 레코드 삭제

Task 4.1에서 형 변환(cast)을 수행한 후에도 `claim_date`가 여전히 NULL인 행은 원래 값이 유효하지 않았음을 의미합니다. `@dp.expect_or_drop` 데코레이터를 추가하여 이러한 행을 삭제합니다:

```
기대치 이름: valid_claim_date
조건:        claim_date IS NOT NULL
```

### 작업 4.3: 구문 분석할 수 없거나 누락된 금액이 있는 기록 삭제

마찬가지로 claim_amount를 캐스트할 수 없는 행을 삭제합니다:

```
기대치 이름: valid_claim_amount
조건:        claim_amount IS NOT NULL
```

### 작업 4.4: 음수 청구 금액이 있는 기록 삭제

음수 청구 금액은 모든 보험 상황에서 유효하지 않습니다. 이러한 행을 삭제합니다:

```
기대치 이름: non_negative_amount
조건:        claim_amount >= 0
```

> 💡 **힌트:** 모든 예상 데코레이터를 @dp.table(...) 및 def claims_validated():.사이에 배치합니다. 순서는 결과에 영향을 주지 않습니다 — 모든 예상이 각 행에서 평가됩니다.

> 🤖 **Genie Code에 요청:**
> *"Lakeflow Spark 선언형 파이프라인을 Python으로 사용하고 있습니다. col().cast()를 적용하여 열을 STRING에서 DATE로 변환한 후 캐스트가 실패한 행을 삭제하려면 어느 예상 조건을 사용합니까?"*

---

## 실습 5: Rescued Data(구조 외 데이터)를 활용한 스키마 드리프트(Schema Drift) 처리

ClearCover는 여러 파트너 중개업체로부터 보험 청구 파일을 수신합니다. 간혹 중개업체가 사전 통보 없이 `broker_reference`나 `fraud_score`와 같은 추가 열을 포함하는 경우가 있습니다. 이런 상황에서 파이프라인이 중단되게 하는 대신, 예상치 못한 데이터를 별도의 열에 저장하여 추후 분석할 수 있도록 설정하고자 합니다.

### 작업 5.1: Rescue 스키마 진화 모드(rescue schema evolution mode)를 적용한 Auto Loader 구현

`09-implement-manage-data-quality-constraints.py` 파일 내의 `claims_rescued()` 함수를 완성합니다.

Auto Loader(`cloudFiles` 형식)와 `spark.readStream`을 사용하여 다음 경로의 CSV 파일을 읽습니다:

```
/Volumes/insurance_lab/bronze/raw_files/
```

다음 옵션으로 구성합니다:

| 옵션                         | 값                                           |
| ------------------------------ | ----------------------------------------------- |
| cloudFiles.format              | csv                                             |
| header                         | true                                            |
| cloudFiles.schemaLocation      | /Volumes/insurance_lab/bronze/raw_files/_schema |
| cloudFiles.schemaEvolutionMode | rescue                                          |
| rescuedDataColumn              | _rescued_data                                   |
| cloudFiles.inferColumnTypes    | true                                            |

**pass** 문을 제거하고 구성된 readStream을 반환합니다.

> 🤖 **Genie Code에 요청:**
> *"`cloudFiles` 형식의 CSV, `schemaEvolutionMode`를 `rescue`로 설정하고 `_rescued_data` 열을 포함하는 PySpark Auto Loader `readStream` 블록 전체를 작성합니다. 그리고 각 옵션이 어떤 역할을 하는지 설명하세요."*

> 💡 **힌트:** 소스 파일이 예상된 스키마와 일치할 경우, 모든 행에서 `_rescued_data` 값은 `NULL`이 됩니다. 향후 파일에 새로운 열(예: `fraud_score`)이 추가되더라도 파이프라인이 중단되지 않고, 해당 값들은 `_rescued_data` 열에 JSON 형태로 저장됩니다.

---

## 실습 6: 파이프라인 실행 및 모니터링

파이프라인 코드가 완료되었으므로 실습 3에서 생성한 파이프라인을 실행합니다.

### 작업 6.1: 파이프라인 파일 저장

계속하기 전에 워크스페이스 편집기에서 09-implement-manage-data-quality-constraints-unity-catalog.py에 대한 모든 변경 사항을 저장했는지 확인합니다.

### 작업 6.2: 파이프라인 실행

**시작** 을 클릭하여 전체 파이프라인 실행을 트리거합니다. 실행이 완료될 때까지 기다립니다.

그래프 보기에서 파이프라인 DAG를 관찰합니다. 세 개의 데이터셋 노드가 표시되어야 합니다:
- silver.claims_validated
- silver.claims_rescued
- gold.claims_summary

### 작업 6.3: 데이터 품질 메트릭 모니터링

1. 파이프라인 그래프에서 **claims_validated** 데이터셋 노드를 클릭합니다.
2. 오른쪽 패널에서 **데이터 품질** 탭을 엽니다.
3. 예상 결과를 검토하고 다음 질문에 답변합니다:
   - 어떤 기대치 검사에서 레코드가 **삭제(drop)** 되었으며, 그 개수는 몇 개입니까?
   - 어떤 기대치 검사에서 **경고(warning)** 가 발생했습니까(레코드는 유지되지만 위반 사항이 기록됨)?
   - `valid_coverage`에서 **실패(fail)** 가 발생했습니까? 실패했다면 이는 소스 데이터에 `coverage_amount <= 0`인 행이 있음을 의미합니다. 어떤 행이 원인인지 조사해 보십시오.

> 💡 **힌트:** `valid_coverage`로 인해 파이프라인이 실패했다면, `insurance_lab.bronze.claims_raw` 테이블에서 `coverage_amount`가 0이거나 NULL인 행을 확인하십시오. 파이프라인 이벤트 로그의 오류 메시지에서도 위반된 레코드를 확인할 수 있습니다.

### 작업 6.4: 출력 테이블 쿼리

다음 쿼리를 실행하여 파이프라인 출력을 확인합니다:

```sql
-- 모든 검증을 통과한 청구 건수는 몇 개입니까?
SELECT COUNT(*) AS valid_claim_count
FROM insurance_lab.silver.claims_validated;

-- 검증이 완료된 Silver 레이어에는 어떤 유형(type)과 상태(status)가 포함되어 있나요?
SELECT claim_type, status, COUNT(*) AS count
FROM insurance_lab.silver.claims_validated
GROUP BY claim_type, status
ORDER BY claim_type, status;

-- Gold 요약 데이터 확인
SELECT *
FROM insurance_lab.gold.claims_summary
ORDER BY claim_type, status;

-- Auto Loader가 수집한 'rescued data'(복구된 데이터)가 있나요?
SELECT claim_id, _rescued_data
FROM insurance_lab.silver.claims_rescued
WHERE _rescued_data IS NOT NULL;
```

> 🤖 **Genie Code에 요청:**
> *"insurance_lab.bronze.claims_raw와 insurance_lab.silver.claims_validated의 데이터 건수를 비교했을 때, 각 단계에서 데이터가 감소한 사실이 Bronze 데이터의 품질 문제에 대해 어떤 점을 시사하는지 설명해 주세요.”*

---

## 정리(선택 사항)

작업이 완료되면 모든 랩 리소스를 제거하려면:

```sql
DROP CATALOG IF EXISTS insurance_lab CASCADE;
```
