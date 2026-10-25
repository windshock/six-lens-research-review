# Six-lens checklist — 독립 질문에서 상호 반증까지

이 자료는 복잡하거나 논쟁적인 코드·실험 검토에서 불러온다. 모든 질문을 강제로 전부 작성하지 말고 **현 코드·자료로 확인 가능한 질문을 우선**하라. 검토 이슈마다 `관측 사실 → 가정 → 실패 기전 → 판별 실험 → 판정`의 다섯 요소를 적는다.

## 1. Experimental scientist / 실험과학자

- 시스템에 실제로 요청한 **자극(input)**은 무엇이며, 생성기/실행기/하네스/대상 프로그램의 경계를 통과했는가?
- 상태를 측정한 **정확한 시점**은 무엇인가? entry vs 초기화 완료 vs shutdown; 같은 이름의 state가 시점에 따라 다른 의미를 가지는가?
- 관측기(GDB, ASAN, tracing, log hook)가 시간을 늘리거나 scheduling/reentrancy, 연결 상태, 고장 순서를 바꿨는가?
- 음성 대조(입력/조건 없이 신호 0), 양성 대조(신호가 반드시 1회 이상 나오는 동작), 자기대조(동일 입력 재실행)가 있는가?
- 동일 입력 시 관측기 온/오프에서 비교 가능한 **외부 결과**를 비교하되, 관측기 없을 때 내부 상태가 관측된 척하지 않는다.
- 종료·미실행·reset·timeout·observer failure·실제 memory error의 신호가 합쳐지지 않았는가?

## 2. Runtime/domain engineer / 도메인 의미론 전문가

- 내부 상태 변수가 **어떤 함수에 의해 소유/초기화/해제**되며, 실제 invariant는 언제 적용되는가? 추정 invariants와 명시적 구현 invariants 분리.
- 함수 호출 사이트와 cleanup가 같은 요청 또는 worker epoch에 속하는가? PID 두 개가 모두 null인데 같다고 처리하지 않았는가?
- 포인터 주소 재등장 = 현재 같은 주소 관측일 뿐. 같은 allocation lifetime / object identity / UAF 여부는 별도 증거 필요.
- callback, GC, exception, bailout, destructor, refcount, allocator, SAPI 및 확장의 실행 경로에서 **어떤 상태 전이가 실제로 가능한가**?
- 컴파일 옵션, sanitizers, opcache, web SAPI, debug mode와 production mode가 상태/오라클 의미를 바꾸는가?
- `health` 같은 관찰 요청 자체가 상태를 바꾼다면 이를 무해한 probe라고 가정하지 않는다.

**PHP2Shell historical worked example (검토 시점 예시, 현재 HEAD 단정 금지):** `php_request_startup` entry에서 `gc_protected=1`은 `gc_reset` 이전 정상 경로에서도 생길 수 있다. post-reset 경계를 실제로 계측하지 않았다면 reset 후에도 보호가 남았다고 주장하지 않는다.

## 3. Mathematician/control theorist / 수학·제어이론 연구자

- 관측 함수 `h(p)`의 핵심 필드와 **포함/제외의 의미**를 명시하라. `h(p1)=h(p2)`는 진짜 내부 상태 일치의 충분조건이 아니다.
- 제한된 유효 후속 시퀀스 집합 Q에서 `p1 ~_Q p2`는 모든 측정된 `O(p,q)`가 같다는 **작업상의 관측 동치**; 미관측 q, 비결정성, 검열된 샘플이 있으면 `undistinguished_under_Q` 또는 unknown만 적어라.
- 정확한 상태 지문이 같아도 suffix의 응답·worker survival·정확히 귀속된 ASAN이 다르면 **behavior-distinguishing witness 후보**. 검증된 지문 차이는 state-distinguishing witness. 둘 다 독립 반복과 실행 무결성 필요.
- 점수식의 극한·편미분/단조성·상호 중복/보상 포화·피드백 루프를 계산하라. 예: `w=(1+new)/sqrt(1+picked)+b`에서 `picked→∞`이면 `b>0`인 항만 양의 상수로 남는다. **예측된 위험**과 **관측된 회귀**를 구별하라.
- 모델이 학습 데이터에만 맞는 것은 지식 획득이 아니다. 실험에 사용하지 않은 suffix에서 결과 예측과 오라클 유효성을 평가하라.
- 가장 정보성 있는 질의는 `Pr(valid)*expected discrimination / cost`로 시작하되, 사전 확률이 보정되지 않았으면 Shannon IG·Bayesian posterior를 숫자로 꾸미지 않는다.

## 4. Vulnerability/fuzzing/domain researcher / 위험 메커니즘 전문가

- 생성기 입력 언어의 표현력이 목표 행동(예: caught bailout, 재진입 GC, consumer action)을 **실제로 생성할 수 있는가**? 구조적 0이면 zero discovery는 스케줄러 실패의 증거가 아니다.
- 위험 실행 흐름을 `source/producer → state mutation/fault → cleanup gap → independent consumer` 형태로 쪼개라. 모든 상태 차이를 보안 결함으로 보상하지 말라.
- prior bugs/corpus를 **양성 대조**로만 사용한 것인지, 모델 튜닝에 노출된 데이터를 blind discovery라고 오표현한 것은 아닌가?
- ASAN이 발견하지 못한 경우도 특정 빌드/실행 조건의 미발견이지 안전 증명은 아니다.
- 함수를 단순히 호출한 것과 해당 결함 조건(인수, fault injection, 반환, worker 지속)을 충족한 것을 구분한다.
- 실제 시스템에 대한 취약점 검증은 권한 있는 격리 환경에서만 수행하고 미공개 결함은 책임 있는 신고 흐름으로 관리한다.

## 5. Statistician/causal inference researcher / 통계·인과추론 전문가

- 독립 실험 단위는 무엇인가? 같은 fingerprint의 `n`개 prefix에서 나온 `C(n,2)` 쌍은 같은 원시 이력을 공유하므로 독립 샘플이 아니다.
- 실제 처치가 있었는가? `treatment=ON`이지만 코드가 해당 분기에 진입하지 않았거나 후보 0이라 bonus applied 0이면 *treatment effect* 식별 불가.
- 고정 시드가 독립 반복을 의미하는가? 시드 간 동일 생성기/캠페인 공유, worker reset과 시간 오차를 확인하라.
- wall/CPU 예산·GDB 오버헤드·유효 실행 수·후보 도달률이 같았는가? 사후에 성공 정의를 바꾸지 않았는가?
- 비교군이 동일한 소프트웨어를 실행했는가(ABI, INI, SAPI, fused pool SHA, opcache)? 신호원/생성기 변경과 스케줄러 변경을 동시에 하지 말라.
- 희귀 발견 `0/3`은 효과 추정의 검정력이 매우 낮다. 유효 목표 전이/비용의 신뢰구간·효과크기와 미지 발견은 별도 논의하라.

## 6. Scientific Discovery Agent architect / AI 과학적 발견 시스템 설계자

- `가설과 대립 가설 → 사전 예측 → 질의 선택 이유 → 실행 매니페스트 → 독립 오라클 → 증거가 지지/반박한 가설 → 다음 질의 변화`가 한 trace로 연결되는가?
- 제안자와 판정자가 동일한 LLM이라면 **구조적 자기 승인**이 일어나지 않는가? 판정기는 코드를 통해 원시 증적과 동결된 규칙을 확인하도록 분리하라.
- unknown/invalid 상황에서도 `무효 실행을 줄이는 질문`을 학습할 수 있지만 이를 상태 분할의 증거로 승격하지 말라.
- 새로운 추론 구조의 학습 성공은 최소한 **새 입력에서의 예측 개선 / 유효 구별 질문 비용 감소 / 다음 쿼리 변경의 감사 가능성** 중 하나로 독립 확인하라.
- synthetic SUL에서 정확히 2개의 숨은 상태, 동일한 초기 관측, 특정 suffix의 행동 차이를 만들고 end-to-end로 검증할 수 있는가?

## 서로 충돌하는 전제의 예

| A 관점 주장 | B 관점 반증 | 해야 할 일 |
| --- | --- | --- |
| 같은 지문 = 같은 상태 | PHP 내부 reset 시점 미관측 | 미관측 post-reset 상태는 unknown, 새로운 관측점 비용 평가 |
| 보너스 +1은 신규 위험 신호 강조 | 수학적으로 선택 횟수가 커져도 보너스 비감쇠 | 선택분포 계산 + live positive-control; 지금 바로 성능 악화 단정 금지 |
| batch 9/9 통과 = 3군 비교 성공 | 실제 신규 모드 scheduler 0줄 | 실행 유효성/알고리즘 충실도/신호원 식별성 분리 |
| 상태 쌍 111,817개 확보 | 4개 지문에서 조합만 대량 생성 | 원본 실험 단위·유효 구별 suffix 수를 우선 평가 |
| 구별 반례 0 = 모델 정확 | 22/28 unknown, 재생 부정확 가능성 | 유효성·원인별 재분류 및 재생 계약부터 교정 |
