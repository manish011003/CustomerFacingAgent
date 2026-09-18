import { PlatformChrome, type Brand, type NavItem, type StepState } from "./platform";

export class ManagerCrmChrome extends PlatformChrome {
  readonly id = "manager" as const;
  readonly brand: Brand = {
    name: "AERO OPS",
    mark: "O",
    product: "Control",
    tagline: "Supervisor CRM",
    accentClass: "text-[#1d4ed8]",
  };
  readonly navItems: NavItem[] = [
    { href: "/", label: "Queue" },
    { href: "/passengers", label: "Passengers" },
    { href: "/graph", label: "Knowledge" },
    { href: "/analytics", label: "Analytics" },
  ];
  readonly steps = ["Open", "Review", "Assess", "Closed"];

  stepIndex({ identified, hasDecision, executed, escalated }: StepState) {
    if (!identified) return 0;
    if (escalated && !executed) return 1;
    if (hasDecision) return 2;
    return 3;
  }
}
