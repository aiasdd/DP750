---
lab:
  index: 12
  title: Azure Databricks에서 개발 수명 주기 프로세스 구현
  module: Azure Databricks에서 개발 수명 주기 프로세스 구현
  module-url: https://learn.microsoft.com/training/modules/implement-development-lifecycle-processes-in-azure-databricks/
  notebook: https://github.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/blob/main/Allfiles/12-implement-development-lifecycle-processes-in-azure-databricks.ipynb
  description: 이 랩에서는 pytest를 사용하여 데이터 변환 파이프라인의 테스트 전략을 구현한 다음, Databricks CLI를 사용하여 파이프라인을 선언적 자동화 번들로 패키징하고 배포합니다.
  duration: 45분
  level: 300
  islab: true
  primarytopics:
    - Azure Databricks
---

# 랩 12: Azure Databricks에서 개발 수명 주기 프로세스 구현

## 소개

여러분은 창고 운영 팀에서 사용하는 **주문 처리 파이프라인**을 유지 관리하는 데이터 엔지니어입니다. 이 파이프라인은 원시 주문 데이터를 읽고, 유효하지 않은 레코드를 제거하고, 상태 코드를 정규화하고, 세금이 포함된 총액을 계산합니다.

파이프라인의 프로덕션 전환을 앞두고 팀에서는 적절한 **SDLC(소프트웨어 개발 수명 주기) 방식**을 도입하기로 했습니다. 여기에는 다음 작업이 포함됩니다.

- 배포 전에 버그를 발견할 수 있도록 **테스트 전략** 구현
- 여러 환경에서 파이프라인을 일관되게 배포할 수 있도록 **DAB(Declarative Automation Bundle, 선언적 자동화 번들)**로 패키징
- **Databricks CLI**를 사용하여 번들을 검증하고, 미리 보고, 배포

이 랩은 다음 세 파트로 구성됩니다.

| 파트 | 주제 | 작업 위치 |
|------|------|-----------|
| **파트 1** | pytest를 사용하여 단위 테스트 구현 | Azure Databricks 작업 영역의 Serverless 컴퓨팅에서 실행되는 노트북 |
| **파트 2** | 선언적 자동화 번들 구성 | **로컬 컴퓨터의 PowerShell 터미널**(Databricks CLI는 로컬에서 실행됨) |
| **파트 3** | Databricks CLI를 사용하여 번들 배포 및 확인 | 동일한 **로컬 PowerShell 터미널**에서 작업한 후 Databricks 작업 영역 UI에서 확인 |

> **중요:** 파트 2와 3에서는 Databricks 작업 영역 내부의 터미널이 아니라 **컴퓨터 또는 랩 가상 머신에 설치된 Databricks CLI**를 사용합니다. 이 파트를 진행하려면 로컬 PowerShell 창을 열고 작업이 끝날 때까지 열어 두세요.

---

## 🤖 이 랩 전체에서 Genie Code 사용

모든 연습에서 **Genie Code**를 사용하는 것을 **권장**합니다.

Genie Code를 열려면 노트북 셀 오른쪽에 있는 ![assistant-icon](https://raw.githubusercontent.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/refs/heads/main/Allfiles/media/genie-code.svg) 아이콘을 선택하거나 바로 가기 키를 사용합니다.

다음 작업에 활용할 수 있습니다.
- pytest 픽스처 및 테스트 함수 생성
- 오류 메시지 이해 및 실패한 테스트 수정
- YAML 번들 구성 초안 작성
- CLI 명령 구문 검색

---

## 필수 조건

- [랩 00: Azure Databricks 환경 설정](00-setup.md)을 사용하여 프로비전한 **Azure Databricks Premium 작업 영역**
- 작업 영역에서 작업을 만들 수 있는 권한(파트 3에 필요)
- Python 및 pytest에 대한 기본 지식

---

## 파트 1: 테스트 전략 구현(노트북)

### 노트북 가져오기

1. Databricks 작업 영역의 왼쪽 사이드바에서 **Workspace**를 클릭합니다.
2. 랩을 저장할 폴더로 이동하거나 새 폴더를 만듭니다.
3. **⋮**(케밥 메뉴)를 클릭하거나 폴더를 마우스 오른쪽 단추로 클릭한 다음 **Import**를 선택합니다.
4. **URL**을 선택하고 다음 URL을 입력한 다음 **Import**를 클릭합니다.
   `https://github.com/aiasdd/DP750/blob/main/Labs/Notebooks/12-implement-development-lifecycle-processes-in-azure-databricks-KO.ipynb`
5. 가져온 노트북을 열고 상단의 컴퓨팅 선택기에서 **Serverless** 컴퓨팅을 선택합니다.

### 노트북 실습 진행

노트북에는 다음 세 개의 연습이 포함되어 있습니다.

- **Exercise 1** — pytest를 설치하고 테스트할 **transforms.py** 모듈을 검토합니다.
- **Exercise 2** — pytest 픽스처를 사용하여 각 변환 함수에 대한 단위 테스트를 작성합니다.
- **Exercise 3** — Spark 세션으로 만든 데이터를 대상으로 전체 파이프라인을 실행하는 통합 테스트를 작성합니다.

파트 2로 계속하기 전에 모든 연습을 완료합니다.

---

## 파트 2: 선언적 자동화 번들 구성

DAB(Declarative Automation Bundle, 선언적 자동화 번들)를 사용하면 작업, 파이프라인, 노트북과 같은 Databricks 리소스를 YAML 구성 파일의 **코드형 인프라**로 정의할 수 있습니다. 이를 통해 반복 가능하고 감사 가능한 배포를 구현할 수 있습니다.

이 파트에서는 로컬 컴퓨터의 **Databricks CLI**를 사용하여 주문 처리 작업용 번들을 만듭니다.

> **작업 위치:** 파트 2와 3의 모든 명령은 **사용자 컴퓨터 또는 랩 가상 머신의 PowerShell 터미널**에서 실행합니다. 지금 **Windows Terminal** 또는 **PowerShell**을 열고 나머지 랩을 진행하는 동안 계속 열어 두세요. Databricks CLI는 네트워크를 통해 작업 영역과 통신합니다. 이 명령을 Databricks 웹 UI 내부에서 실행하면 **안 됩니다**.

### Databricks CLI 설치 및 구성

1. 로컬 PowerShell 창에서 Databricks CLI를 설치합니다.

   ```powershell
   winget install Databricks.DatabricksCLI
   ```

   새 `databricks` 명령이 PATH에 추가되도록 PowerShell을 **닫았다가 다시 연** 다음 설치를 확인합니다.

   ```powershell
   databricks --version
   ```

   *예상 결과:* 명령이 버전 번호(예: `Databricks CLI v0.x.x`)를 출력합니다. 명령을 인식할 수 없다고 표시되면 PowerShell을 다시 열고 다시 시도합니다.

2. Azure Databricks 작업 영역에 CLI를 인증합니다.

   ```powershell
   databricks auth login --host https://<your-workspace-url>
   ```

   **<your-workspace-url>**을 작업 영역의 URL(예: https://adb-1234567890123456.7.azuredatabricks.net)로 바꿉니다. 작업 영역이 열려 있을 때 브라우저의 주소 표시줄에서 이 URL을 복사할 수 있습니다. **프로필 이름**을 묻는 메시지가 표시되면 Enter 키를 눌러 기본값을 적용합니다. 브라우저 창이 열리면 로그인하고 요청을 승인합니다.

   *예상 결과:* PowerShell에 `Profile DEFAULT was successfully saved`가 표시되어 CLI가 작업 영역에 인증되었음을 확인할 수 있습니다.

3. 새 프로젝트 디렉터리와 번들에 필요한 두 하위 폴더를 만든 다음 프로젝트 디렉터리로 이동합니다.

   ```powershell
   mkdir ~/order-pipeline-bundle; cd ~/order-pipeline-bundle
   mkdir notebooks, resources
   ```

   *예상 결과:* PowerShell 프롬프트가 `order-pipeline-bundle`로 끝나고 폴더에 빈 `notebooks` 및 `resources` 하위 폴더가 포함됩니다. `ls`를 실행하여 확인합니다.

### 번들 구성 파일 만들기

**databricks.yml** 파일은 선언적 자동화 번들의 핵심이며 배포할 리소스를 설명합니다. 이 단계에서는 `order-pipeline-bundle` 폴더의 루트에 이 파일을 만듭니다. 다음 요구 사항을 충족하는 databricks.yml 파일을 작성해야 합니다.

- 번들 이름: `order-pipeline-bundle`
- 다음을 포함하는 variables 섹션:
  - `environment` 변수(기본값: `development`)
  - 설명과 **빈 문자열 기본값(`""`)**을 포함하는 `cluster_policy_id` 변수. 클러스터 정책 ID는 작업 클러스터에 구성 규칙을 적용하며, 프로덕션 번들에서는 해당 클러스터에서 이 값을 참조합니다. 이 랩에서는 작업에 Serverless 컴퓨팅을 사용하므로 빈 문자열 기본값을 지정하여 변수를 **선택 사항**으로 만들고 배포할 때 값을 제공하지 않아도 되도록 합니다. 실제 값을 사용하려면 작업 영역의 **Compute** > **Policies**에서 정책을 열고 세부 정보 또는 URL에 표시된 정책 ID를 복사합니다.
- order-pipeline-job이라는 작업을 정의하는 resources 섹션:
  - 환경 변수를 사용하는 표시 이름: ${var.environment}-order-pipeline
  - 다음 두 개의 노트북 태스크:
    - validate-data — ./notebooks/validate.py 실행
    - transform-data — validate-data에 종속되며 ./notebooks/transform.py 실행
- 다음을 포함하는 targets 섹션:
  - dev 대상(기본 대상, 개발 모드, environment = development)
  - prod 대상(프로덕션 모드, 자체 작업 영역 호스트, environment = production)

명령줄보다 YAML을 쉽게 읽고 편집할 수 있도록 일반 텍스트 편집기를 사용하여 이 파일을 만듭니다.

1. 텍스트 편집기에서 `order-pipeline-bundle` 폴더를 엽니다.

   - **VS Code**(권장): PowerShell 창에서 `code .`을 실행하여 현재 폴더를 엽니다. `code` 명령을 사용할 수 없으면 VS Code를 직접 열고 **File** > **Open Folder**를 선택한 다음 `order-pipeline-bundle` 폴더를 선택합니다.
   - **Notepad**: `notepad databricks.yml`을 실행합니다. 파일이 아직 없으므로 파일을 만들 것인지 묻는 메시지가 표시되면 **Yes**를 선택합니다.

2. `order-pipeline-bundle` 폴더의 루트에 **databricks.yml**이라는 새 파일을 만듭니다(VS Code에서는 **New File**을 선택하고 이름을 `databricks.yml`로 지정).

3. 아래의 시작 구성을 파일에 복사합니다. 번들 이름, `environment` 변수, 첫 번째 태스크 및 `dev` 대상은 이미 포함되어 있습니다. `# TODO`로 표시된 세 섹션을 완성합니다.

   ```yaml
   bundle:
     name: order-pipeline-bundle

   variables:
     environment:
       description: The deployment environment name
       default: development
     # TODO: Add a variable named 'cluster_policy_id'.
     # Give it a 'description' and a 'default' value of "" (an empty string),
     # which makes the variable optional so you don't have to supply it at deploy time.
     # (A real cluster policy ID comes from Compute > Policies in your workspace,
     # but you don't need one for this lab.)

   resources:
     jobs:
       order-pipeline-job:
         name: ${var.environment}-order-pipeline
         tasks:
           - task_key: validate-data
             notebook_task:
               notebook_path: ./notebooks/validate.py
           # TODO: Add a second task named 'transform-data'
           # It should depend on 'validate-data' and run ./notebooks/transform.py
           # Refer to the 'depends_on' key in the Declarative Automation Bundle schema.

   targets:
     dev:
       default: true
       mode: development
       variables:
         environment: development
     # TODO: Add a 'prod' target that:
     # - sets mode to production
     # - sets a workspace host (use a placeholder URL for now)
     # - overrides the environment variable to 'production'
   ```

   > **팁:** YAML은 들여쓰기에 민감합니다. 각 수준마다 **공백 두 칸**을 사용하고 탭은 사용하지 마세요. 각 `# TODO` 블록을 주변 예제 줄에 맞춰 정렬합니다.

4. 파일을 **저장**합니다(VS Code에서는 **Ctrl+S**, Notepad에서는 **File** > **Save** 선택). `notebooks` 또는 `resources` 내부가 아니라 order-pipeline-bundle 폴더 바로 아래에 `databricks.yml`로 저장되었는지 확인합니다.

> 🤖 **Genie Code 팁:** 적용할 수 있는 전체 참조 구성을 확인하려면 *"두 개의 대상, 작업 태스크 및 사용자 지정 변수가 포함된 완전한 선언적 자동화 번들 databricks.yml 예제를 보여 줘"*라고 요청합니다.

> **솔루션이 필요한가요?** 모든 `# TODO` 섹션이 완성된 참조 파일은 [Allfiles/answers/12-databricks-bundle-with-answers.yml](https://github.com/MicrosoftLearning/DP-750T00-Implement-Data-Engineering-Solutions-using-Azure-Databricks/blob/main/Allfiles/answers/12-databricks-bundle-with-answers.yml)에서 확인할 수 있습니다. 먼저 `# TODO` 섹션을 직접 완성한 다음 솔루션과 비교하세요.

*예상 결과:* order-pipeline-bundle의 루트에 databricks.yml 파일이 있고, 파일에는 cluster_policy_id 변수, depends_on이 지정된 두 번째 transform-data 태스크 및 추가한 prod 대상이 포함되어 있습니다. PowerShell에서 `Get-Content databricks.yml`을 실행하여 확인할 수 있습니다.

### 자리 표시자 노트북 만들기(검증에 필요)

번들 검증에서는 `databricks.yml`에서 참조하는 모든 노트북이 실제로 디스크에 존재하고 **Databricks 노트북인지** 확인합니다. 일반 `.py` 파일만으로는 충분하지 않습니다. Databricks 소스 형식 노트북은 특수한 첫 줄 `# Databricks notebook source`로 시작해야 하며, 파일은 **BOM(바이트 순서 표시) 없는 UTF-8**로 저장해야 합니다. 파일에 BOM이 있거나 다른 인코딩을 사용하면 편집기에서 텍스트가 올바르게 보여도 Databricks CLI가 헤더를 감지하지 못하고 *"... is not a notebook"* 오류와 함께 검증에 실패합니다.

로컬 PowerShell 창에서 다음 명령을 실행하여(계속 `order-pipeline-bundle` 폴더 내부에서) BOM 없는 UTF-8 형식의 자리 표시자 노트북 두 개를 만듭니다.

```powershell
[System.IO.File]::WriteAllLines("$PWD\notebooks\validate.py",  @("# Databricks notebook source", "# validate"))
[System.IO.File]::WriteAllLines("$PWD\notebooks\transform.py", @("# Databricks notebook source", "# transform"))
```

> **`Set-Content`를 사용하지 않는 이유는 무엇인가요?** `Set-Content`(및 `Out-File`)는 PowerShell 버전에 따라 BOM을 앞에 추가하거나 UTF-16을 사용할 수 있으며, 이로 인해 *"is not a notebook"* 오류가 발생합니다. `[System.IO.File]::WriteAllLines`는 항상 BOM **없는** UTF-8로 작성하므로 매직 헤더가 파일의 맨 처음에 위치합니다.

*예상 결과:* `notebooks` 폴더에 `validate.py`와 `transform.py`가 있으며 각 파일은 `# Databricks notebook source`로 시작합니다. `Get-Content notebooks/validate.py`를 실행하여 헤더가 첫 번째 줄에 있는지 확인합니다. `databricks bundle validate`를 다시 실행하면 *"is not a notebook"* 오류가 더 이상 표시되지 않습니다.

---

## 파트 3: Databricks CLI를 사용하여 번들 배포 및 확인

번들 구성을 완료했으므로 **Databricks CLI**를 사용하여 작업 영역에서 번들을 검증하고, 배포 계획을 미리 보고, 배포합니다.

> **작업 위치:** 이 파트의 모든 명령은 **로컬 PowerShell 창**의 `order-pipeline-bundle` 폴더 내부에서 실행합니다. PowerShell을 닫았다면 다시 열고 먼저 `cd ~/order-pipeline-bundle`을 실행합니다.

### 1단계 — 번들 검증

order-pipeline-bundle 디렉터리 내부에서 다음 명령을 실행합니다. 이 명령은 databricks.yml의 구문이 올바르고 유효한 리소스를 참조하는지 확인합니다.

```powershell
databricks bundle validate
```

*예상 결과:* 명령이 번들의 **Name**(`order-pipeline-bundle`), **Target**(`dev`) 및 **Workspace** 경로를 보여 주는 요약을 출력한 다음 `Validation OK!`를 표시합니다. 오류가 표시되면 메시지(일반적으로 문제가 있는 줄 또는 키를 알려 줌)를 읽고 YAML을 수정한 다음 명령을 다시 실행합니다.

> 🤖 **팁:** 검증 오류 메시지를 복사하여 Genie Code에 붙여 넣으면 설명과 권장 수정 방법을 확인할 수 있습니다.

### 2단계 — 배포 계획 미리 보기

작업 영역을 변경하기 전에 배포에서 만들거나 업데이트할 항목을 미리 봅니다.

```powershell
databricks bundle plan
```

출력을 검토합니다. *예상 결과:* order-pipeline-job이 아직 없으므로 계획에서 **생성됨**으로 보고됩니다. 이 단계에서는 리소스가 변경되지 않습니다. 특정 대상을 기준으로 계획을 실행하려면 대상을 명시적으로 지정합니다.

```powershell
databricks bundle plan -t dev
```

### 3단계 — 번들 배포

번들을 `dev` 대상에 배포합니다.

```powershell
databricks bundle deploy -t dev
```

배포하는 동안 CLI는 다음 작업을 수행합니다.
- 노트북 파일을 작업 영역에 업로드
- 작업 영역의 **Jobs & Pipelines** 섹션에 order-pipeline-job 생성(개발 모드가 활성화되어 있으므로 이름 앞에 `[dev <username>]`이 추가됨)

*예상 결과:* 오류 없이 명령이 완료되고 `Deployment complete!`와 같은 메시지가 표시됩니다.

### 4단계 — 배포된 리소스 확인

배포에 성공했는지 확인합니다.

```powershell
databricks bundle summary
```

*예상 결과:* 출력에 배포된 **order-pipeline-job**과 해당 작업으로 연결되는 직접 **URL**이 표시됩니다. 브라우저에서 URL을 열거나 작업 영역의 **Jobs & Pipelines**로 이동하여 다음을 확인합니다.
- 작업 이름 앞에 `[dev <your-username>]`이 추가되어 표시됩니다.
- 작업을 열면 **validate-data**와 **transform-data**라는 두 태스크가 표시되며, 태스크 그래프에서 **transform-data**가 **validate-data**에 종속되어 있습니다.

> 🤖 **팁:** 작업 이름 앞에 사용자 이름이 추가되는 이유를 이해하려면 *"선언적 자동화 번들의 개발 모드는 작업 이름과 일정에 어떤 영향을 주나요?"*라고 질문합니다.

### 5단계 — 정리(선택 사항)

작업 영역에서 배포된 리소스를 제거하려면 `order-pipeline-bundle` 폴더에서 다음 명령을 실행합니다.

```powershell
databricks bundle destroy -t dev
```

메시지가 표시되면 생성된 작업을 삭제할 것인지 확인합니다. *예상 결과:* CLI에서 리소스가 제거되었다고 보고하며 작업이 더 이상 **Jobs & Pipelines**에 표시되지 않습니다.

---

## 요약

이 랩에서는 다음 작업을 수행했습니다.

- pytest 픽스처를 사용하여 개별 변환 함수를 확인하는 **단위 테스트** 구현
- 변수, 작업 리소스 및 다중 환경 대상을 포함하는 **선언적 자동화 번들** 구성
- **Databricks CLI**를 사용하여 번들 배포를 검증하고, 계획하고, 배포하고, 확인
