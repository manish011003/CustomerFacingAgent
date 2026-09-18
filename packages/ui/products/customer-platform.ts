import { PlatformChrome, type Brand, type NavItem, type StepState } from "./platform";

export class CustomerResolveChrome extends PlatformChrome {
  readonly id = "customer" as const;
  readonly brand: Brand = {
    name: "AERO",
    mark: "A",
    product: "Resolve",
    tagline: "Passenger disruption",
    accentClass: "text-[#ff5a5f]",
  };
  readonly navItems: NavItem[] = [
    { href: "/", label: "Resolve" },
    { href: "/account", label: "Account" },
  ];
  readonly steps = ["Account", "Options", "Action", "Done"];

  stepIndex({ identified, hasDecision, executed, escalated }: StepState) {
    if (!identified) return 0;
    if (!hasDecision) return 1;
    if (executed || escalated) return 3;
    return 2;
  }
}
