from __future__ import annotations

import re

from models.schemas import ExtractedRequest, Extraction, RequestType
from products.extractors.base import IntentExtractor


class HeuristicExtractor(IntentExtractor):
    def __init__(self, directory: list[dict] | None = None) -> None:
        self.directory = directory or []

    def extract(self, message: str, session=None) -> Extraction:
        text = message or ""
        lower = text.lower()
        extraction = Extraction(raw_text=text)

        for row in self.directory:
            pnr = (row.get("pnr") or "").strip()
            name = (row.get("name") or "").strip()
            if pnr and re.search(rf"\b{re.escape(pnr)}\b", text, re.I):
                extraction.mentioned_pnr = pnr.upper()
            if name and name.lower() in lower:
                extraction.mentioned_name = name

        extraction.legal_or_formal = bool(
            re.search(r"\b(legal action|lawsuit|sue|lawyer|formal complaint|file a complaint)\b", lower)
        )
        if extraction.legal_or_formal:
            extraction.requests.append(ExtractedRequest(type=RequestType.LEGAL_OR_FORMAL))

        if re.search(r"\b(furious|angry|frustrated|upset|unacceptable|ruined)\b", lower):
            extraction.emotion = "angry" if re.search(r"furious|angry|unacceptable", lower) else "frustrated"
        elif re.search(
            r"(don'?t understand|do not understand|confus|what does that mean|not sure what"
            r"|no ?one told me|nobody told me|makes no sense|what happened)",
            lower,
        ):
            extraction.emotion = "confused"

        if re.search(r"business(?:-|\s)?class|free upgrade|upgrade", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.BUSINESS_UPGRADE))

        if re.search(r"full\s+night|whole night|entire night", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.HOTEL_FULL_NIGHT))
        elif re.search(r"\bhotel\b|accommodation", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.HOTEL_DELAYED_HOURS))

        fare = None
        fare_match = re.search(
            r"(?:₹|rs\.?|inr)\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)|([0-9]{1,3}(?:,[0-9]{3})+)\s*(?:rupees|more)",
            lower,
        )
        if fare_match:
            raw = fare_match.group(1) or fare_match.group(2)
            fare = int(raw.replace(",", ""))
        if re.search(r"fare difference|higher[- ]fare|different(?:\s+\w+)? flight|move me|another flight|waive", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.HIGHER_FARE_REBOOK, fare_difference_inr=fare))

        if re.search(r"different payment|another (?:card|account)|other payment method", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.REFUND_OTHER_METHOD))
        elif re.search(r"\brefund\b|cash back|money back", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.REFUND_ORIGINAL))

        if re.search(r"\brebook\b|another seat|next (?:available )?flight", lower) and not any(
            r.type == RequestType.HIGHER_FARE_REBOOK for r in extraction.requests
        ):
            extraction.requests.append(ExtractedRequest(type=RequestType.REBOOK_24H))

        if re.search(r"lounge", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.LOUNGE))
        if re.search(r"meal voucher|meal", lower):
            extraction.requests.append(ExtractedRequest(type=RequestType.MEAL_VOUCHER))

        if re.search(r"status|what happened|my flight|cancelled|delayed|where's my", lower) and not extraction.requests:
            extraction.requests.append(ExtractedRequest(type=RequestType.STATUS))

        if not extraction.requests:
            extraction.requests.append(ExtractedRequest(type=RequestType.GENERAL_HELP))

        return extraction
