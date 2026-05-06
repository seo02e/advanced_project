const STATUS_REPLACEMENTS: Array<[RegExp, string]> = [
  [/\bnot\s+eligible\b/gi, "대상 아님"],
  [/\bnot_eligible\b/gi, "대상 아님"],
  [/\bneeds_check\b/gi, "확인 필요"],
  [/\bneed_check\b/gi, "확인 필요"],
  [/\beligible\b/gi, "지원 가능성 높음"],
  [/\bmaybe\b/gi, "가능성 있음"],
  [/\balways\b/gi, "상시/마감 아님"],
];

export function formatStatusLabel(value: string): string {
  const normalized = value.trim().toLowerCase();

  if (normalized === "eligible") {
    return "지원 가능성 높음";
  }

  if (normalized === "maybe") {
    return "가능성 있음";
  }

  if (normalized === "확인 필요" || normalized === "needs_check" || normalized === "need_check") {
    return "확인 필요";
  }

  if (normalized === "not eligible" || normalized === "not_eligible") {
    return "대상 아님";
  }

  if (normalized === "always") {
    return "상시/마감 아님";
  }

  return formatStatusText(value);
}

export function formatStatusText(value: string): string {
  return STATUS_REPLACEMENTS.reduce(
    (text, [pattern, replacement]) => text.replace(pattern, replacement),
    value,
  );
}
