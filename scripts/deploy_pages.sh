#!/usr/bin/env bash
# 01~10 빌드 결과(dist/hoban/NN)를 기존 Cloudflare Pages 프로젝트에 올린다.
# 번호별 프로젝트명은 저장소 밖 파일 deploy-projects.local 에 한 줄씩 "번호 프로젝트명"으로 적는다(커밋하지 않는다).
#   01 my-project-01
#   02 my-project-02
# 사용: scripts/deploy_pages.sh            # 계획만 출력(업로드 안 함)
#       scripts/deploy_pages.sh --go       # 실제 업로드
#       scripts/deploy_pages.sh --go 03 05 # 일부 번호만
# 빌드가 로컬 검토용 noindex이면 중단한다. 운영 공개 설정을 확인한 빌드만 올리려면 --allow-noindex를 붙인다.
set -euo pipefail
cd "$(dirname "$0")/.."
MAP="${DEPLOY_PROJECTS_FILE:-deploy-projects.local}"
GO=0; ALLOW_NOINDEX=0; ONLY=()
for a in "$@"; do
  case "$a" in --go) GO=1 ;; --allow-noindex) ALLOW_NOINDEX=1 ;; [0-1][0-9]) ONLY+=("$a") ;; *) echo "알 수 없는 인자: $a"; exit 2 ;; esac
done
[ -f "$MAP" ] || { echo "$MAP 파일이 없습니다. 각 줄에 '번호 프로젝트명'을 적어 주세요. (npx wrangler pages project list 로 기존 프로젝트를 확인)"; exit 2; }
want() { [ ${#ONLY[@]} -eq 0 ] && return 0; for o in "${ONLY[@]}"; do [ "$o" = "$1" ] && return 0; done; return 1; }
while read -r num project _; do
  [[ -z "${num:-}" || "$num" == \#* ]] && continue
  want "$num" || continue
  dir="dist/hoban/$num"
  [ -f "$dir/index.html" ] || { echo "[$num] $dir 없음: 먼저 빌드하세요"; exit 1; }
  [ -f "$dir/pyeong-converter/index.html" ] || { echo "[$num] 최신 빌드가 아닙니다(pyeong-converter 없음). 다시 빌드하세요"; exit 1; }
  if grep -rq 'content="noindex' "$dir/index.html" && [ "$ALLOW_NOINDEX" -eq 0 ]; then
    echo "[$num] 중단: 빌드가 검토용 noindex 상태입니다. 운영 공개 설정을 적용한 빌드인지 확인하세요. (PARTNER_INDEXNOW_20261023.md 2번)"; exit 1
  fi
  echo "[$num] $dir -> Cloudflare Pages 프로젝트 '$project'"
  if [ "$GO" -eq 1 ]; then npx wrangler pages deploy "$dir" --project-name "$project" --branch main; fi
done < "$MAP"
[ "$GO" -eq 1 ] || echo "계획만 출력했습니다. 실제로 올리려면 --go 를 붙이세요."
