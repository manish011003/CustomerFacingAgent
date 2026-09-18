import type { PlatformId } from "./products/platform";
import type { PlatformChrome } from "./products/platform";
import { CustomerResolveChrome } from "./products/customer-platform";
import { ManagerCrmChrome } from "./products/manager-platform";
import type { DecisionChrome, DecisionTone } from "./products/decision";
import {
  AllowDecisionChrome,
  AskDecisionChrome,
  DenyDecisionChrome,
  EscalateDecisionChrome,
  InformDecisionChrome,
} from "./products/decision";

const PLATFORM_REGISTRY: Record<PlatformId, () => PlatformChrome> = {
  customer: () => new CustomerResolveChrome(),
  manager: () => new ManagerCrmChrome(),
};

/** Factory method — pages request chrome by platform id, never by concrete class. */
export function createPlatform(id: PlatformId): PlatformChrome {
  const product = PLATFORM_REGISTRY[id];
  if (!product) throw new Error(`Unknown platform: ${id}`);
  return product();
}

const DECISION_REGISTRY: Record<DecisionTone, () => DecisionChrome> = {
  ALLOW: () => new AllowDecisionChrome(),
  DENY: () => new DenyDecisionChrome(),
  ESCALATE: () => new EscalateDecisionChrome(),
  ASK: () => new AskDecisionChrome(),
  INFORM: () => new InformDecisionChrome(),
};

/** Factory method — decision pills are constructed only here. */
export function createDecisionChrome(status: string): DecisionChrome {
  const key = status as DecisionTone;
  const product = DECISION_REGISTRY[key] ?? DECISION_REGISTRY.INFORM;
  return product();
}

export type { PlatformId, PlatformChrome };
export type { DecisionChrome, DecisionTone };
