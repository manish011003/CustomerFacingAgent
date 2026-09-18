export type DecisionTone = "ALLOW" | "DENY" | "ESCALATE" | "ASK" | "INFORM";

/** Product: visual chrome for a policy decision status. */
export abstract class DecisionChrome {
  abstract readonly status: DecisionTone;
  abstract readonly label: string;
  abstract readonly pill: string;
  abstract readonly row: string;
}

export class AllowDecisionChrome extends DecisionChrome {
  readonly status = "ALLOW" as const;
  readonly label = "Allowed";
  readonly pill = "bg-emerald-50 text-emerald-700 border-emerald-100";
  readonly row = "bg-white";
}

export class DenyDecisionChrome extends DecisionChrome {
  readonly status = "DENY" as const;
  readonly label = "Denied";
  readonly pill = "bg-rose-50 text-rose-600 border-rose-100";
  readonly row = "bg-white";
}

export class EscalateDecisionChrome extends DecisionChrome {
  readonly status = "ESCALATE" as const;
  readonly label = "Supervisor";
  readonly pill = "bg-amber-50 text-amber-700 border-amber-100";
  readonly row = "bg-white";
}

export class AskDecisionChrome extends DecisionChrome {
  readonly status = "ASK" as const;
  readonly label = "Choose";
  readonly pill = "bg-sky-50 text-sky-700 border-sky-100";
  readonly row = "bg-white";
}

export class InformDecisionChrome extends DecisionChrome {
  readonly status = "INFORM" as const;
  readonly label = "Info";
  readonly pill = "bg-slate-50 text-slate-600 border-slate-100";
  readonly row = "bg-white";
}
