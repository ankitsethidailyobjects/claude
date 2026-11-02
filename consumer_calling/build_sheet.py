"""Build the Brand & Creative consumer-calling workbook (Nov-26 round).

Source: "DailyObjects Brand & Creative — Customer Questionnaire" (Google Doc),
the earlier questionnaire sheet (format), and Sheena Denmead's canvas-range
questions (email, 28-Oct-26).

Run: python3 build_sheet.py <out.xlsx>
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

NAVY = "1F2A44"
SECTION = "E8ECF4"
CANVAS_FILL = "F3EBDD"
YELLOW = "FFF2CC"
thin = Side(style="thin", color="D0D5DD")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
BASE = Font(name="Arial", size=10)
WRAP = Alignment(wrap_text=True, vertical="top")


def header(ws, cols, widths):
    ws.append(cols)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
        c = ws.cell(row=1, column=i)
        c.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDER
    ws.freeze_panes = "A2"


def row(ws, values, fill=None, bold=False):
    ws.append(values)
    r = ws.max_row
    for i in range(1, ws.max_column + 1):
        c = ws.cell(row=r, column=i)
        c.font = Font(name="Arial", size=10, bold=bold)
        c.alignment = WRAP
        c.border = BORDER
        if fill:
            c.fill = PatternFill("solid", fgColor=fill)


def section(ws, text, fill=SECTION):
    row(ws, [text] + [None] * (ws.max_column - 1), fill=fill, bold=True)
    ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=ws.max_column)


# ---------------------------------------------------------------- questions
# (q, probe, area, ask_to, listen, source)
MASTER = [
    ("Section 1 · Warm-up: the person and their everyday things · Context about routines and the objects in them, before the conversation turns to DailyObjects", [
        ("Hi, I'm [name] from the brand and creative team at DailyObjects. Thank you for making the time. We're speaking with customers to understand how they see DailyObjects, in their own words. There are no right or wrong answers, and hearing what doesn't work for you is as useful to us as hearing what does. Is it alright if I take notes while we talk?",
         "—", "—", "All", "Consent to notes; set tone. Make clear that critical views are welcome.", "Doc"),
        ("Tell me a bit about yourself: what you do, and what a typical weekday looks like.",
         "Where do you spend most of your day?", "A1", "All", "Life stage, work setting, commute; context for personas and shoot settings.", "Doc"),
        ("Walk me through the things you carry with you on a normal day.",
         "Which of those do you use most often? How long have you had them?", "A1", "All", "Everyday carry, devices, Apple or other ecosystem; where our products sit in the kit.", "Doc"),
        ("Tell me about the space where you spend most of your working or study hours.",
         "What's on your desk or around you there?", "A1", "All", "Desk setup; settings for shoots.", "Doc"),
        ("Is there anything you own that you've had for a long time and still use? Tell me about it.",
         "What has kept it in use?", "A1 / A5", "All", "What durability and attachment mean to them, in their words.", "Doc"),
        ("When did you last buy something for your phone, laptop, desk or bag? What was it?",
         "Where did you buy it?", "A1 / A3", "All", "Recency and category of the last purchase; sets up Section 3.", "Doc"),
    ]),
    ("Section 2 · First encounter and history with DailyObjects · Their own timeline with the brand. Let them tell the story; don't describe the brand or its products", [
        ("How did you first come across DailyObjects?",
         "Roughly when was that? What do you remember about that first time?", "A2", "All", "First touchpoint (search, ad, creator, friend, store, marketplace) and what stuck from it.", "Doc"),
        ("What happened after that? Take me through your history with the brand up to now.",
         "Tell me more about that.", "A2", "All", "Gaps, returns, what pulled them back; whether the story is about products or the brand.", "Doc"),
        ("Have you bought from DailyObjects? If so, what, and when?",
         "Was it for yourself or someone else? Where did you buy it: website, app, a store, a marketplace?", "A2 / A5", "All", "Purchase history in their memory vs our records; gifting; channel.", "Doc"),
        ("Have there been times you considered DailyObjects and chose something else? What happened?",
         "What did you go with instead?", "A2 / A7", "All", "Lost moments and the reason in their words (price, look, trust, availability).", "Doc"),
        ("How often, if at all, does DailyObjects come up for you now: in your feed, in conversation, when shopping?",
         "Where was the last time?", "A2 / A6", "All", "Current salience and the channels it comes through.", "Doc"),
    ]),
    ("Section 3 · The category: how they shop for accessories · The decision process and the brands in play. Make clear we want to hear about every brand they use, not only ours", [
        ("When you think of buying a phone case, a bag or something for your desk, which brands come to mind first?",
         "Any others? Where do you know each of them from?", "A3 / A4", "All", "Top-of-mind recall: the order brands are named in and whether DailyObjects comes up unprompted. Note: they know we're DailyObjects, so read a mention as recall, not proof of salience.", "Doc comment (TOM recall)"),
        ("Think about the last phone case, laptop sleeve, bag or desk item you bought. Take me through how that happened, from start to finish.",
         "What prompted it? Where did you look? What did you consider, and what did you rule out? What made you settle on the one you bought?", "A3", "All", "Trigger → search → shortlist → decision; where the deciding moment happened.", "Doc"),
        ("When you're buying something in this area, what do you pay attention to?",
         "Can you give me an example?", "A3", "All", "Their own purchase criteria, unprompted and in their order.", "Doc"),
        ("Apart from DailyObjects, which brands or stores come to mind for these kinds of products?",
         "Where do you know each of them from?", "A3 / A7", "All", "Consideration set; marketplaces vs D2C brands. Use these names in Section 7.", "Doc"),
        ("How do you usually find out about new products or brands in this space?",
         "Can you think of the last time that happened?", "A3 / A6", "All", "Discovery channels: feed, creators, search, friends, stores.", "Doc"),
        ("How much do you typically spend on items like these? How do you decide what's a reasonable amount?",
         "What makes something feel worth it?", "A3", "All", "Price anchors; what 'worth it' means; sale timing.", "Doc"),
        ("Has anything you bought in this category not worked out? What happened?",
         "What did you do after that?", "A3 / A5", "All", "Failure modes in the category and what they do next.", "Doc"),
    ]),
    ("Section 4 · Unprompted brand perceptions · Their own vocabulary for the brand. Note exact words; probe each one for meaning before moving on", [
        ("When you hear the name DailyObjects, what comes to mind?",
         "Anything else? You said [word]. What do you mean by that?", "A4", "All", "Unaided associations; whether a product, a look or a feeling comes first. Capture verbatim.", "Doc"),
        ("If you were describing DailyObjects to a friend who had never heard of it, what would you say?",
         "What would you tell them they sell?", "A4", "All", "Positioning in their words; brand vs store.", "Doc"),
        ("What kinds of products do you think of when you think of DailyObjects?",
         "Anything else?", "A4", "All", "Category box: which categories they name before any prompt.", "Doc"),
        ("Who do you picture buying from DailyObjects? Describe them.",
         "How similar or different is that person to you?", "A4", "All", "Imagined customer; distance between that person and themselves.", "Doc"),
        ("What, if anything, do you think DailyObjects does differently from other brands you mentioned?",
         "Can you give me an example?", "A4 / A7", "All", "Distinctiveness in their words — or the absence of it.", "Doc"),
        ("How would you describe where DailyObjects stands, compared with the brands you know in this space?",
         "What makes you say that?", "A4 / A7", "All", "Their read of our positioning without us naming one.", "Doc comment (positioning)"),
        ("Is there anything about the brand you're unsure about or have questions about?",
         "Tell me more about that.", "A4", "All", "Doubts and trust gaps.", "Doc"),
        ("Has your view of DailyObjects changed over the time you've known it? If so, how, and what led to that?",
         "When did you notice that?", "A4", "All", "Direction of change and what caused it (product, price, ads, service).", "Doc"),
    ]),
    ("Section 5 · Products and the ownership experience · What living with the product has been like. For non-buyers, ask about products they've seen or that people around them own", [
        ("Tell me about the DailyObjects product you've used the most. How does it fit into your day?",
         "Where and when do you use it?", "A5", "Buyers (non-buyers: products they've seen)", "Role in the day; settings and occasions.", "Doc"),
        ("Think back to when it arrived. What do you remember about receiving and opening it?",
         "What did you notice first?", "A5", "Buyers", "Unboxing and first impression; packaging recall.", "Doc"),
        ("How has it held up since then?",
         "What, if anything, has changed about it?", "A5", "Buyers", "Wear in their words (peel, fade, tear, softening) vs holding up.", "Doc"),
        ("How does it compare with what you'd expected when you ordered it?",
         "What, if anything, was different from what you'd expected?", "A5 / A6", "Buyers", "Promise-vs-reality gaps: 'thinner', 'shinier', 'smaller', colour.", "Doc"),
        ("Has anyone else noticed it or asked about it? What did they say?",
         "What did you tell them?", "A5", "Buyers", "Social visibility and word of mouth.", "Doc"),
        ("If you've bought more than once, what led you back? If you haven't, what has happened since the first purchase?",
         "Tell me more about that.", "A5 / A2", "Buyers", "Brand pull vs offer pull for repeat.", "Doc"),
        ("Have you had any reason to contact DailyObjects (a delivery, a return, a question)? How did that go?",
         "What happened next?", "A5", "Buyers", "Service moments that shape perception. Pass complaints to support after the call.", "Doc"),
        ("If it stopped working tomorrow, what would you do?",
         "Where would you look?", "A5 / A7", "Buyers", "Replace with DailyObjects or switch; who they'd switch to.", "Doc"),
    ]),
    ("Section 6 · Creative they've noticed: ads, social, website, packaging · Unaided recall. Don't show anything; let them describe what they remember, including what they've forgotten", [
        ("Have you seen anything from DailyObjects in the last few months: posts, ads, emails, anything else? Tell me about what you remember.",
         "Where did you see it? What was in it? What did you take from it?", "A6", "All", "Unaided creative recall: format, people, product, platform.", "Doc"),
        ("What do you think about what you've seen from DailyObjects?",
         "What makes you say that?", "A6", "All", "Their own judgement of the creative, without us supplying a frame.", "Doc comment (creatives)"),
        ("What did you do, if anything, after seeing it?",
         "Tell me more about that.", "A6", "All", "Action taken: clicked, searched, saved, ignored.", "Doc"),
        ("Do you follow DailyObjects anywhere (Instagram, YouTube, email, the app)? What do you notice about what they post there?",
         "Can you give me an example?", "A6", "All", "Owned-channel reach and what it signals.", "Doc"),
        ("Think about the DailyObjects website or app. Describe what it's like to browse it.",
         "What do you look at on a product page?", "A6", "All", "What convinces them on a page: photos, video, reviews, details.", "Doc"),
        ("Think about the packaging your order came in. What do you remember about it?",
         "Anything else?", "A6 / A5", "Buyers", "Packaging recall and what it signals.", "Doc"),
        ("If you saw a DailyObjects post in your feed without the logo on it, how, if at all, would you know it was theirs?",
         "What would give it away?", "A6 / A4", "All", "Distinctive brand assets — or none.", "Doc"),
        ("Is there any piece of DailyObjects content you've shared, saved or talked about with someone? What was it?",
         "What made you do that?", "A6", "All", "Shareable content and why.", "Doc"),
        ("How does what you've seen from DailyObjects compare with what you see from other brands in your feed?",
         "Which brands are you thinking of?", "A6 / A7", "All", "Creative benchmark brands in their feed.", "Doc"),
    ]),
    ("Section 7 · DailyObjects relative to other brands · Their own map of the space. Use the brands they named in Section 3; don't introduce new ones", [
        ("Earlier you mentioned [brands]. Where does DailyObjects sit among those for you?",
         "What puts it there?", "A7", "All", "Their positioning map and the axes they use (price, design, quality, trust).", "Doc"),
        ("In what situations would you choose DailyObjects over those? In what situations would you choose one of those instead?",
         "Can you give me an example?", "A7", "All", "Occasions where we win and lose.", "Doc"),
        ("What would you say each of those brands is known for? And DailyObjects?",
         "Anything else?", "A7 / A4", "All", "What we're known for vs competitors.", "Doc"),
        ("If DailyObjects no longer existed, what would you use instead? What, if anything, would be different?",
         "What would you miss, if anything?", "A7", "All", "Substitutes and the irreplaceable part of the brand.", "Doc"),
    ]),
    ("Section 8 · Projective exercises · Indirect routes to perceptions people find hard to state. Frame as quick and imaginative; the explanation behind each answer matters more than the answer", [
        ("If DailyObjects were a person, describe them: their age, what they do, where they live, how they spend a weekend.",
         "What about the brand makes you picture them that way?", "A4", "All", "Brand personality; compare with the customer they pictured in Section 4.", "Doc"),
        ("If DailyObjects were a place in your city, what kind of place would it be? Why?",
         "What about it fits?", "A4", "All", "Price tier and mood signals.", "Doc"),
        ("Imagine DailyObjects walked into a room of other brands. Who would it go and talk to? Who would it avoid?",
         "What makes you say that?", "A4 / A7", "All", "Peer set and anti-set.", "Doc"),
        ("Complete these sentences however you like: \"DailyObjects is for people who…\" · \"DailyObjects is not for people who…\" · \"The thing I'd tell DailyObjects is…\"",
         "Tell me more about that.", "A4", "All", "Inclusion/exclusion; direct advice. Capture verbatim.", "Doc"),
        ("If you had to sum up DailyObjects in three words, what would they be?",
         "Talk me through each one.", "A4", "All", "Customer-language bank for hooks and headlines.", "Doc"),
    ]),
    ("Section 9 · Close", [
        ("Looking back over our conversation, is there anything you said that you'd like to add to or change?", "—", "—", "All", "Second thoughts are often the most honest answer.", "Doc"),
        ("Is there anything about DailyObjects we haven't talked about that you think matters?", "—", "All areas", "All", "Topics we didn't plan for.", "Doc"),
        ("Is there anything you'd like to ask us?", "—", "—", "All", "Note questions for follow-up.", "Doc"),
        ("What, if anything, did you think about differently during this conversation?", "—", "A4", "All", "Shifts in view during the call.", "Doc"),
    ]),
]

INSIGHTS = [
    ("A1", "The person and their everyday carry", "Doc §1",
     "Who they are, their weekday, what they carry, their desk, the long-lasting things they own — before the brand comes up.",
     "Personas and shoot settings in the current creative strategy are assumptions. 77.5% of customers have an Apple signal and Apple-only customers repeat at 22% vs 12% for non-Apple, so the ecosystem and kit people carry is likely central to how our products fit. Starting here also anchors later answers in real objects rather than opinions.",
     "Persona refresh; lifestyle settings and casting for shoots; which objects to style our products alongside.",
     "Routine, commute, devices, desk setup, what 'lasting' means to them."),
    ("A2", "First encounter and history with the brand", "Doc §2",
     "How DailyObjects entered their life and their timeline with it since: first touch, purchases, near-misses, current salience.",
     "53% of last-12-month orders are first orders and only 27% of a year's new customers return within 12 months. New-customer orders come from Google Ads 38%, Direct 21%, Meta 20%, Organic 16%. Their own story tells us which touchpoints are remembered, which are not, and where the relationship stalls after order one.",
     "Where brand-building money and creative should go across the journey; post-purchase CRM moments.",
     "First-touch story, gaps between orders, times they chose someone else and why."),
    ("A3", "How they shop the category", "Doc §3 (+ TOM recall from doc comment)",
     "The decision process for accessories, the criteria they use, the brands in their consideration set, and what 'reasonable price' means.",
     "Around half of orders fall in sale weeks and 58–70% carry a discount; 22% of customers buy only on sale days. Understanding the category process without DailyObjects in the frame shows whether we lose on price, discovery or trust — and which brands are top of mind (added from the doc comment on TOM recall).",
     "Category entry points to own in creative; price and offer communication; search vs social investment.",
     "Brands named first, triggers, where they look, what they rule out, price anchors."),
    ("A4", "Unprompted brand perception", "Doc §4 and §8 (+ positioning from doc comment)",
     "What DailyObjects means in their own vocabulary, who they think it's for, what's different about it, and how that has changed.",
     "Branded search clicks fell ~11% (Oct-25–Mar-26 vs Apr–Oct-26). 45% of first orders contain a phone case and case or strap entrants mostly stay in one category, which suggests people may know a product or a store rather than a brand. Projectives (§8) give an indirect read where direct answers are thin.",
     "Brand positioning line; which categories the brand story leads with; brand-vs-performance spend case.",
     "Exact words, categories named unprompted, imagined customer, brand-as-person, three words."),
    ("A5", "Products and the ownership experience", "Doc §5",
     "What living with the product is like: arrival, how it holds up, expectation vs reality, social notice, service, repeat.",
     "In written reviews since Oct-25, 28% mention quality and 21% design or looks. Top complaints: doesn't work (377), damaged on arrival (305), wears out — peel, fade, tear (288), material/finish (282), not as pictured (112). Site shows ~4.6★ vs a true 3.88★. Calls tell us the story behind those numbers.",
     "Claims we can and cannot make; product-quality feedback to category teams; imagery that shows wear honestly.",
     "Gap words ('thinner', 'faded', 'softer'), what held up, who noticed, what they'd do if it broke."),
    ("A6", "Creative recall and recognisability", "Doc §6 (+ 'what do you think of the creatives' from doc comment)",
     "What they remember from our ads, social, site and packaging, unaided; what they did after; whether our content is recognisable without the logo.",
     "After HPS, catalogue (DPA) ads rose from 34% to 49% of weekly Meta spend; influencer video drew 27% of spend and 31% of revenue. Creator/UGC is the best format at every funnel stage in the creative strategy deck. We need to know what actually lodges in memory and whether we have distinctive assets.",
     "Mix of creator vs studio vs catalogue creative; hook rules; distinctive brand assets to build.",
     "Unaided recall, format and platform, action taken, 'how would you know it's them', benchmark brands."),
    ("A7", "Position relative to other brands", "Doc §7",
     "Where DailyObjects sits on their own map of the brands they named, when they pick us vs others, and what they'd use if we disappeared.",
     "Customers compare us with the brands they actually use, not the ones we benchmark against. Using only brands they named keeps the map theirs and avoids leading.",
     "Competitive positioning; occasions to target; what to defend.",
     "Axes they use (price, design, quality, trust), win/lose situations, substitutes."),
    ("A8", "Canvas range: what customers value in the material", "Canvas Questionnaire tab (Sheena's questions, 28-Oct-26)",
     "What canvas-range buyers like about the material — functional and aesthetic — and whether the appeal is the natural cotton or the look of canvas.",
     "Sheena (makeitbetterco) says we already know the complaints: colour fading, colour bleeding and going soft over time. The open question is what makes the range appealing, so we keep that and fix quality. A poly-cotton blend or synthetic canvas would solve durability; this tells us whether customers would still want it if it looked the same.",
     "Material decision for the canvas range (natural cotton vs blend vs synthetic); what the range's creative and PDP copy should lead with.",
     "Whether they mention cotton/natural unprompted, touch and feel words, look words, versatility (work to weekend), how it has aged, reaction to 'same look, different material'."),
]

COHORTS = [
    ("First-time (NTP)", "One delivered order in the last 60 days; no earlier order.", 10,
     "Fresh first impression and discovery story.",
     "What made you decide to try DailyObjects this time?\nWhat, if anything, almost stopped you?\nBefore this order, what had you seen or heard about DailyObjects?",
     "Master Question List"),
    ("ATC — added to cart, did not buy", "Added to cart in the last 30 days, no order in that window (MoEngage / GA4 cart list). Mix of never-bought and past buyers.", 10,
     "What our creative and pages promise that isn't enough to buy.",
     "Tell me what happened after you added it to the cart.\nWhat was on your mind when you left it there?\nWhere did you end up getting something like it, if at all? How did that go?",
     "Master Question List (skip §5 for never-bought)"),
    ("Second-time (O2)", "Exactly 2 orders, second in the last 90 days.", 10,
     "What brought them back — brand pull or offer.",
     "What brought you back to DailyObjects the second time?\nHow was the second purchase different from the first?\nBetween the two orders, where did you see or hear from DailyObjects?",
     "Master Question List"),
    ("Power / O3+", "3+ orders, latest in the last 120 days.", 10,
     "Deep brand meaning, rotation, advocacy.",
     "How has your view of DailyObjects changed since your first order?\nWhich DailyObjects products do you own? Tell me how you use them.\nWhat do you look for each time you come back?",
     "Master Question List"),
    ("Lapsed", "2+ orders in the past but none in the last 12 months.", 8,
     "What faded, and where they went instead.",
     "Since your last order, how have you been buying things like these?\nWhat, if anything, has changed for you — or for DailyObjects?\nWhen did you last see or hear anything from DailyObjects? What was it?",
     "Master Question List"),
    ("Canvas range buyers", "Delivered order with a canvas-range product (Pedal Backpack, Commute Messenger Bag and the rest of the canvas line) in the last 6 months, delivered at least 3 weeks ago. Prioritise loyal customers: 2+ DailyObjects orders or 2+ canvas pieces.", 12,
     "Sheena's brief: what customers love about the canvas material, so we keep it while fixing fading, bleeding and softening. 3+ weeks of use means they can talk about how it has held up; 6 months keeps the purchase fresh.",
     "Use the Canvas Questionnaire tab (it has its own add-on section).",
     "Canvas Questionnaire"),
]

QUOTAS = [
    ("Category of last order", "Spread across Phone Cases, Charging, Bags, Watch Bands, Desk / Organisers — at least 2 per cohort outside Phone Cases."),
    ("Device", "About 3 in 4 Apple users, 1 in 4 Android — mirrors the base (77.5% Apple signal)."),
    ("Price behaviour", "At least 3 per cohort who bought only on sale days and 3 who bought at least once at full price."),
    ("Canvas: product mix", "At least 4 Pedal Backpack and 4 Commute Messenger Bag owners; the rest across other canvas pieces."),
    ("Canvas: time owned", "About half delivered 3–8 weeks ago, half 2–6 months ago, so we hear both first impressions and how the material has aged."),
    ("Canvas: loyalty", "At least half with 2+ DailyObjects orders or 2+ canvas pieces (Sheena asked for loyal customers). Include 2–3 who reviewed a canvas piece, any rating."),
    ("Geography", "Mix of Top-8 metros and Tier 2; Delhi NCR customers can be invited to the office in person (useful for canvas: they can bring the bag)."),
    ("Incentive", "Free phone case or store credit, given after the call so it doesn't bias answers."),
]

CANVAS = [
    ("Section 1 · Warm-up (3 min) · Same opening as the main script; keep it short", [
        ("Hi, I'm [name] from DailyObjects. Thank you for making the time. We're speaking with a few customers to understand, in their own words, how they use the things they've bought from us. There are no right or wrong answers, and hearing what doesn't work for you is as useful as hearing what does. Is it alright if I take notes while we talk?",
         "—", "—", "All", "Consent to notes; set tone. Don't say the call is about canvas or material yet.", "Main §1"),
        ("Tell me a bit about yourself: what you do, and what a typical weekday looks like.",
         "Where do you spend most of your day? How do you get around?", "A1", "All", "Commute mode, work setting, dress code — context for how a bag is used.", "Main §1"),
        ("Walk me through what you carry with you on a normal day, and what you carry it in.",
         "Do you use the same bag every day, or switch?", "A1 / A8", "All", "Whether the canvas bag is their everyday bag or one of several; rotation.", "Main §1 (adapted)"),
    ]),
    ("Section 2 · The bag and how it came into their life (5 min) · Purchase story for the canvas piece", [
        ("Tell me about the [Pedal Backpack / Commute Messenger Bag] you bought from us. How did you come to buy it?",
         "Where did you first see it? What else were you looking at?", "A2 / A8", "All", "Discovery path; alternatives considered (other bags, other materials).", "New"),
        ("When you first saw it, what caught your attention?",
         "Anything else? You said [word]. What do you mean by that?", "A8", "All", "First attraction in their words: look, colour, shape, material, price, function. Note if material comes up unprompted.", "New"),
        ("What made you settle on this one?",
         "What did you rule out, and why?", "A3 / A8", "All", "Deciding factor; whether material played a role in the decision.", "New"),
        ("How does it compare with what you'd pictured when you ordered it?",
         "What, if anything, was different?", "A5 / A8", "All", "Promise vs reality on colour, texture, weight, stiffness.", "Main §5"),
    ]),
    ("Section 3 · Living with the bag (6 min) · Where and how it's used; how it has changed", [
        ("Take me through the last few times you used it. Where were you going?",
         "What else do you take it to?", "A8", "All", "Occasions: office, college, weekend, travel. Listen for 'works for both' (versatility) without asking for it.", "Sheena Q2 (setup)"),
        ("Are there places or occasions you would or wouldn't take it to?",
         "What makes it right or not right for those?", "A8", "All", "Formal vs casual range in their words — tests Sheena's 'formal enough for work, casual enough for weekend'.", "Sheena Q2"),
        ("How has it held up since you got it?",
         "What, if anything, has changed about how it looks or feels?", "A5 / A8", "All", "Unprompted mention of fading, bleeding, softening — and whether they mind. Some may like a worn-in look: note it.", "New"),
        ("How do you look after it, if at all?",
         "Have you ever washed it or cleaned it? What happened?", "A8", "All", "Care behaviour; where colour bleed happens.", "New"),
        ("Has anyone noticed it or asked about it? What did they say?",
         "What did you tell them?", "A5 / A8", "All", "How others describe it — social proof language.", "Main §5"),
    ]),
    ("Section 4 · The material (8 min) · CORE SECTION — Sheena's questions. Do not say 'cotton', 'natural', 'canvas' or any property until they do", [
        ("How would you describe your bag to someone who hasn't seen it?",
         "Anything else?", "A8", "All", "Whether they lead with material, look, colour or function. Capture exact words.", "Sheena Q1 (warm-up)"),
        ("Tell me about the material it's made of.",
         "What do you know about it? Where did you learn that?", "A8", "All", "Do they know it's cotton canvas? Do they say 'canvas', 'cotton', 'natural', 'fabric'? Their knowledge, unprompted.", "Sheena Q1"),
        ("What stands out to you about the material?",
         "You said [word]. What do you mean by that? Can you give me an example?", "A8", "All", "The properties they value, functional or aesthetic, in their order and words. Don't offer examples.", "Sheena Q2"),
        ("When you hold it or wear it, what do you notice?",
         "How would you describe the feel?", "A8", "All", "Tactile words: rough, soft, sturdy, natural, 'real', stiff. Whether feel matters as much as look.", "Sheena Q1 / Q2"),
        ("What, if anything, does the material say about the bag — or about the person carrying it?",
         "What makes you say that?", "A8 / A4", "All", "Meanings attached to the material: honest, rugged, sustainable, premium, casual.", "Sheena Q1"),
        ("If you were buying another bag, how much, if at all, would the material come into it?",
         "What would you look for?", "A8 / A3", "All", "Weight of material in future decisions.", "Sheena Q1"),
        ("Imagine a bag that looks exactly like yours but is made from a different material. What, if anything, would be different for you?",
         "What would you want to know about it? What would make it feel the same, or not?", "A8", "All", "ASK LAST in this section. The key test of natural vs look. Listen for whether 'natural'/'cotton' matters, or only the look and feel. Don't name poly-cotton or synthetic unless they ask what we mean.", "Sheena Q1"),
    ]),
    ("Section 5 · Canvas range in the brand (3 min) · Short version of main §4", [
        ("When you hear the name DailyObjects, what comes to mind?",
         "Anything else?", "A4", "All", "Whether bags/canvas come up at all; brand vs product.", "Main §4"),
        ("What kinds of products do you think of when you think of DailyObjects?",
         "Anything else?", "A4", "All", "Whether bags are in their DailyObjects box.", "Main §4"),
        ("Have you seen anything from DailyObjects about this bag or bags like it — posts, ads, the website?",
         "What do you remember about it? What did it show?", "A6 / A8", "All", "Which canvas creative is remembered; does imagery show the material?", "Main §6"),
        ("If you had to sum up this bag in three words, what would they be?",
         "Talk me through each one.", "A8", "All", "Copy bank for the canvas range.", "Main §8 (adapted)"),
    ]),
    ("Section 6 · Close (2 min)", [
        ("Is there anything about the bag or the material we haven't talked about that you think matters?", "—", "A8", "All", "Topics we didn't plan for.", "Main §9"),
        ("Is there anything you'd like to ask us?", "—", "—", "All", "Pass complaints to support after the call.", "Main §9"),
        ("If we sent you a couple of fabric samples later, would you be open to telling us what you think?", "—", "A8", "All", "Recruit for a follow-up material test (blend vs synthetic vs current). Note yes/no.", "New"),
    ]),
]


def questions_tab(ws, data, sec_fill):
    header(ws, ["Section", "Q#", "Script question (read as written)", "Neutral probe (only if the person doesn't lead)",
                "Insight area", "Ask to", "What we're listening for (interviewer note)", "Source"],
           [9, 6, 55, 42, 11, 16, 50, 18])
    for si, (title, qs) in enumerate(data, 1):
        section(ws, title, sec_fill)
        for qi, q in enumerate(qs, 1):
            row(ws, [str(si), f"{si}.{qi}", *q])


def build(path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Master Question List"
    questions_tab(ws, MASTER, SECTION)

    ws = wb.create_sheet("Insight Areas")
    header(ws, ["#", "Insight area", "Source section", "What we want to learn", "Why — reasoning and what the data says",
                "Decision it feeds", "Listen for"], [5, 26, 22, 42, 60, 36, 40])
    for r in INSIGHTS:
        row(ws, list(r), fill=CANVAS_FILL if r[0] == "A8" else None)

    ws = wb.create_sheet("Cohorts")
    header(ws, ["Cohort", "Definition (pull from warehouse / CRM)", "Calls (target)", "Why this cohort",
                "Cohort add-on questions (ask after Section 3)", "Questionnaire to use"], [26, 48, 10, 44, 52, 24])
    for r in COHORTS:
        row(ws, list(r), fill=CANVAS_FILL if r[0].startswith("Canvas") else None)
        ws.cell(row=ws.max_row, column=3).fill = PatternFill("solid", fgColor=YELLOW)
    n = len(COHORTS)
    row(ws, ["Total calls", None, f"=SUM(C2:C{n + 1})", None, None, None], bold=True)
    ws.append([])
    section(ws, "Quotas within each cohort (aim for, not strict)")
    for k, v in QUOTAS:
        row(ws, [k, v, None, None, None, None])
    ws.append([])
    ws.append(["Yellow cells (call targets) are inputs — edit them and the total updates."])
    ws.cell(row=ws.max_row, column=1).font = Font(name="Arial", size=9, italic=True)

    ws = wb.create_sheet("Canvas Questionnaire")
    questions_tab(ws, CANVAS, CANVAS_FILL)
    ws.append([])
    ws.append(["Sheena's two questions (email, 28-Oct-26) are reworded to stay open: Q1 'look of canvas vs natural cotton' → 4.2, 4.4, 4.5, 4.6, 4.7. "
               "Q2 'properties they like' → 3.1, 3.2, 4.3, 4.4. Known complaints (fading, bleeding, softening) are never raised by the interviewer; 3.3 lets them come up naturally."])
    ws.cell(row=ws.max_row, column=1).font = Font(name="Arial", size=9, italic=True)

    ws = wb.create_sheet("Call List")
    cols = ["Call ID", "Cohort", "Customer name", "Phone", "City", "Last purchase date", "Last order — products",
            "Canvas product(s) bought", "# orders (lifetime)", "Assigned to", "Call status", "Call date", "Notes"]
    header(ws, cols, [9, 22, 22, 15, 14, 14, 36, 26, 11, 14, 14, 12, 30])
    ws.append(["Pending warehouse pull — run the queries in the 'Call List SQL' tab and paste results from row 3. "
               "Pull ~3× the call target per cohort to allow for no-answers."])
    ws.cell(row=2, column=1).font = Font(name="Arial", size=9, italic=True, color="9A3412")

    ws = wb.create_sheet("Call List SQL")
    header(ws, ["Step", "Query (BigQuery)"], [22, 140])
    with open(__file__.replace("build_sheet.py", "call_lists.sql")) as f:
        sql = f.read()
    for block in sql.split("\n-- @@ ")[1:]:
        name, body = block.split("\n", 1)
        row(ws, [name.strip(), body.strip()])

    for s in wb.worksheets:
        for r in s.iter_rows():
            for c in r:
                if c.font and c.font.name != "Arial":
                    c.font = Font(name="Arial", size=c.font.size or 10, bold=c.font.b, italic=c.font.i, color=c.font.color)
    wb.save(path)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "consumer_calling.xlsx")
