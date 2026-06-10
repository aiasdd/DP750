---
lab:
  index: 03
  title: Unity Catalog에서 개체 생성 및 구성
---

---
|구분|내용|
|---|---|
|설명| 이 랩에서는 대학 데이터 플랫폼을 위한 완전한 Unity Catalog 네임스페이스를 구축합니다. 카탈로그, 메달리온 스키마, 기본 키 및 외래 키 제약 조건이 있는 관리 테이블, 뷰, 볼륨 및 재사용 가능한 SQL 함수를 생성합니다. 열 추가 및 거버넌스 태그 적용과 같은 DDL 작업을 연습하고, Unity Catalog가 메달리온 아키텍처의 모든 계층에서 구조화된 데이터를 어떻게 구성하고 관리하는지 살펴봅니다. 마지막에는 Azure Databricks의 실제 데이터 엔지니어링 관행을 반영하는 완전히 구조화되고 쿼리 준비가 된 환경을 갖게 됩니다.|
|소요시간| 60분|
|난이도| 300|
---

# 랩 03: Unity Catalog에서 개체 생성 및 구성

## 시나리오

귀사는 **Lakeside University**의 데이터 엔지니어입니다. Lakeside University는 학사 운영을 디지털화하는 중순 규모 교육 기관입니다. 귀사의 팀은 학생 기록, 과정 목록 및 등록 데이터를 관리하기 위해 Azure Databricks에서 최신 데이터 플랫폼을 구축하는 작업을 맡았습니다.

이 랩에서는 Lakeside University 개발 환경을 위한 완전한 Unity Catalog 네임스페이스를 설계하고 구현합니다. 조직 명명 규칙을 따르는 카탈로그, 스키마, 제약 조건이 있는 테이블, 뷰, 볼륨 및 재사용 가능한 SQL 함수를 생성합니다.

## 목표

이 랩을 완료하면 다음을 수행할 수 있습니다:

- Unity Catalog 명명 규칙에 따라 카탈로그 및 메달리온 스키마를 생성합니다.
- 기본 키 및 외래 키 제약 조건이 있는 관리 테이블을 생성합니다.
- 표준 뷰 및 구체화된 뷰를 구축하여 분석 쿼리를 처리합니다.
- 관리 볼륨을 생성하고 CSV 파일을 이 볼륨에 로드합니다.
- 성적 분류를 위한 재사용 가능한 SQL 스칼라 함수를 작성합니다.
- **ALTER** 문을 사용하여 테이블을 확장하고 거버넌스 태그를 적용합니다.

이 랩은 완료하는 데 약 **60분**이 소요됩니다.

---

## 🤖 이 랩 전체에서 Genie Code를 사용합니다

이 랩 중에는 항상 **Genie Code**를 사용할 것을 권장습니다. 모든 연습에는 Genie Code 패널에 직접 붙여넣을 수 있는 제안 프롬프트가 포함되어 있습니다.

Genie Code를 열려면 모든 노트북 셀 오른쪽에 있는 ![assistant-icon](https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/media/genie-code.svg)을 선택하거나 키보드 단축키를 사용합니다.

> 💡 **팁:** Genie Code의 출력을 무조건 복사하여 붙여넣지 마세요. 읽고 이해한 다음 각 작업의 특정 요구 사항에 맞게 조정하세요. Genie Code는 사고를 대체하지 않고 가속화하는 도구입니다.

---

## 필수 조건

이 랩을 시작하기 전에 다음을 확인하세요:

- [랩 00: Azure Databricks 환경 설정](00-setup.md)을 사용하여 프로비저닝된 **Azure Databricks Premium 작업 영역**이 있습니다.
- 작업 영역에 연결된 활성 **Unity Catalog 메타스토어**가 있습니다.
- 메타스토어에 **CREATE CATALOG** 권한이 있습니다(강사 또는 작업 영역 관리자가 부여함).
- 기본 SQL에 익숙합니다(CREATE TABLE, SELECT, JOIN).

---

## 랩 노트북 가져오기

1. Databricks 작업 영역에서 왼쪽 사이드바의 **작업 영역**을 선택합니다.
2. 랩 노트북을 저장할 폴더로 이동하거나 생성합니다(예: 홈 폴더).
3. **⋮**(kebab) 메뉴를 선택하거나 폴더를 마우스 오른쪽 단추로 클릭한 다음 **가져오기**를 선택합니다.
4. **URL**을 선택하고 다음 URL을 입력한 다음 **가져오기**를 선택합니다:

```
https://github.com/asddai/AzureDatabricks/blob/main/Labs/Notebooks/03-create-and-organize-objects-in-unity-catalog-KO.ipynb
```

5. 가져온 노트북을 엽니다. 노트북 위쪽의 컴퓨팅 선택기에서 **서버리스** 컴퓨팅을 선택합니다.

---

## 노트북 작업

가져온 노트북을 열고 각 셀의 지침을 따라 연습 1~6을 완료합니다. 노트북 끝의 **다음 단계** 셀에 도달하면 여기로 돌아와서 아래의 연습을 계속하세요.

---

## 연습: AI/BI Genie Space 구성(선택 사항)

이 선택적 작업에는 Genie Space가 필요하며, 이는 노트북이 아닌 Databricks UI를 통해 완전히 구성됩니다.

노트북 연습을 완료한 후 Genie Space를 선택적으로 생성하여 Lakeside University 데이터에 대한 자연어 쿼리를 경험할 수 있습니다.

1. 왼쪽 사이드바에서 **+ 새로 만들기** > **Genie space**를 선택합니다.
2. **데이터** 아래에 다음 테이블을 추가합니다:
   - `edu_dev.silver.students`
   - `edu_dev.silver.courses`
   - `edu_dev.silver.enrollments`
   - `edu_dev.silver.vw_student_enrollments`
   - `edu_dev.gold.vw_department_enrollment_stats`
3. 스페이스 이름을 `Lakeside University Analytics`로 지정합니다.
4. `enrollments.grade` 열의 경우 설명을 다음과 같이 업데이트합니다: `0.0~10.0 척도의 수치 등급이며, 8.5 이상은 A, 7.0 이상은 B, 5.5 이상은 C, 4.0 이상은 D, 4.0 미만은 F입니다.`
5. **채팅** 탭으로 이동하여 다음을 질문합니다: *"어느 학과가 가장 높은 평균 성적을 가지고 있나요?"*
6. Genie가 생성한 SQL을 검토하고 **vw_department_enrollment_stats** 구체화된 뷰와 비교합니다.

> 🤖 **Genie Code 팁:** Genie space 내에서 Genie Code를 요청하여 SQL 지침을 작성하거나 열 동의어를 정의하는 데 도움을 받을 수 있습니다.

---

## 정리(선택 사항)

이 랩에서 생성한 리소스를 제거하려면 노트북에서 다음을 실행합니다:

```sql
DROP CATALOG IF EXISTS edu_dev CASCADE;
```

> ⚠️ 이렇게 하면 edu_dev에서 생성된 모든 스키마, 테이블, 뷰, 볼륨 및 함수가 영구적으로 삭제됩니다. 이러한 개체가 더 이상 필요하지 않다고 확실한 경우에만 실행하세요.
