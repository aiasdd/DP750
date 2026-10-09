---
lab:
  index: 12
  title: Azure Databricks에서 개발 수명 주기 프로세스 구현
  module: Azure Databricks에서 개발 수명 주기 프로세스 구현
  module-url: https://learn.microsoft.com/training/wwl-databricks/implement-development-lifecycle-processes-in-azure-databricks/
  notebook: https://github.com/aiasdd/DP750/blob/main/Labs/Notebooks/Allfiles/12-implement-development-lifecycle-processes-in-azure-databricks-KO.ipynb
  description: 이 랩에서는 pytest를 사용하여 데이터 변환 파이프라인에 대한 테스트 전략을 구현한 다음 Databricks CLI를 사용하여 파이프라인을 Databricks 자산 번들로 패키지하고 배포합니다.
  duration: 50분
  level: 300
  islab: true
  primarytopics:
    - Azure Databricks
---

---
|구분|내용|
|---|---|
|설명| 이 랩에서는 pytest를 사용하여 데이터 변환 파이프라인에 대한 테스트 전략을 구현한 다음 Databricks CLI를 사용하여 파이프라인을 Databricks 자산 번들로 패키지하고 배포합니다.|
|소요시간| 50분|
|난이도| 300|
---

# 랩 12: Azure Databricks에서 개발 수명 주기 프로세스 구현

## 소개

귀사는 창고 운영 팀에서 사용하는 **주문 처리 파이프라인** 을 유지 관리하는 책임을 담당하는 데이터 엔지니어입니다. 파이프라인은 원본 주문 데이터를 읽고 유효하지 않은 기록을 제거하며 상태 코드를 정규화하고 세금 포함 합계를 계산합니다.

파이프라인이 프로덕션으로 이동함에 따라 팀은 적절한 **소프트웨어 개발 수명 주기(SDLC) 관행** 을 채택하기로 결정했습니다. 즉:

- 배포하기 전에 버그를 포착할 수 있도록 **테스팅 전략** 을 구현합니다
- 파이프라인을 **Databricks 자산 번들(DAB)** 로 패키지하여 환경 전반에서 일관되게 배포할 수 있습니다
- **Databricks CLI** 를 사용하여 번들을 검증하고 미리 보며 배포합니다

이 랩은 3부로 구성되어 있습니다:

| 부분 | 주제 | 위치 |
|------|-------|--------|
| **파트 1** | pytest를 사용한 단위 테스트 구현 | 노트북 |
| **파트 2** | Databricks 자산 번들 구성 | 작업 영역 터미널 |
| **파트 3** | Databricks CLI로 번들 배포 및 검증 | 작업 영역 터미널 |

---

## 🤖 이 랩 전체에서 Genie Code를 사용합니다

모든 연습에 **Genie Code** 를 사용할 것을 **강력히 권장합니다**.

Genie Code를 열려면 모든 노트북 셀 오른쪽에 있는 ![assistant-icon](https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/media/genie-code.svg)을 선택하거나 키보드 단축키를 사용합니다.

다음을 위해 사용하세요:
- pytest 고정장치 및 테스트 함수 생성
- 오류 메시지 이해 및 실패한 테스트 수정
- YAML 번들 구성 초안
- CLI 명령 구문 조회

---

## 필수 조건

- [랩 00: Azure Databricks 환경 설정](00-setup.md)을 사용하여 프로비저닝된 **Azure Databricks Premium 작업 영역**이 있습니다.
- 작업 영역에서 작업을 생성할 수 있는 권한이 있습니다(파트 3에 필요).
- Python 및 pytest에 대한 기본 이해가 있습니다.

---

## 파트 1: 테스팅 전략 구현(노트북)

### 노트북 가져오기

1. Databricks 작업 영역에서 왼쪽 사이드바의 **작업 영역** 을 클릭합니다.
2. 랩을 저장할 폴더로 이동하거나 생성합니다.
3. **⋮**(kebab 메뉴)를 클릭하거나 폴더를 마우스 오른쪽 단추로 클릭한 다음 **가져오기** 를 선택합니다.
4. **URL** 을 선택하고 다음 URL을 입력한 다음 **가져오기** 를 클릭합니다:

```
https://github.com/aiasdd/DP750/blob/main/Labs/Notebooks/12-implement-development-lifecycle-processes-in-azure-databricks-KO.ipynb
```

5. 가져온 노트북을 열고 위쪽의 컴퓨팅 선택기에서 **서버리스** 컴퓨팅을 선택합니다.

### 노트북 진행

노트북에는 3개의 연습이 포함되어 있습니다:

- **연습 1** — pytest를 설치하고 테스트할 제공된 **transforms.py** 모듈을 검토합니다.
- **연습 2** — pytest 고정장치를 사용하여 각 변환 함수에 대한 단위 테스트를 작성합니다.
- **연습 3** — Spark 세션으로 생성된 데이터에 대해 전체 파이프라인을 실행하는 통합 테스트를 작성합니다.

파트 2를 계속하기 전에 모든 연습을 완료합니다.

---

## 파트 2: Databricks 자산 번들 구성

Databricks 자산 번들(DAB)을 사용하면 Databricks 리소스(작업, 파이프라인, 노트북)를 YAML 구성 파일에 **코드로서의 인프라** 로 정의할 수 있습니다. 이렇게 하면 배포가 반복 가능하고 감사 가능합니다.

이 부분에서는 로컬 머신의 **Databricks CLI** 를 사용하여 주문 처리 작업에 대한 번들을 생성합니다.

### Databricks CLI 설치 및 구성

1. PowerShell을 사용하여 Databricks CLI를 설치합니다:

   ```powershell
   winget install Databricks.DatabricksCLI
   ```

   설치를 확인합니다:

   ```powershell
   databricks --version
   ```

2. Azure Databricks 작업 영역에 대해 CLI를 인증합니다:

   ```powershell
   databricks auth login --host https://<귀사의-작업-영역-url>
   ```

   **<귀사의-작업-영역-url>** 을 작업 영역의 URL로 바꿉니다(예: https://adb-1234567890123456.7.azuredatabricks.net). 브라우저 프롬프트를 따라 인증을 완료합니다.

3. 새 프로젝트 디렉터리를 생성하고 이동합니다:

   ```powershell
   mkdir ~/order-pipeline-bundle; cd ~/order-pipeline-bundle
   mkdir notebooks, resources
   ```

### 번들 구성 파일 생성

다음 요구 사항을 사용하여 databricks.yml 파일을 생성하는 것이 귀사의 작업입니다:

- 번들 이름: `order-pipeline-bundle`
- 변수 섹션:
  - 환경 변수(기본값: `development`)
  - cluster_policy_id 변수(설명 포함, 기본값 없음)
- 다음을 정의하는 order-pipeline-job이라는 작업이 있는 리소스 섹션:
  - 환경 변수를 사용하는 표시 이름: ${var.environment}-order-pipeline
  - 두 개의 노트북 작업:
    - validate-data — ./notebooks/validate.py 실행
    - transform-data — validate-data에 종속되며 ./notebooks/transform.py 실행
- 다음이 있는 대상 섹션:
  - dev 대상(기본값, 개발 모드, 환경 = development)
  - prod 대상(프로덕션 모드, 자체 작업 영역 호스트, 환경 = production)

아래 PowerShell 스니펫을 **시작점**으로 사용하고 `# TODO`로 표시된 섹션을 채웁니다:

```powershell
@'
bundle:
  name: order-pipeline-bundle

variables:
  environment:
    description: The deployment environment name
    default: development
  # TODO: 'cluster_policy_id'라는 변수 추가
  # 설명이 있어야 하고 기본값이 없어야 합니다.

resources:
  jobs:
    order-pipeline-job:
      name: ${var.environment}-order-pipeline
      tasks:
        - task_key: validate-data
          notebook_task:
            notebook_path: ./notebooks/validate.py
        # TODO: 'transform-data'라는 두 번째 작업 추가
        # 'validate-data'에 종속되어야 하고 ./notebooks/transform.py 실행
        # Databricks 자산 번들 스키마의 'depends_on' 키를 참조합니다.

targets:
  dev:
    default: true
    mode: development
    variables:
      environment: development
  # TODO: 다음을 수행하는 'prod' 대상 추가:
  # - 모드를 프로덕션으로 설정
  # - 작업 영역 호스트 설정(지금은 자리 표시자 URL 사용)
  # - 환경 변수를 'production'으로 오버라이드
'@ | Set-Content databricks.yml
```

> 🤖 **Genie Code 팁:** *"두 개의 대상, 작업 작업 및 사용자 지정 변수가 있는 완전한 Databricks 자산 번들 databricks.yml 예제를 보여주세요"*라고 하여 적응할 수 있는 전체 참조 구성을 얻습니다.

### 자리 표시자 노트북 생성(검증에 필요)

번들 검증은 참조되는 노트북이 존재하는지 확인합니다. 두 개의 자리 표시자 노트북 파일을 생성합니다:

```powershell
"# validate" | Set-Content notebooks/validate.py
"# transform" | Set-Content notebooks/transform.py
```

---

## 파트 3: Databricks CLI로 번들 배포 및 검증

번들이 구성되었으므로 **Databricks CLI** 를 사용하여 검증, 미리 보기 및 작업 영역에 배포합니다.

### 단계 1 — 번들 검증

order-pipeline-bundle 디렉터리 내에서 다음 명령을 실행합니다. 이렇게 하면 databricks.yml이 구문적으로 올바르고 유효한 리소스를 참조하는지 확인합니다.

```powershell
databricks bundle validate
```

검증에 성공하면 번들 이름, 대상 환경 및 작업 영역 경로를 보여주는 요약이 표시됩니다. 오류가 있으면 출력을 검토하고 계속하기 전에 YAML을 수정합니다.

> 🤖 **팁:** 검증 오류 메시지를 복사하여 Genie Code에 붙여넣어 설명과 제안된 수정 사항을 얻습니다.

### 단계 2 — 배포 계획 미리 보기

작업 영역에 변경하기 전에 배포가 무엇을 생성하거나 업데이트할 것인지 미리 봅니다:

```powershell
databricks bundle plan
```

출력을 검토합니다. order-pipeline-job이 **생성될** 것임을 알 수 있어야 합니다(아직 존재하지 않으므로). 기본이 아닌 대상의 경우 명시적으로 지정합니다:

```powershell
databricks bundle plan -t dev
```

### 단계 3 — 번들 배포

`dev` 대상에 번들을 배포합니다:

```powershell
databricks bundle deploy -t dev
```

배포 중에 CLI:
- 노트북 파일을 작업 영역에 업로드합니다
- 작업 영역의 **작업 및 파이프라인** 섹션에서 order-pipeline-job을 생성합니다(`[dev <사용자이름>]`으로 접두사 붙임, 개발 모드가 활성화되어 있기 때문)

### 단계 4 — 배포된 리소스 확인

배포 성공을 확인합니다:

```powershell
databricks bundle summary
```

출력에는 생성된 작업에 대한 직접 URL이 포함됩니다. 브라우저에서 URL을 열어 작업이 두 작업(validate-data 및 transform-data)이 올바르게 구성된 작업 영역에 나타나는지 확인합니다.

> 🤖 **팁:** *"Databricks 자산 번들 개발 모드는 작업 이름 및 일정에 어떤 영향을 미칩니까?"*라고 하여 작업이 사용자 이름으로 접두사가 붙는 이유를 이해합니다.

### 단계 5 — 정리(선택 사항)

작업 영역에서 배포된 리소스를 제거하려면:

```powershell
databricks bundle destroy -t dev
```

메시지가 표시될 때 생성된 작업을 삭제하도록 확인합니다.

---

## 요약

이 랩에서 귀사는:

- pytest 고정장치를 사용하여 **단위 테스트** 를 구현하여 개별 변환 함수를 검증했습니다
- 변수, 작업 리소스 및 다중 환경 대상을 사용하여 **Databricks 자산 번들** 을 구성했습니다
- **Databricks CLI** 를 사용하여 번들 배포를 검증하고, 계획하고, 배포하고, 검증했습니다
