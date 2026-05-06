import type { Policy } from "../types/chat";

export function dedupePolicies(policies: unknown = []): Policy[] {
  const seen = new Set<string>();
  const safePolicies = Array.isArray(policies) ? policies.filter(isPolicyLike) : [];

  return safePolicies.filter((policy, index) => {
    const key = getPolicyDedupKey(policy, index);
    if (seen.has(key)) {
      return false;
    }

    seen.add(key);
    return true;
  });
}

function isPolicyLike(value: unknown): value is Policy {
  return Boolean(value && typeof value === "object");
}

function getPolicyDedupKey(policy: Policy, index: number): string {
  const policyId = normalize(policy.policy_id);
  if (policyId) {
    return `policy_id:${policyId}`;
  }

  const policyName = normalize(policy.policy_name);
  const sourceUrl = normalize(policy.source_url ?? policy.url);
  if (policyName && sourceUrl) {
    return `policy_name_source:${policyName}:${sourceUrl}`;
  }

  if (policyName) {
    return `policy_name:${policyName}`;
  }

  const name = normalize(policy.name);
  if (name) {
    return `name:${name}`;
  }

  if (sourceUrl) {
    return `source_url:${sourceUrl}`;
  }

  return `unknown:${index}`;
}

function normalize(value: unknown): string | null {
  if (typeof value !== "string") {
    return null;
  }

  const normalized = value.trim().toLowerCase();
  return normalized.length > 0 ? normalized : null;
}
