"""
taxonomy.py — Domain knowledge for the DailyObjects Reddit social-listening system.

Everything the pipeline needs to *know* about DailyObjects, its categories, its
competitors, and the consumer themes we track lives here as data, so the
collection and classification code stays generic and the taxonomy can evolve
without touching logic. This directly encodes the brief's Phase 1 search
surface, Phase 3 theme taxonomy, and Phase 8 competitor set.

All classification here is transparent and rule/lexicon based on purpose: the
system must be re-runnable every month and produce the *same* labels for the
same text (Phase 24). Lexicon labels are a first pass — `classification_confidence`
and `research_notes` are populated so a human or LLM reviewer can audit and
override low-confidence rows before they feed business decisions.
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# BRAND MATCHING  (Agent 1 — is this mention actually about DailyObjects?)
# --------------------------------------------------------------------------
# Ordered specific -> generic. "daily objects" (two words) is noisy, so the
# collector requires a nearby product/brand token when only the loose form
# matches (handled in classify.py).
BRAND_TERMS_STRICT = [
    "dailyobjects",
    "dailyobjects.com",
    "daily objects",
]

# --------------------------------------------------------------------------
# SEARCH SURFACE  (Agent 1 — Discovery)
# --------------------------------------------------------------------------
# Query strings fanned out across Reddit search. Kept close to the brief so
# coverage is auditable. The collector runs each of these across several sort
# orders (relevance / new / top / comments) and time filters.
SEARCH_QUERIES = [
    "DailyObjects", "Daily Objects", "dailyobjects.com",
    "DailyObjects review", "DailyObjects worth it", "DailyObjects quality",
    "DailyObjects customer service", "DailyObjects return", "DailyObjects refund",
    "DailyObjects warranty", "DailyObjects delivery", "DailyObjects scam",
    "DailyObjects alternatives", "DailyObjects vs",
    "DailyObjects phone case", "DailyObjects iPhone case",
    "DailyObjects bags", "DailyObjects backpack", "DailyObjects tote bag",
    "DailyObjects crossbody", "DailyObjects sling",
    "DailyObjects power bank", "DailyObjects charger", "DailyObjects wireless charger",
    "DailyObjects cable", "DailyObjects adapter",
    "DailyObjects Apple Watch strap", "DailyObjects watch band",
    "DailyObjects laptop sleeve", "DailyObjects organiser", "DailyObjects organizer",
    "DailyObjects wallet", "DailyObjects MagSafe",
]

# Communities most likely to host DailyObjects conversation. The collector also
# runs site-wide search (not restricted to these), so the list is a *booster*
# for targeted subreddit search, not a fence (brief: "Do not restrict yourself
# to a predetermined subreddit list").
SEED_SUBREDDITS = [
    # India general / city / shopping / deals
    "india", "IndianStreetBets", "indianstreetwear", "IndiaTech",
    "bangalore", "mumbai", "delhi", "pune", "hyderabad",
    "IndiaInvestments", "DesiMenFashion", "AbroadLifestyleIndia",
    "IndianFashionAddicts", "IndianSkincareAddicts", "IndianGaming",
    "unitedstatesofindia", "developersIndia", "indiadiscussion",
    # Tech / Apple / Android / accessories
    "apple", "iphone", "android", "smartphones", "gadgets",
    "AndroidQuestions", "applewatch", "AppleWatch", "MagSafe",
    "batteries", "UsbCHardware", "onexindia", "oneplus",
    # Bags / EDC / fashion / travel
    "onebag", "ManyBaggers", "backpacks", "EDC", "frugalmalefashion",
    "handbags", "travel", "manbags",
]

# --------------------------------------------------------------------------
# PRODUCT CATEGORIES  (Phase 3 / Phase 7)
# --------------------------------------------------------------------------
# Maps a canonical category -> keyword patterns found in Reddit text.
# Order matters: first match wins in classify.categorize().
CATEGORY_KEYWORDS = {
    "Phone Cases": [
        "phone case", "iphone case", "case for", "back cover", "bumper case",
        "clear case", "leather case", "magsafe case", "silicone case", "phone cover",
    ],
    "MagSafe & Mounts": ["magsafe", "mag safe", "car mount", "phone stand", "magnetic mount"],
    "Power Banks": ["power bank", "powerbank", "portable charger", "battery pack"],
    "Wireless Chargers": ["wireless charger", "wireless charging", "charging pad", "qi charger", "3-in-1 charger"],
    "Charging Accessories": ["charger", "gan charger", "wall charger", "adapter", "brick", "fast charging"],
    "Cables": ["cable", "usb-c", "usb c", "lightning cable", "braided cable", "type c cable"],
    "Apple Watch Straps": ["apple watch strap", "watch strap", "watch band", "watch loop"],
    "Laptop Sleeves": ["laptop sleeve", "macbook sleeve", "laptop bag", "sleeve for"],
    "Backpacks": ["backpack", "rucksack", "back pack"],
    "Tote Bags": ["tote", "tote bag"],
    "Crossbody & Slings": ["crossbody", "cross body", "sling", "sling bag"],
    "Wallets": ["wallet", "card holder", "cardholder"],
    "Tech Organisers": ["organiser", "organizer", "cable organiser", "tech kit", "gadget organizer", "pouch"],
    "Desk & Accessories": ["mouse pad", "deskpad", "desk mat", "coaster", "keyboard"],
    "Apparel & Other": ["t-shirt", "tshirt", "apparel", "notebook", "diary"],
}

# --------------------------------------------------------------------------
# COMPETITORS  (Phase 8) — seed list; new names should be appended as the data
# reveals them. `aliases` catches spelling variants.
# --------------------------------------------------------------------------
COMPETITORS = {
    "Spigen": ["spigen"],
    "ESR": ["esr"],
    "Ringke": ["ringke"],
    "Caseology": ["caseology"],
    "Casetify": ["casetify", "case-tify"],
    "Apple": ["apple case", "apple silicone", "apple finewoven", "apple leather"],
    "Anker": ["anker", "soundcore"],
    "Belkin": ["belkin"],
    "UGREEN": ["ugreen", "u green"],
    "Stuffcool": ["stuffcool", "stuff cool"],
    "Ambrane": ["ambrane"],
    "Mokobara": ["mokobara"],
    "Uppercase": ["uppercase"],
    "Mivi": ["mivi"],
    "boAt": ["boat lifestyle", "boat "],
    "Portronics": ["portronics"],
    "Wildcraft": ["wildcraft"],
    "American Tourister": ["american tourister"],
    "Skybags": ["skybags"],
    "Nillkin": ["nillkin"],
    "Torras": ["torras"],
    "AliExpress/Generic": ["aliexpress", "ali express", "amazon basics", "local brand", "generic case"],
}

# --------------------------------------------------------------------------
# THEME TAXONOMY  (Phase 3) — primary theme -> {sub-themes, trigger keywords}
# Used to assign primary_theme / secondary_theme.
# --------------------------------------------------------------------------
THEME_TAXONOMY = {
    "Product — Design & Aesthetics": {
        "definition": "Look, colours, minimalism, uniqueness of the product's appearance.",
        "subthemes": ["Design", "Aesthetics", "Finish", "Originality", "Customisation"],
        "keywords": ["design", "aesthetic", "looks", "colour", "color", "minimal", "premium look",
                     "beautiful", "gorgeous", "customis", "customiz", "print", "sleek", "classy"],
    },
    "Product — Material & Build": {
        "definition": "Material grade, build quality, fit and finish of the physical product.",
        "subthemes": ["Material quality", "Fit", "Finish", "Build"],
        "keywords": ["material", "leather", "silicone", "build quality", "feels", "cheap plastic",
                     "flimsy", "sturdy", "solid", "fit", "stitching", "vegan leather", "pu leather"],
    },
    "Product — Durability & Reliability": {
        "definition": "How well the product lasts and keeps working over time.",
        "subthemes": ["Durability", "Reliability", "Protection", "Product failure", "Longevity"],
        "keywords": ["durab", "lasted", "wore off", "peel", "peeled", "flaking", "crack", "broke",
                     "stopped working", "died", "fell apart", "yellowing", "print came off",
                     "glue", "coming off", "drop protection", "protection", "warranty claim"],
    },
    "Product — Functionality & Innovation": {
        "definition": "Whether the product does its job well and offers meaningful features.",
        "subthemes": ["Functionality", "Innovation", "Compatibility", "Charging speed"],
        "keywords": ["functional", "works well", "innovat", "feature", "charging speed", "slow charging",
                     "compatib", "magsafe strength", "capacity", "mah", "overheat"],
    },
    "Value — Price & Worth": {
        "definition": "Price level and whether the product is judged worth the money.",
        "subthemes": ["Price", "Value for money", "Overpriced", "Justified premium", "Cheaper alternatives"],
        "keywords": ["price", "expensive", "overpriced", "worth it", "not worth", "value for money",
                     "too costly", "cheaper", "affordable", "rip off", "ripoff", "markup", "overcharg",
                     "for the price", "budget", "premium pricing"],
    },
    "Value — Discounts & Sales": {
        "definition": "Discounting, sale events, coupons and their effect on perception.",
        "subthemes": ["Discounts", "Sale", "Coupons"],
        "keywords": ["discount", "sale", "coupon", "offer", "deal", "% off", "cashback"],
    },
    "Brand — Trust & Perception": {
        "definition": "General trust, desirability, and what the brand stands for.",
        "subthemes": ["Trust", "Desirability", "Indian brand", "Differentiation", "Reputation"],
        "keywords": ["trust", "reputation", "indian brand", "made in india", "desi", "legit", "reliable brand",
                     "recommend", "would recommend", "brand", "hype", "overhyped", "genuine"],
    },
    "Brand — Originality vs Copy": {
        "definition": "Perception of originality vs reselling/rebranding generic products.",
        "subthemes": ["Originality", "Rebranding", "Copy"],
        "keywords": ["rebrand", "aliexpress", "white label", "whitelabel", "same as", "generic",
                     "just a", "markup", "reselling", "chinese"],
    },
    "CX — Delivery & Packaging": {
        "definition": "Shipping speed, condition on arrival, and unboxing/packaging.",
        "subthemes": ["Delivery", "Shipping", "Packaging"],
        "keywords": ["delivery", "shipping", "shipped", "arrived", "packaging", "unboxing", "late",
                     "delayed", "courier", "dispatch"],
    },
    "CX — Returns, Refunds & Warranty": {
        "definition": "Ease of return/refund and honouring of warranty/replacement.",
        "subthemes": ["Returns", "Refunds", "Warranty", "Replacement"],
        "keywords": ["return", "refund", "warranty", "replacement", "replace", "lifetime guarantee",
                     "guarantee", "exchange", "money back"],
    },
    "CX — Customer Support": {
        "definition": "Responsiveness and helpfulness of customer service.",
        "subthemes": ["Support", "Escalation", "Responsiveness"],
        "keywords": ["customer service", "customer care", "customer support", "support team", "no response",
                     "ignored", "ticket", "email", "helpline", "unresponsive", "resolved", "rude"],
    },
}

# --------------------------------------------------------------------------
# SENTIMENT LEXICON  (Phase 6 — multidimensional) — weighted terms. Values in
# [-3, +3]. This is a transparent lexicon, not a neural model; combined with
# negation handling in classify.py.
# --------------------------------------------------------------------------
POSITIVE_TERMS = {
    "love": 2, "great": 2, "excellent": 3, "amazing": 3, "awesome": 2, "best": 2,
    "premium": 1, "beautiful": 2, "gorgeous": 2, "sturdy": 2, "durable": 2, "solid": 2,
    "worth it": 2, "worth every": 2, "recommend": 2, "happy": 2, "satisfied": 2, "sleek": 1,
    "impressed": 2, "quality": 1, "good": 1, "nice": 1, "reliable": 2, "loved": 2,
    "fantastic": 3, "perfect": 3, "value for money": 2, "highly recommend": 3, "no complaints": 2,
    "held up": 2, "lasted": 1,
}
NEGATIVE_TERMS = {
    "hate": -2, "terrible": -3, "awful": -3, "worst": -3, "bad": -2, "poor": -2, "cheap": -1,
    "flimsy": -2, "overpriced": -2, "not worth": -2, "waste": -2, "scam": -3, "avoid": -2,
    "disappointed": -2, "disappointing": -2, "broke": -2, "broken": -2, "peeled": -2, "peeling": -2,
    "cracked": -2, "faded": -1, "wore off": -2, "came off": -2, "stopped working": -3, "died": -2,
    "rip off": -3, "ripoff": -3, "regret": -2, "useless": -3, "refused": -2, "no response": -2,
    "ignored": -2, "rude": -2, "defective": -2, "returned": -1, "never buy": -3, "stay away": -3,
    "yellowing": -1, "misleading": -2, "fake": -2, "delayed": -1,
}
NEGATORS = {"not", "no", "never", "isn't", "isnt", "wasn't", "wasnt", "don't", "dont",
            "didn't", "didnt", "can't", "cant", "won't", "wont", "hardly", "barely"}
INTENSIFIERS = {"very": 1.5, "really": 1.4, "extremely": 1.8, "so": 1.3, "super": 1.5,
                "absolutely": 1.6, "totally": 1.4, "quite": 1.2}

# --------------------------------------------------------------------------
# EVIDENCE STRENGTH  (Agent 3 / Phase 1) — cue phrases per class.
# --------------------------------------------------------------------------
FIRSTHAND_CUES = ["i bought", "i own", "i have been using", "i've been using", "i use", "my dailyobjects",
                  "i purchased", "i ordered", "bought this", "been using", "i got", "my case", "my bag",
                  "i had", "mine", "i returned", "i had ordered", "using it for"]
RECOMMENDATION_CUES = ["would recommend", "i recommend", "go for", "check out", "you should get",
                       "worth buying", "i suggest", "get the", "recommend"]
HEARSAY_CUES = ["i've heard", "ive heard", "apparently", "everyone says", "people say", "i heard",
                "supposedly", "seems like", "from what i", "heard that"]
COMPARISON_CUES = [" vs ", "versus", "compared to", "better than", "instead of", "over dailyobjects",
                   "rather than", "as good as"]

USER_TYPE_CUES = {
    "Repeat customer": ["always buy", "every phone", "bought again", "second one", "multiple",
                        "keep buying", "loyal", "few times"],
    "Former customer": ["used to", "no longer", "switched to", "stopped buying", "went back to"],
    "Prospective customer": ["thinking of", "should i", "planning to", "considering", "looking at",
                             "worth buying", "is it good", "any reviews"],
    "First-hand customer": FIRSTHAND_CUES,
}

# Purchase-journey stage (Phase 13) cues, checked in priority order.
JOURNEY_CUES = {
    "Discovery": ["what should i buy", "recommend a", "suggestions for", "looking for a", "which brand"],
    "Evaluation": [" vs ", "versus", "compared to", "better than", "or should i"],
    "Consideration": ["is dailyobjects good", "any good", "worth it", "should i buy", "reviews?"],
    "Conversion barrier": ["worth ₹", "worth rs", "too expensive", "that much", "justify the price"],
    "Failure": ["stopped working", "broke", "peeled", "died", "defective", "not working", "fell apart"],
    "Support": ["customer care", "customer service", "customer support", "warranty claim", "refund", "return"],
    "Advocacy": ["always recommend", "i always buy", "cannot recommend enough", "big fan", "love them"],
    "Product experience": ["been using", "using it for", "after a year", "months of use", "held up"],
}
