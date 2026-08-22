

import json

with open("products.json") as f:
    PRODUCTS = json.load(f)

# A simple point value for how profitable each product is.
# high = 1.0, medium = 0.6, low = 0.3
MARGIN_POINTS = {"high": 1.0, "medium": 0.6, "low": 0.3}


CONCERN_WORDS = {
    "dry skin":            ["dry", "flaky", "tight skin", "dehydrated"],
    "poor sleep":          ["sleep", "restless", "insomnia", "wind down"],
    "stress before bed":   ["stress", "anxious", "can't relax"],
    "low energy":          ["tired", "fatigue", "low energy", "sluggish"],
    "dullness":            ["dull", "uneven tone"],
}

TIME_WORDS = {
    "evening": ["evening", "night", "before bed", "wind down"],
    "morning": ["morning", "wake up", "start my day"],
}


def understand_message(message):
    """Reads the customer's message and pulls out what matters."""
    text = message.lower()

    # Which concerns did the customer mention?
    concerns_found = []
    for concern, keywords in CONCERN_WORDS.items():
        for word in keywords:
            if word in text:
                concerns_found.append(concern)
                break
    if not concerns_found:
        concerns_found = ["general wellness"]

    # Is this a morning or evening routine?
    time_of_day = "evening"  # default
    for time, keywords in TIME_WORDS.items():
        for word in keywords:
            if word in text:
                time_of_day = time
                break

    
    wants_simple = any(w in text for w in ["simple", "easy", "quick", "without making it complicated"])

    return {
        "concerns": concerns_found,
        "time_of_day": time_of_day,
        "wants_simple": wants_simple,
    }


def ask_followup_question(understanding):
    """One short, natural follow-up question - not a long survey."""
    if "dry skin" in understanding["concerns"]:
        return "Got it - is the dryness mostly on your face, or your body too?"
    return "Got it - anything you'd like this routine to avoid?"


IGNORE_WORDS = {"i", "my", "a", "an", "the", "and", "to", "for", "with", "is",
                 "in", "of", "on", "that", "this", "it", "without", "want",
                 "lately", "particularly", "well", "create", "better"}


def find_matching_products(understanding, message):
    customer_words = set(message.lower().replace(",", "").replace(".", "").split()) - IGNORE_WORDS

    matches = []
    for product in PRODUCTS:
        product_text = " ".join([
            product["name"], product["description"],
            " ".join(product["benefits"]), " ".join(product["concerns_addressed"]),
        ]).lower().replace(",", "")
        product_words = set(product_text.split()) - IGNORE_WORDS

        shared_words = customer_words & product_words
        relevance = len(shared_words)

        # small bonus if it's meant for the right time of day
        if product["usage_time"] == understanding["time_of_day"]:
            relevance += 1

        
        matches.append((product, relevance))

    matches.sort(key=lambda pair: pair[1], reverse=True)
    return matches


def score_products(matches, fair=True):
    """
    fair=True  -> what we actually ship. Mostly based on relevance;
                  margin only nudges the order slightly (a tiebreaker).
    fair=False -> the BAD version, shown only for comparison, where
                  margin matters more than relevance. This is the
                  mistake the case study asks us to avoid.
    """
    scored = []
    for product, relevance in matches:
        margin = MARGIN_POINTS[product["margin_tier"]]
        if fair:
            score = (relevance * 0.85) + (margin * 0.15)
        else:
            score = (relevance * 0.2) + (margin * 0.8)
        scored.append((product, relevance, margin, score))

    scored.sort(key=lambda row: row[3], reverse=True)
    return scored


def build_ritual(scored_products, understanding):
    """Pick a small, non-repetitive set of products for the routine."""
    max_items = 2 if understanding["wants_simple"] else 3
    ritual = []
    used_types = set()

    for product, relevance, margin, score in scored_products:
        if product["subcategory"] in used_types:
            continue  # skip if we already picked this type of product
        ritual.append((product, relevance, margin, score))
        used_types.add(product["subcategory"])
        if len(ritual) == max_items:
            break

    return ritual


def explain_product(product, understanding):
    matching_concerns = [c for c in understanding["concerns"] if c in product["concerns_addressed"]]
    concern = matching_concerns[0] if matching_concerns else understanding["concerns"][0]
    ingredient = product["hero_ingredients"][0]
    benefit = product["benefits"][0]
    if benefit.lower().startswith("supports "):
        benefit = benefit[len("supports "):]  # avoid saying "supports supports..."

    return (f"{product['name']} - recommended for \"{concern}\" because of "
            f"{ingredient}, which supports {benefit}. "
            f"(A wellness suggestion, not a medical claim.)")


# PUTTING IT ALL TOGETHER 

def run_example(message):
    print("=" * 70)
    print("CUSTOMER SAYS:", message)
    print("=" * 70)

    # In this we Understanding costomer problem
    understanding = understand_message(message)
    print("\nSTEP 1 - Understand the Customer Problem:")
    print("  Concerns:", understanding["concerns"])
    print("  Time of day:", understanding["time_of_day"])
    print("  Wants a simple routine?", understanding["wants_simple"])
    print("  Follow-up question:", ask_followup_question(understanding))

    # in this step we Retrieving the matching product
    matches = find_matching_products(understanding, message)
    print(f"\nSTEP 2 - All products, ranked by relevance ({len(matches)} total):")
    for product, relevance in matches:
        print(f"  {product['name']} (relevance={relevance})")

    # we  Recommend the product from our database
    fair_scores = score_products(matches, fair=True)
    ritual = build_ritual(fair_scores, understanding)
    print("\nSTEP 3 - Recommended routine and product (fair scoring):")
    for product, relevance, margin, score in ritual:
        print(f"  -> {product['name']}  (${product['price']}, score={round(score, 2)})")

    # from step we Explain why we suggest this product
    print("\nSTEP 4 - Why we picked these:")
    for product, relevance, margin, score in ritual:
        print("  " + explain_product(product, understanding))

    # show what would happen if we optimized for profit instead
    unfair_scores = score_products(matches, fair=False)
    unfair_ritual = build_ritual(unfair_scores, understanding)
    print("\nCOMPARISON - what a profit-first system would recommend instead:")
    for product, relevance, margin, score in unfair_ritual:
        print(f"  -> {product['name']}  (${product['price']}, relevance={relevance}, score={round(score, 2)})")
    print("This is why we DON'T let margin drive recommendations -")
    print("it can push irrelevant, expensive products to the top.\n")


if __name__ == "__main__":
    run_example(
        "My skin feels dry lately, I'm not sleeping particularly well, "
        "and I want to create a better evening routine without making it complicated."
    )

    run_example(
        "I wake up feeling sluggish and my skin looks dull, "
        "need something simple to start the day."
    )
