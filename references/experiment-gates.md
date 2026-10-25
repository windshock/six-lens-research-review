# Evidence tiers, experiment gates, and scientific validity

이 문서는 분석/실험의 **"증거가 무엇을 지지하는가"**를 판정할 때 필요하다. 시험을 수행하지 않은 경우 FAIL이 아니라 `NOT_TESTED`로 표시할 수 있으나, **성공을 선언하는 데 필수인 게이트가 NOT_TESTED면 그 성공을 승인하지 않는다.**

## 증거 강도 (사실 자체의 타입)

| 분류 | 의미 | 올바른 표현 |
| --- | --- | --- |
| `CODE_VERIFIED` | 실제 현재 소스·커밋에서 분기/조건/계산 확인 | "현재 코드에서는 +1 보너스가 감쇠하지 않는다" |
| `REPORTED_RESULT` | 커밋·보고서에 실측이 기록됨, 원본 재실행은 하지 않음 | "커밋에 230건이라고 보고됐다" |
| `INDEPENDENTLY_REPRODUCED` | 동일 조건에서 직접 재실행하고 증적 확보 | "독립 재실행에서 3/3 동일 결과 확인" |
| `DERIVED` | 명시적 코드/수학적 가정으로부터 논리적으로 도출 | "picked→∞에서 weight→1" |
| `HYPOTHESIS` | 반증할 수 있는 메커니즘 추정 | "상수 보너스가 부모 집중을 증가시킬 수 있다" |
| `UNKNOWN` | 관측 부족·접근 제한·검증 미완료 | "원본 랩 증적을 확인하지 못했다" |

`CODE_VERIFIED`는 경로가 실제 사용됐다는 증거가 아니다. `DERIVED` 예측은 실제 대상 워크로드에서의 효과 실측과 구별한다. 출처는 commit SHA/파일/라인/실험 ID가 원칙이다.

## 결론 범위 (conclusion scope)

증거 강도와 독립된 두 번째 축이다. 어휘 출처: `security-hypothesis-lab`의 references/conclusion-strength.md.

| 범위 | 조건 | 올바른 표현 |
| --- | --- | --- |
| `target-proven` | 대상 시스템 자체에서 주장된 행동이 관측되고 필요한 전제가 확인됨 | "대상에서 X가 관측됐다" |
| `lab-proven` | 확인된 대상 사실을 반영한 실험실에서 재현됐으나 대상 종단 간 증명은 아님 | "대상 형태의 실험실에서 X를 재현했다; 대상 전제 Y는 미확인" |
| `hypothesis-only` | 그럴듯하나 미검증 전제에 의존 | "Y가 성립하면 X가 될 수 있다" |

- 격리 실험실만 허용된 연구(예: 메모리 오류 관측까지만 허용)에서는 상한이 `lab-proven`이다. 실제 배포 영향은 기본 설정·SAPI·확장 조합 같은 **대상 전제 목록**과 함께 `hypothesis-only`로 둔다.
- 보고는 **확인된 프리미티브 → 추가 조건이 필요한 공격 경로 → 피해** 순으로 분리한다. 책임 있는 신고 문서에도 같은 분리를 쓴다.
- `INDEPENDENTLY_REPRODUCED`이면서 `hypothesis-only`일 수 있다(실험실 현상은 재현됐지만 대상 전제가 미확인). 두 축을 한 단어로 합치지 말라.

## 게이트 계약

| Gate | 반드시 확인할 사실 | FAIL 또는 NOT_TESTED의 처리 |
| --- | --- | --- |
| **G1** 재생 충실도 | 전체 입력/모든 인수, 버전/sha, PHP/build/ini/config/옵션, observer/하네스, 실행 위치 재현 | `replay_invalid`; model split 금지 |
| **G2** 관측·도달 | 대상 호출/전제조건과 suffix 실제 도달, 필수 상태·타임스탬프·worker 동일성/계측 위치 | `observer_incomplete` 또는 `not_reached`; 오라클의 같음/다름 판정 금지 |
| **G3** 오라클 | actual fault와 harness/timeout/network error 분리, PID/step 귀속, 동결된 결과 해석 | `inconclusive`; 오류 부류·UAF 확정 금지 |
| **G4** 실행 알고리즘 | feedback mode 분기, corpus 등록, 유효 부모 선택, candidate→reward→선택→child 실행 | 모드 성능 비교 `invalid` 또는 신호원 0이라면 `effect_not_identifiable` |
| **G5** 독립 반복/인과 | 자기대조·교란 통제·비용, 독립 seed/worker, hold-out, 전처리와 분석 사전등록 | 우월성 주장 보류, 탐색 기록은 기술통계만 가능 |
| **G6** 지식 갱신 | G1–G3·필요 시 G4–G5 및 검증된 구별 증거, 이전 모델/수정 이유 기록 | 자동 모델 분할/새 결함 확정 금지 |

G4는 **계층적으로 세분화**하라: `algorithm_ran` / `source_reachable` / `signal_observed` / `candidate_admitted` / `bonus_applied` / `parent_selected` / `valid_child_executed`. `candidate=0`인 실험은 충분히 정상적인 *negative control*일 수 있으나, 해당 bonus의 효과는 식별되지 않는다. 그 경우 `G4 algorithm_ran=PASS`, `treatment_activation=NOT_APPLICABLE/NO_EXPOSURE`를 같이 기재한다.

## 상태 구별의 최소 증적 계약

현재 관측 h(p1)=h(p2)임을 확인한 뒤, 동일 환경에서 정확한 p1+q, p2+q를 **독립 프로세스**에서 실행한다.

1. 각 prefix+suffix 실행에 대해 완전한 단계 인수/환경 해시를 보존한다.
2. 자기 대조(같은 prefix+suffix 반복)에서 결과가 안정적인지 검사한다.
3. 유효 suffix가 실제 실행됐는지, ASAN/worker가 해당 suffix에 속하는지 검증한다.
4. 요청별 후속 관측 `O_e(p,q)|q`가 다르면 `behavior_distinguishing_witness`, 새로운 지문이 다르면 `state_distinguishing_witness` 후보로 분류한다. **서로 다른 비교 도구가 단순히 다른 로그를 만들었다는 것은 반례가 아니다.**
5. 독립 재검증 후 모델 블록을 분할하되, 시험하지 않은 다른 prefix에 검증 결과를 자동 전파하지 않는다.
6. 유효 q 집합에서 차이가 없으면 `undistinguished_under_Q`, 실제 q 미도달은 `unknown/not_reached`.

## 통계 오류 방지

- n개 prefix에서 `n*(n-1)/2` 쌍을 만들어도 독립 표본 수가 증가하는 것은 아니다(공유 원시 실행).
- `0` findings에서 발견 능력 우위 비교는 어려울 수 있다. 사전등록된 유효 목표 이벤트 도달률, 실행당 비용, 예측 calibration/hold-out으로 별도 평가한다.
- 보상 수학식에서 장기 집중 위험을 찾았다면 **합성 시험에서 weight 변화를 계산**하고, 실제 시스템에서 동일 효과가 발생하는지는 별도 대조 실행으로 검증한다.
- off/state/invariant/model의 비교는 고정된 생성기/알파벳과 버전·설정·샘플링 단위가 같아야 한다. 생성기와 피드백을 동시에 바꾸면 attribution이 어려워진다.

## 권장 심각도

- **P0:** 사용자가 실험에 의존해 잘못된 결론을 낼 수 있음, 잘못된 상태 분할/자동 대응, 원본 재생 불충실, 잘못된 실행군, 무효 실험의 성공 판정.
- **P1:** 유효한 알고리즘이 성과를 내지 못할 수 있음, 중복 탐색·무의미 신호·보상 고착·통계 검정력 부족.
- **P2:** 개선 여지는 있지만 현재 결론의 유효성을 깨뜨리지 않음, 보조 계측·대형 학습기 도입·성능 최적화 등.
