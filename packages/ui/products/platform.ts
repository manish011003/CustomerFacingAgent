export type PlatformId = "customer" | "manager";

export type NavItem = {
  href: string;
  label: string;
};

export type Brand = {
  name: string;
  mark: string;
  product: string;
  tagline: string;
  accentClass: string;
};

export type StepState = {
  identified: boolean;
  hasDecision: boolean;
  executed: boolean;
  escalated: boolean;
};

/** Product: chrome contract for a platform. Pages never import concrete platforms. */
export abstract class PlatformChrome {
  abstract readonly id: PlatformId;
  abstract readonly brand: Brand;
  abstract readonly navItems: NavItem[];
  abstract readonly steps: string[];
  abstract stepIndex(input: StepState): number;
}
