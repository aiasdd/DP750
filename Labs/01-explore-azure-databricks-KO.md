---
lab:
  index: 01
  title: Azure Databricks 살펴보기
  module: Azure Databricks 살펴보기
  module-url: https://learn.microsoft.com/training/modules/explore-azure-databricks/
  notebook: https://github.com/asddai/AzureDatabricks/blob/main/Labs/Notebooks/01-explore-azure-databricks-KO.ipynb
---
---
|구분|내용|
|---|---|
|설명| 이 랩에서는 Azure Databricks 워크스페이스 UI를 살펴보고, Unity Catalog 볼륨에 샘플 데이터셋을 업로드하며, Python, SQL 매직 명령 및 Markdown을 포함한 노트북 기능을 사용해봅니다. CityMoves Transit이라는 가상의 대중교통 기관의 맥락에서 Genie Code를 사용하여 코드를 생성하고 개선합니다.|
|소요시간| 40분|
|난이도| 200|
---

# 랩 01: Azure Databricks 살펴보기

이 랩에서는 지역 대중교통 기관인 **CityMoves Transit**의 맥락에서 Azure Databricks를 처음 시작합니다. CityMoves Transit은 대도시 지역의 버스, 트램 및 기차 서비스를 관리합니다. 새로 입사한 데이터 엔지니어로서, 이후 랩에서 데이터 파이프라인 및 분석을 시작하기 전에 Azure Databricks 워크스페이스에 익숙해지는 것이 목표입니다.

이 랩을 완료하면 다음을 수행할 수 있습니다:

- Azure Databricks 워크스페이스 UI의 주요 영역을 탐색합니다.
- 데이터 수집 인터페이스를 사용하여 샘플 데이터셋을 업로드합니다.
- Python 코드 셀, SQL 매직 명령 및 Markdown 문서를 포함한 노트북 기능을 살펴봅니다.

이 랩은 완료하는 데 약 **40분**이 소요됩니다.

---

## 필수 조건

이 랩을 시작하기 전에 다음을 확인하세요:

- [랩 00: Azure Databricks 환경 설정](00-setup.md)을 사용하여 프로비저닝된 **Azure Databricks Premium 워크스페이스**이 있습니다.
- 기본 Azure Portal 탐색에 익숙합니다.
- 이전 Databricks 경험이 필요하지 않습니다.

---

## 연습 1: Azure Databricks 워크스페이스 UI 탐색

코드를 작성하기 전에 Azure Databricks 환경을 살펴보겠습니다. UI에 익숙해지면 이 과정 전반에서 더 효율적으로 작업할 수 있습니다.

### 작업 1: 워크스페이스 사이드바 살펴보기

1. Azure Databricks 워크스페이스에서 **왼쪽 사이드바**를 살펴봅니다. 다음 섹션을 식별합니다:
   - **워크스페이스** — 노트북 및 파일용 개인 및 공유 폴더입니다.
   - **최근 항목** — 최근에 열었던 개체입니다.
   - **카탈로그** — Unity Catalog 데이터 자산(테이블, 볼륨, 스키마)입니다.
   - **작업 및 파이프라인** — 자동화된 워크플로입니다.
   - **컴퓨팅** — 클러스터 및 SQL 웨어하우스 관리입니다.
   - **마켓플레이스** — 파트너 데이터 및 솔루션입니다.

2. **+ 새로 만들기**(사이드바 위쪽)를 클릭하고 생성할 수 있는 개체 유형(노트북, 쿼리, 클러스터, 대시보드 등)을 검토합니다. **아직 아무것도 생성하지 마세요** — 이것은 단순한 탐색용입니다.

3. 위쪽의 **검색** 막대를 사용하여 `routes`를 검색합니다. 아직 아무것도 나타나지 않지만, 수집 후 데이터 자산을 찾는 데 이를 사용할 것입니다.

### 작업 2: Genie Code 살펴보기

**Genie Code**는 Azure Databricks에 직접 내장된 AI 기반 페어 프로그래머입니다. 사용자 인터페이스를 떠나지 않고도 코드를 생성하고, 오류를 설명하고, 개선 사항을 제안하고, 질문에 답할 수 있습니다. 이 랩과 모든 향후 랩 전반에서 이를 사용할 것을 권장합니다.

1. Azure Databricks 홈 페이지에서 페이지 오른쪽 상단의 **Genie Code** 아이콘(![assistant-icon](https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/media/genie-code.svg))을 클릭하여 Genie Code 패널을 엽니다.

2. 다음 프롬프트를 입력하고 응답을 관찰합니다:

    ```
    데이터 엔지니어로서 Azure Databricks를 사용하여 무엇을 할 수 있나요?
    ```

3. 답변을 검토합니다. Genie Code가 컨텍스트 인식 워크스페이스 기반 지침을 어떻게 제공하는지 확인합니다.

> 💡 **이 시점부터 코드나 SQL을 작성하도록 요청받을 때마다 Genie Code를 사용하세요. 원하는 내용을 일반 언어로 설명한 다음 제안 사항을 적응하고 실행합니다.**

### 작업 3: 샘플 운송 데이터셋 업로드

CityMoves Transit은 경로 정보가 있는 CSV 파일을 제공했습니다. 작업은 데이터 수집 UI를 사용하여 워크스페이스에 업로드하여 이후 랩에서 사용할 수 있도록 하는 것입니다.

업로드하기 전에 파일을 저장할 Unity Catalog **볼륨**이 필요합니다. 다음 단계를 따르세요:

1. Databricks 워크스페이스 사이드바에서 **카탈로그**를 클릭합니다.
2. 카탈로그 탐색기에서 **adb-ws-####** 카탈로그를 확장한 다음 **default** 스키마를 확장합니다.
3. **default** 옆의 **⋮** 메뉴를 클릭한 다음 **만들기** > **볼륨**을 선택합니다.
4. 볼륨 이름으로 `lab_data`를 입력하고, 유형을 **관리 볼륨**으로 두고 **만들기**를 클릭합니다.

이제 데이터 파일을 업로드합니다:

5. Databricks 워크스페이스 사이드바에서 **+ 새로 만들기**를 클릭한 다음 **데이터 추가**를 선택합니다.

6. 데이터 업로드 인터페이스에서 **이 볼륨 upload**를 선택합니다.

7. 다음 파일 [routes.csv](https://github.com/asddai/AzureDatabricks/raw/main/Labs/data/routes.csv) 을 다운로드한 다음 **찾아보기**를 클릭하여 선택합니다:

8. 대상을 묻는 메시지가 나타나면 방금 생성한 볼륨을 선택합니다: **adb-ws-####** > **default** > **lab_data**.

9. 업로드가 완료되면 왼쪽 사이드바의 **카탈로그**로 이동하고 업로드된 파일을 찾습니다. 카탈로그 계층(**adb-ws-####** > **default** > **lab_data**)을 확장하여 routes.csv가 표시되는지 확인합니다.

    > **참고**: 이 랩에서는 데이터를 쿼리하거나 로드할 필요가 없습니다. 목표는 단순히 업로드 워크플로에 익숙해지는 것입니다. 이후 랩에서 이 데이터로 작업할 것입니다.

---

## 랩 노트북 가져오기

데이터 파일을 업로드한 후 랩 노트북을 Databricks 워크스페이스으로 가져옵니다.

1. Azure Databricks 워크스페이스에서 왼쪽 사이드바의 **워크스페이스**을 클릭합니다.

2. 랩을 저장할 폴더로 이동하거나 생성합니다(예: Labs/01-explore-azure-databricks).

3. 폴더 옆의 **⋮** 메뉴를 클릭하거나 마우스 오른쪽 단추로 클릭한 다음 **가져오기**를 선택합니다.

4. **URL**을 선택하고 다음 URL을 입력한 다음 **가져오기**를 클릭합니다:
  ```
https://github.com/asddai/AzureDatabricks/blob/main/Labs/Notebooks/01-explore-azure-databricks-KO.ipynb
  ```

5. 가져온 노트북을 엽니다. 노트북 위쪽의 컴퓨팅 선택기에서 **서버리스** 컴퓨팅을 선택합니다.

---

## 노트북에서 계속하기

UI 기반 연습을 완료했습니다. 이제 가져온 노트북 01-explore-azure-databricks.ipynb를 열고 실무 코딩 연습을 계속합니다.

셀을 실행하기 전에 **서버리스** 컴퓨팅이 선택되어 있는지 확인합니다.
