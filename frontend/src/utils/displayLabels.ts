const SOURCE_LABELS: Array<[string, string]> = [
  ["youth-up.kr", "청년정책 플랫폼"],
  ["work24.go.kr", "고용24"],
  ["kua.go.kr", "국민취업지원제도"],
  ["welfare.comwel.or.kr", "근로복지공단"],
  ["lh.or.kr", "LH"],
  ["bokjiro.go.kr", "복지로"],
  ["gov.kr", "정부24"],
  ["kosaf.go.kr", "한국장학재단"],
  ["smes.go.kr", "중소벤처기업부/중소기업 지원"],
];

export function getSourceDisplayLabel(hostname: string): string {
  const normalizedHost = hostname.replace(/^www\./, "").toLowerCase();
  const match = SOURCE_LABELS.find(([domain]) => normalizedHost.endsWith(domain));

  if (!match) {
    return normalizedHost;
  }

  const [domain, label] = match;
  return `${label} (${domain})`;
}
