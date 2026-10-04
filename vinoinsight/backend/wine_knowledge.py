"""
VinoInsight AI - Offline Wine Knowledge Base
--------------------------------------------
A broad, beginner-friendly knowledge base covering the general wine domain.

This is the OFFLINE FALLBACK used by wine_chatbot.py when the Gemini API is
unavailable (no API key configured, no internet, rate limit hit, or a transient
API error). It is deliberately wide rather than deep: the goal is that a user
with no wine knowledge always gets a useful, plain-English answer, even when
the live AI model cannot be reached.

Structure
---------
KNOWLEDGE_BASE is a list of (keywords, answer) pairs.

  * keywords  - list of lowercase trigger phrases. Matching is done on whole
                words (with an optional trailing "s" for simple plurals), so
                "ph" will not match inside "phone" and "port" will not match
                inside "important".
  * answer    - a short, beginner-friendly response (2-4 sentences).

Multi-word keywords are scored higher than single words, so a question like
"what food goes with red wine" matches the FOOD PAIRING entry rather than the
generic RED WINE entry. See wine_chatbot._fallback_answer() for the scorer.

Adding a topic is intentionally low-friction: append one more tuple below.
"""

KNOWLEDGE_BASE = [

    # ------------------------------------------------------------------
    # GREETINGS / META / APP USAGE
    # ------------------------------------------------------------------
    (['hello', 'hey there', 'hi there', 'good morning', 'good evening'],
     "Hello! I'm the VinoInsight wine assistant. Ask me anything about wine — "
     "grape varieties, wine styles, taste and aroma, food pairing, serving and "
     "storage, wine regions, how wine is made, or how this app's predictions work. "
     "No prior wine knowledge needed."),

    (['what can you do', 'what can i ask', 'what do you know', 'help me',
      'what topics', 'who are you', 'what are you'],
     "I can explain anything wine-related in simple terms: types of wine, grape "
     "varieties, how a wine tastes and smells, which foods to pair it with, what "
     "temperature to serve it at, how to store it, wine regions, how wine is made, "
     "and confusing wine words. I can also explain how VinoInsight predicts wine "
     "quality, price range, aroma profile, and consumer segment."),

    (['how do i use', 'how can i use', 'how to use', 'getting started',
      'how does this app work', 'how do i start', 'how to work',
      'how do i work', 'work this system', 'use this system',
      'use this app', 'work this app', 'how does vinoinsight work'],
     "Go to Predict, choose a Wine Style (Red, White, Rosé, Sparkling, or Dessert), "
     "enter the chemical values (acidity, pH, alcohol, sugar, sulphates, etc.), then "
     "click Predict. You'll get a quality score, price range, aroma profile, and "
     "consumer segment, plus recommendations to improve quality. Use Compare to check "
     "two wines side by side."),

    (['compare page', 'compare wines', 'compare two'],
     "Use the Compare page to enter two wine samples side by side and see which one "
     "scores higher across all five predictions."),

    (['quality score', 'quality prediction', 'predict quality', 'quality range'],
     "VinoInsight predicts a wine's quality score from its measured chemistry — things "
     "like alcohol, volatile acidity, sulphates, and residual sugar. Higher alcohol and "
     "balanced acidity usually push the score up, while high volatile acidity pulls it "
     "down. The Results page also shows which specific inputs influenced your score most."),

    (['consumer segment'],
     "Consumer segment is VinoInsight's estimate of which type of drinker a wine suits — "
     "for example everyday casual drinkers, enthusiasts, or premium collectors. It's "
     "inferred from the predicted quality and price characteristics."),

    # ------------------------------------------------------------------
    # MAIN WINE TYPES
    # ------------------------------------------------------------------
    (['types of wine', 'kinds of wine', 'wine types', 'different wines',
      'main types', 'categories of wine', 'styles of wine'],
     "There are five main styles. Red wine is made from dark grapes fermented with "
     "their skins; white wine is made mostly without skins; rosé gets brief skin "
     "contact for its pink colour; sparkling wine (like Champagne or Prosecco) has "
     "bubbles from a second fermentation; and dessert or fortified wine (like Port or "
     "Sauternes) is sweet and often stronger. Everything else is a variation on these."),

    (['red wine'],
     "Red wine is made from dark-skinned grapes fermented together with their skins, "
     "which gives it colour and tannin. It usually tastes of dark fruit, sometimes with "
     "notes of spice, leather, or oak, and feels slightly drying in the mouth. Popular "
     "examples are Cabernet Sauvignon, Merlot, Pinot Noir, and Shiraz."),

    (['white wine'],
     "White wine is usually made without grape skins, so it's lighter in colour, has "
     "almost no tannin, and tastes crisper and fresher than red. Styles range from "
     "light and zesty (Sauvignon Blanc, Pinot Grigio) to rich and creamy (oaked "
     "Chardonnay). It's normally served chilled."),

    (['rose wine', 'rosé', 'rose', 'pink wine', 'blush wine'],
     "Rosé is made from red grapes, but the juice sits with the skins for only a few "
     "hours instead of days — just long enough to pick up a pink colour. The result is "
     "lighter and fresher than red, usually with strawberry or citrus notes. Serve it "
     "well chilled; it's a good beginner wine."),

    (['sparkling wine', 'bubbly', 'fizzy wine', 'bubbles'],
     "Sparkling wine gets its bubbles from a second fermentation that traps carbon "
     "dioxide in the bottle. Champagne (France) is the most famous, but Prosecco "
     "(Italy) and Cava (Spain) offer similar enjoyment for less. Serve it very cold, "
     "around 6-8°C, in a tall flute or a white wine glass."),

    (['dessert wine', 'sweet wine', 'pudding wine'],
     "Dessert wines are sweet because fermentation is stopped early or the grapes are "
     "dried, frozen, or affected by 'noble rot', which concentrates their sugar. "
     "Examples include Sauternes, Ice Wine, Moscato, and Tokaji. They're served cold "
     "in small glasses, usually with dessert or blue cheese."),

    (['fortified wine', 'fortified'],
     "Fortified wine has a neutral grape spirit added during or after fermentation, "
     "raising the alcohol to roughly 17-20%. Port, Sherry, Madeira, and Marsala are the "
     "classic examples. They keep much longer once opened than ordinary wine — often "
     "several weeks."),

    (['orange wine', 'skin contact wine', 'amber wine'],
     "Orange wine is white wine made like a red — the juice ferments in contact with "
     "the grape skins, giving it an amber colour, a little tannin, and a nutty, dried-"
     "fruit character. It's an old technique that became fashionable again recently. "
     "Serve it lightly chilled, around 12-14°C."),

    (['natural wine', 'organic wine', 'biodynamic', 'vegan wine', 'sustainable wine'],
     "Organic wine comes from grapes grown without synthetic pesticides; biodynamic goes "
     "further with a whole-farm, calendar-based approach; natural wine adds minimal "
     "intervention in the cellar, with little or no added sulphites. Vegan wine simply "
     "avoids animal-derived fining agents like egg white or isinglass. None of these "
     "labels automatically means better-tasting wine — they describe how it was made."),

    (['non alcoholic', 'alcohol free', 'dealcoholised', 'zero alcohol'],
     "Non-alcoholic wine is made normally and then has the alcohol removed by vacuum "
     "distillation or filtration. It keeps much of the aroma but loses some body, since "
     "alcohol carries weight and texture. Chilling it well and serving it in a proper "
     "wine glass makes a noticeable difference."),

    # ------------------------------------------------------------------
    # DIFFERENCES / COMPARISONS
    # ------------------------------------------------------------------
    (['red vs white', 'difference between red and white',
      'red and white difference', 'red or white'],
     "The main difference is the grape skins. Red wine ferments with the skins, which "
     "adds colour, tannin, and a fuller, drier mouthfeel; white wine is normally made "
     "without them, so it's lighter, crisper, and more acidic. Reds are served warmer "
     "(14-18°C) and whites cold (7-12°C)."),

    (['champagne vs prosecco', 'difference between champagne and prosecco',
      'champagne and prosecco'],
     "Champagne is made only in the Champagne region of France, with a second "
     "fermentation inside each bottle, giving bready, toasty flavours and fine bubbles. "
     "Prosecco is Italian, fermented in a large tank, which keeps it fruitier, lighter, "
     "and much cheaper. Both are sparkling — Champagne is more complex, Prosecco more "
     "easy-going."),

    (['old world', 'new world', 'old world vs new world'],
     "'Old World' means traditional European wine countries — France, Italy, Spain, "
     "Germany, Portugal — where wines tend to be lighter, more earthy, and named after "
     "the place. 'New World' means everywhere else — the USA, Australia, Chile, "
     "Argentina, New Zealand, South Africa — where wines are usually riper, fruitier, "
     "and named after the grape. Neither is better; they're different styles."),

    (['dry vs sweet', 'difference between dry and sweet', 'dry or sweet',
      'dry wine', 'dry', 'off dry', 'what does dry mean'],
     "'Dry' means the yeast converted nearly all the grape sugar into alcohol, so there's "
     "little sweetness left — most red and white table wines are dry. 'Off-dry' has a "
     "touch of sweetness, and 'sweet' wines have plenty. Note that a wine can taste fruity "
     "and still be dry: fruit aroma is not the same as sugar."),

    # ------------------------------------------------------------------
    # RED GRAPE VARIETIES
    # ------------------------------------------------------------------
    (['grape variety', 'grape varieties', 'varietal', 'types of grapes',
      'wine grapes', 'which grapes'],
     "A grape variety is simply the type of grape a wine is made from, and it's the "
     "single biggest influence on how a wine tastes. Common reds are Cabernet Sauvignon, "
     "Merlot, Pinot Noir, Syrah/Shiraz, Malbec, and Sangiovese; common whites are "
     "Chardonnay, Sauvignon Blanc, Riesling, Pinot Grigio, and Moscato. Learning three or "
     "four you like is the fastest way into wine."),

    (['cabernet sauvignon', 'cabernet', 'cab sauv'],
     "Cabernet Sauvignon is a full-bodied red with firm tannins and flavours of "
     "blackcurrant, cedar, and sometimes green pepper. It ages well and is the backbone "
     "of Bordeaux and Napa Valley reds. Pair it with steak or lamb."),

    (['merlot'],
     "Merlot is a softer, rounder red than Cabernet, with plum and black cherry flavours "
     "and gentler tannins. That smoothness makes it one of the easiest reds for beginners. "
     "It pairs well with roast chicken, pork, and tomato-based pasta."),

    (['pinot noir'],
     "Pinot Noir is a light-bodied red with low tannin, bright acidity, and red cherry, "
     "raspberry, and earthy or mushroomy notes. Burgundy in France is its spiritual home. "
     "It's unusually food-friendly and even works with salmon and duck."),

    (['syrah', 'shiraz'],
     "Syrah (called Shiraz in Australia) is a bold red with blackberry, black pepper, and "
     "smoky notes. French versions are typically more peppery and restrained; Australian "
     "ones are riper and jammier. It's excellent with grilled and barbecued meat."),

    (['malbec'],
     "Malbec is a deeply coloured Argentine red with plum and blackberry flavours, soft "
     "tannins, and a velvety texture. It offers a lot of flavour for the price, which makes "
     "it a popular everyday red. It's a natural partner for steak."),

    (['zinfandel'],
     "Zinfandel is a ripe, jammy red from California with brambly fruit, spice, and often "
     "high alcohol. 'White Zinfandel' is a completely different thing — a sweet pink wine. "
     "Red Zinfandel suits barbecue and burgers."),

    (['sangiovese', 'chianti'],
     "Sangiovese is Italy's signature red grape and the base of Chianti. It has high "
     "acidity, firm tannins, and sour cherry, tomato leaf, and herb flavours. That acidity "
     "makes it superb with tomato-based Italian food."),

    (['nebbiolo', 'barolo', 'barbaresco'],
     "Nebbiolo makes Barolo and Barbaresco in northern Italy. It's pale in colour but "
     "powerful in taste, with high tannin and acidity and aromas of rose, tar, and cherry. "
     "These wines usually need several years of ageing to soften."),

    (['tempranillo', 'rioja'],
     "Tempranillo is Spain's leading red grape and the main grape of Rioja. It gives cherry "
     "and dried-fig flavours, and Spanish oak ageing adds vanilla, coconut, and leather. "
     "Labels marked Crianza, Reserva, or Gran Reserva have been aged progressively longer."),

    (['grenache', 'garnacha'],
     "Grenache (Garnacha in Spain) makes soft, generous reds with strawberry and white "
     "pepper notes and relatively high alcohol. It's often blended, most famously in "
     "Châteauneuf-du-Pape and in GSM blends with Syrah and Mourvèdre."),

    # ------------------------------------------------------------------
    # WHITE GRAPE VARIETIES
    # ------------------------------------------------------------------
    (['chardonnay'],
     "Chardonnay is the world's most planted white grape and takes many forms. Unoaked "
     "versions like Chablis are lean, citrusy, and mineral; oaked versions are richer, with "
     "butter, vanilla, and tropical fruit. If you disliked one style, try the other before "
     "writing the grape off."),

    (['sauvignon blanc'],
     "Sauvignon Blanc is a crisp, high-acid white with grapefruit, gooseberry, and fresh-cut "
     "grass aromas. New Zealand versions are punchy and tropical; French Sancerre is more "
     "restrained and mineral. Serve it very cold with goat cheese, salads, or seafood."),

    (['riesling'],
     "Riesling is an aromatic white with bright acidity and aromas of lime, green apple, and "
     "sometimes honey or petrol. It comes in every sweetness level from bone dry to lusciously "
     "sweet, so check the label. Its acidity makes it the best all-round match for spicy food."),

    (['pinot grigio', 'pinot gris'],
     "Pinot Grigio and Pinot Gris are the same grape in different styles. Italian Pinot Grigio "
     "is light, dry, and neutral — an easy aperitif; Alsatian Pinot Gris is richer, spicier, "
     "and sometimes slightly sweet. Both are served well chilled."),

    (['moscato', 'muscat'],
     "Moscato is a light, sweet, slightly fizzy white with grapey, peachy, orange-blossom "
     "aromas and low alcohol (around 5-7%). Its sweetness and gentle character make it very "
     "beginner-friendly. Serve it very cold, with fruit desserts or on its own."),

    (['chenin blanc'],
     "Chenin Blanc is a versatile white from the Loire Valley in France and South Africa. It "
     "has high acidity and apple, quince, and honey flavours, and appears dry, off-dry, sweet, "
     "and sparkling. Dry versions pair beautifully with roast chicken and pork."),

    (['viognier'],
     "Viognier is a full-bodied white with low acidity and heady aromas of apricot, peach, and "
     "honeysuckle. It tastes almost sweet because of that perfume, but it's usually dry. Serve "
     "it slightly less cold than most whites, around 10-12°C."),

    (['gewurztraminer', 'gewürztraminer'],
     "Gewürztraminer is intensely aromatic, with lychee, rose petal, and ginger notes and a "
     "soft, oily texture. It's often off-dry, which helps it handle spicy Asian dishes. If you "
     "like fragrant wines, this is one to try."),

    # ------------------------------------------------------------------
    # FAMOUS WINE NAMES / REGIONS
    # ------------------------------------------------------------------
    (['wine region', 'wine regions', 'where is wine made', 'wine producing countries',
      'best wine countries'],
     "The biggest producers are Italy, France, and Spain, followed by the USA, Argentina, "
     "Chile, Australia, South Africa, and Germany. Region matters because climate shapes "
     "style: cooler places (Burgundy, Germany, New Zealand) give lighter, higher-acid wines, "
     "while warmer places (Napa, Barossa, Mendoza) give riper, fuller, higher-alcohol wines."),

    (['bordeaux'],
     "Bordeaux is a region in south-west France famous for red blends of Cabernet Sauvignon "
     "and Merlot, plus dry and sweet whites. Left Bank wines are Cabernet-led and firmer; "
     "Right Bank wines are Merlot-led and softer. Bordeaux is named after the place, not the "
     "grape."),

    (['burgundy', 'bourgogne'],
     "Burgundy in eastern France makes red wine from Pinot Noir and white wine from "
     "Chardonnay — almost nothing else. Its wines are labelled by vineyard rather than grape, "
     "which is why the labels look confusing. Chablis is Burgundy's northern, unoaked "
     "Chardonnay area."),

    (['champagne'],
     "Champagne is sparkling wine made only in the Champagne region of northern France, using "
     "a second fermentation in the bottle. That process creates fine bubbles and toasty, "
     "biscuity flavours. 'Brut' on the label means dry, which is the most common style."),

    (['port', 'porto'],
     "Port is a sweet fortified red wine from the Douro Valley in Portugal, usually around 20% "
     "alcohol. Ruby Port is fruity and youthful; Tawny Port is aged in barrel and tastes of "
     "caramel, nuts, and dried fruit. Serve it in small glasses with chocolate or blue cheese."),

    (['sherry', 'jerez'],
     "Sherry is a fortified wine from southern Spain, ranging from bone-dry Fino and Manzanilla "
     "to rich, sweet Pedro Ximénez. Dry styles are served chilled as an aperitif and go "
     "brilliantly with olives, almonds, and ham. It's one of the best-value wine categories."),

    (['prosecco'],
     "Prosecco is Italy's popular sparkling wine, made from the Glera grape in a large tank "
     "rather than in the bottle. That keeps it fresh, fruity, and floral, with pear and apple "
     "notes. It's lighter and cheaper than Champagne and best drunk young and very cold."),

    (['beaujolais'],
     "Beaujolais is a light, juicy French red made from the Gamay grape, with bright cherry and "
     "banana-like fruit and very soft tannins. It's one of the few reds that's genuinely nice "
     "slightly chilled, around 12-14°C. A great choice if you find most reds too heavy."),

    # ------------------------------------------------------------------
    # TASTE, AROMA & CHARACTERISTICS
    # ------------------------------------------------------------------
    (['tannin'],
     "Tannins come from grape skins, seeds, stems, and oak barrels. They create the dry, "
     "slightly grippy feeling on your gums and tongue — like over-brewed tea — and are mostly "
     "found in red wine. Tannin also helps a wine age, and it softens over time."),

    (['acidity', 'acid', 'crisp', 'tart'],
     "Acidity gives wine its freshness and makes your mouth water. Too little and a wine tastes "
     "flat and heavy; too much and it tastes sharp or sour. It's the reason white wines feel "
     "refreshing and why high-acid wines work so well with food."),

    (['body', 'full bodied', 'light bodied', 'medium bodied'],
     "Body is how heavy a wine feels in your mouth — think skimmed milk versus cream. It comes "
     "mainly from alcohol and extract, so higher-alcohol wines feel fuller. Pinot Grigio and "
     "Pinot Noir are light-bodied; oaked Chardonnay and Cabernet Sauvignon are full-bodied."),

    (['aroma', 'smell', 'nose', 'bouquet', 'scent'],
     "Aroma is what you smell in a wine, and it accounts for most of what you think you're "
     "tasting. 'Primary' aromas come from the grape (fruit, flowers, herbs), 'secondary' from "
     "fermentation (bread, butter), and 'tertiary' or 'bouquet' from ageing (nuts, leather, "
     "dried fruit). Swirling the glass releases them."),

    (['finish', 'aftertaste', 'length'],
     "The finish is how long the flavour lingers after you swallow. A few seconds is short; "
     "30 seconds or more is long, and generally a sign of a better wine. A pleasant, "
     "persistent finish matters more than a big first impression."),

    (['balance', 'complexity', 'good wine', 'what makes a good wine'],
     "A good wine is balanced — no single element (acidity, sweetness, tannin, alcohol, oak) "
     "sticks out. Beyond that, quality shows in complexity (several layers of flavour) and a "
     "long finish. Ultimately the best wine is the one you enjoy drinking, and price is only a "
     "rough guide."),

    (['minerality', 'mineral'],
     "'Minerality' is an informal tasting term for a wet-stone, chalky, or flinty impression, "
     "often found in Chablis, Sancerre, and Riesling. Scientists still debate what causes it, "
     "since wine doesn't literally absorb minerals from the soil. In practice it's used to "
     "describe wines that taste more stony than fruity."),

    (['legs', 'tears of wine'],
     "The 'legs' or 'tears' running down the inside of a glass after you swirl it come from "
     "alcohol evaporating faster than water. They tell you a wine is high in alcohol or sugar "
     "— nothing more. They are not an indicator of quality, despite the myth."),

    (['oak', 'oaked', 'oaky', 'barrel', 'oak aging', 'oak ageing',
      'barrel aging', 'barrel ageing', 'oak barrel'],
     "Ageing wine in oak barrels adds flavours of vanilla, toast, coconut, or baking spice and "
     "softens the texture. New barrels give a stronger effect than old ones, and French oak is "
     "subtler than American oak. Cheaper wines sometimes use oak chips for a similar effect."),

    (['vintage'],
     "The vintage is simply the year the grapes were picked. It matters because weather varies: "
     "a warm year gives riper, fuller wines and a cool one gives lighter, crisper wines. For "
     "most everyday wines the vintage matters far less than people assume — drink them young."),

    (['terroir'],
     "Terroir is a French idea covering everything about a vineyard's location — soil, slope, "
     "climate, and local tradition — that gives its wine a distinctive character. It's why the "
     "same grape tastes different in Burgundy and in California. It's also why European labels "
     "emphasise place over grape."),

    (['taste wine', 'how to taste', 'tasting wine', 'wine tasting'],
     "Use four steps: look at the colour, swirl the glass to release aromas, smell it properly, "
     "then take a sip and let it coat your mouth. Ask yourself simple questions — is it sweet or "
     "dry, light or heavy, does the flavour last? You don't need fancy vocabulary; noticing what "
     "you like is the whole point."),

    (['sulphate', 'sulfate', 'sulfite', 'sulphite'],
     "Sulphites are a preservative and antioxidant that keep wine fresh and stable, and small "
     "amounts occur naturally in all fermented wine. In VinoInsight's chemical inputs, higher "
     "sulphates often correlate with better-rated wines. Only a small number of people are "
     "genuinely sulphite-sensitive — sulphites are not the usual cause of wine headaches."),

    (['alcohol content', 'alcohol', 'abv', 'how strong', 'alcohol percentage'],
     "Most table wine is 11-14% alcohol by volume (ABV), while fortified wines like Port reach "
     "18-20% and light Moscato can be as low as 5%. Alcohol adds body and a warm sensation, so "
     "higher-alcohol wines feel fuller and richer. The percentage is always printed on the label."),

    (['residual sugar', 'sugar', 'sweetness'],
     "Residual sugar is the grape sugar left over after fermentation stops — the more that "
     "remains, the sweeter the wine. Dry wines have very little; dessert wines have a lot. In "
     "VinoInsight, residual sugar is one of the inputs used to predict a wine's aroma profile "
     "and style."),

    (['ph'],
     "pH measures how acidic a wine is, on a scale where lower means more acidic. Most wines "
     "sit between 3.0 and 4.0, with whites typically lower (more acidic) than reds. Low pH "
     "keeps a wine fresh and helps it age; high pH makes it taste flabby and spoil faster."),

    (['volatile acidity'],
     "Volatile acidity is mostly acetic acid — the compound in vinegar. A trace adds lift and "
     "complexity, but too much makes a wine smell sharp, vinegary, or of nail polish. It's one "
     "of the strongest negative predictors of quality in VinoInsight's model."),

    # ------------------------------------------------------------------
    # FOOD PAIRING
    # ------------------------------------------------------------------
    (['food pairing', 'pair with food', 'what food', 'goes with', 'pairing',
      'what to eat', 'match with food', 'food and wine'],
     "The simplest rule is to match weight with weight: light wines with light dishes, bold "
     "wines with rich dishes. Acidity cuts through fat and salt, sweetness tames spice, and "
     "tannin softens against protein and fat. When in doubt, a dry rosé or an unoaked white "
     "goes with a surprising amount of food."),

    (['pair with steak', 'wine with steak', 'with steak', 'steak', 'red meat',
      'with beef', 'beef', 'with lamb', 'lamb', 'barbecue', 'grilled meat'],
     "Red meat calls for a tannic red — Cabernet Sauvignon, Malbec, Syrah, or a Bordeaux blend. "
     "The protein and fat in the meat soften the tannins, so the wine tastes smoother and the "
     "meat tastes richer. Lamb also works beautifully with Rioja."),

    (['wine with fish', 'with fish', 'fish', 'with seafood', 'seafood', 'sushi',
      'salmon', 'shellfish', 'prawn', 'oyster'],
     "Most fish and seafood suit crisp, unoaked whites: Sauvignon Blanc, Pinot Grigio, Albariño, "
     "or Chablis. The acidity works like a squeeze of lemon. For richer fish like salmon or tuna, "
     "a light red such as Pinot Noir works well too."),

    (['wine with chicken', 'with chicken', 'chicken', 'with pork', 'pork',
      'turkey', 'roast dinner'],
     "Chicken and pork are flexible — they sit between light and heavy. Chardonnay, Chenin Blanc, "
     "or a light red like Pinot Noir or Beaujolais all work. Let the sauce decide: creamy sauces "
     "want a richer white, tomato sauces want a higher-acid red."),

    (['wine with cheese', 'with cheese', 'cheese', 'cheese pairing', 'cheese board'],
     "White wine actually pairs with cheese more reliably than red, because its acidity cuts the "
     "fat. Try Sauvignon Blanc with goat cheese, Chardonnay with brie, and a sweet wine like Port "
     "or Sauternes with blue cheese. Hard aged cheeses like Parmesan are the ones that do suit "
     "big reds."),

    (['wine with pasta', 'with pasta', 'pasta', 'with pizza', 'pizza',
      'with tomato', 'tomato', 'italian food', 'lasagne'],
     "Tomato-based dishes are acidic, so they need a high-acid red — Chianti (Sangiovese), "
     "Barbera, or Valpolicella. For creamy or cheesy pasta, an unoaked Chardonnay or Pinot Grigio "
     "is better. Pizza works with almost any medium-bodied Italian red."),

    (['spicy food', 'wine with curry', 'with curry', 'curry', 'with indian',
      'with thai', 'thai', 'spicy', 'chilli', 'chili', 'hot food'],
     "Spicy food needs a wine with some sweetness and low alcohol, because alcohol amplifies "
     "heat. Off-dry Riesling, Gewürztraminer, or Moscato all tame chilli nicely. Avoid tannic, "
     "high-alcohol reds — they make spice feel harsher."),

    (['wine with chocolate', 'with chocolate', 'chocolate', 'with dessert',
      'dessert pairing', 'with cake', 'sweet course'],
     "The key rule is that the wine should be sweeter than the dessert, or it will taste sour by "
     "comparison. Port or a sweet red works with dark chocolate, Moscato with fruit desserts, and "
     "Sauternes with custard or tarts. Dry red wine and chocolate is a common mismatch."),

    (['vegetarian', 'wine with salad', 'wine with vegetables', 'vegan food'],
     "Vegetable dishes usually suit crisp whites and light reds: Sauvignon Blanc with green "
     "vegetables and herbs, dry rosé with roasted vegetables, and Pinot Noir with mushrooms or "
     "lentils. Watch out for vinaigrettes — a high-acid wine handles them best."),

    # ------------------------------------------------------------------
    # SERVING
    # ------------------------------------------------------------------
    (['serving temperature', 'serve', 'temperature', 'how cold', 'chill',
      'what temperature', 'best temperature', 'right temperature',
      'serve red', 'serve white', 'serve wine', 'too warm', 'ice bucket'],
     "Sparkling wine is best at 6-8°C, light whites and rosé at 7-10°C, full-bodied whites at "
     "10-13°C, light reds at 12-14°C, and full reds at 15-18°C. Most people serve white too cold "
     "and red too warm — 20 minutes in the fridge improves nearly any red. Very cold temperatures "
     "mute aroma."),

    (['decant', 'decanting', 'decanter', 'breathe', 'aerate', 'aeration',
      'let it breathe'],
     "Decanting means pouring wine into a wide vessel so it meets air, which softens tannins and "
     "opens up the aroma. Young, tannic reds benefit most — 30 to 60 minutes is usually plenty. "
     "It also separates old wines from their sediment. Simply pulling the cork does almost nothing."),

    (['wine glass', 'glassware', 'which glass', 'glass shape', 'glass',
      'what glass', 'stemware', 'flute'],
     "Use a glass with a bowl wide enough to swirl and a rim that narrows to concentrate aroma, "
     "and hold it by the stem so you don't warm the wine. Reds suit a bigger bowl, whites a "
     "smaller one, and sparkling a flute or narrow white glass. One decent all-purpose glass is "
     "genuinely enough."),

    (['how much to pour', 'pour', 'serving size', 'how many glasses'],
     "A standard pour is about 150ml, which gives roughly five glasses from a 750ml bottle. Fill "
     "only to the widest part of the bowl — about a third — so there's room to swirl. For tasting "
     "rather than drinking, 50ml is enough."),

    (['open wine', 'opening', 'corkscrew', 'how to open'],
     "Cut the foil below the lip, insert the corkscrew in the centre of the cork, twist until "
     "almost through, then lever it out steadily. For sparkling wine, hold the cork firmly and "
     "twist the bottle instead — aim it away from people and let it sigh rather than pop. A "
     "waiter's friend corkscrew is the most reliable tool."),

    # ------------------------------------------------------------------
    # STORAGE & AGEING
    # ------------------------------------------------------------------
    (['store wine', 'storage', 'how to store', 'store', 'storing', 'keep wine',
      'wine fridge', 'cellar', 'where to keep', 'wine rack'],
     "Store wine on its side (so a cork stays moist) somewhere cool, dark, and steady — ideally "
     "10-15°C. Temperature swings, direct light, vibration, and heat are what actually ruin wine. "
     "A cupboard away from the oven beats the top of the fridge; screwcap bottles can stand "
     "upright."),

    (['opened wine', 'how long does wine last', 'after opening', 'leftover wine',
      'keep opened', 'stays good', 'opened bottle', 'open bottle',
      'half a bottle', 'once opened', 'store an opened'],
     "Once opened, most reds and whites last 3-5 days in the fridge with the cork pushed back in "
     "— yes, red goes in the fridge too, just let it warm up before drinking. Sparkling wine loses "
     "fizz within 1-3 days even with a stopper. Fortified wines like Port and Sherry last several "
     "weeks."),

    (['aging', 'ageing', 'age wine', 'get better with age', 'how long to keep',
      'improve with age', 'age this', 'should i age', 'cellar it',
      'lay it down', 'drink now or'],
     "Only about 1% of wine actually improves with age — it needs enough tannin, acidity, or sugar "
     "to survive. Most wine on shop shelves is made to drink within one to three years, and keeping "
     "it longer makes it worse, not better. Age-worthy bottles are typically structured reds, fine "
     "Riesling, and sweet or fortified wines."),

    (['corked', 'cork taint', 'gone bad', 'off wine', 'spoiled', 'bad wine',
      'wine gone off'],
     "A 'corked' wine smells of wet cardboard or damp basement and tastes dull — it's caused by a "
     "compound called TCA in the cork, affects a small percentage of bottles, and is harmless but "
     "unpleasant. Wine that smells sharply of vinegar or looks brown when it shouldn't has oxidised. "
     "In both cases the bottle is faulty and a shop will usually replace it."),

    (['cork vs screwcap', 'screwcap', 'screw cap', 'why cork'],
     "Screwcaps seal more reliably and completely eliminate cork taint, which is why New Zealand "
     "and Australia adopted them widely. Cork allows a very slow oxygen exchange that some believe "
     "helps long ageing. A screwcap says nothing about quality — plenty of excellent wine uses one."),

    # ------------------------------------------------------------------
    # PRODUCTION
    # ------------------------------------------------------------------
    (['how is wine made', 'wine making', 'winemaking', 'production process',
      'how do they make wine', 'made from'],
     "Grapes are harvested, crushed, and then fermented — yeast eats the sugar and converts it into "
     "alcohol and carbon dioxide. Red wine ferments with the skins for colour and tannin; white "
     "wine is pressed first so the skins are removed. The wine is then clarified, sometimes aged in "
     "oak or steel, and finally bottled."),

    (['fermentation', 'ferment', 'yeast'],
     "Fermentation is the step where yeast converts grape sugar into alcohol and carbon dioxide, "
     "typically over one to three weeks. Stop it early and sugar remains, giving a sweeter wine; "
     "let it finish and you get a dry wine. Temperature matters too — cooler fermentation preserves "
     "fresh, fruity aromas."),

    (['malolactic', 'malolactic fermentation', 'malic acid', 'lactic'],
     "Malolactic fermentation is a second, bacterial conversion that turns sharp malic acid (as in "
     "green apples) into softer lactic acid (as in milk). It makes a wine rounder and can add "
     "buttery notes — it's why some Chardonnay tastes creamy. Nearly all reds go through it; whites "
     "only when the winemaker wants that softness."),

    (['harvest', 'picking', 'when are grapes picked'],
     "Grapes are harvested when sugar, acidity, and flavour reach the right balance — usually late "
     "summer to autumn, so around September in Europe and February to April in the southern "
     "hemisphere. Picking early keeps acidity and lowers alcohol; picking late gives riper, "
     "fuller wines. Some pickers work at night to keep the fruit cool."),

    (['blend', 'blending', 'blended wine'],
     "A blended wine mixes two or more grape varieties so their strengths cover each other's gaps "
     "— Cabernet's structure with Merlot's softness, for example. Blending is a mark of skill, not "
     "a shortcut; Bordeaux and Champagne are both blends. A 'single varietal' wine, by contrast, is "
     "made from mostly one grape."),

    (['how are bubbles made', 'traditional method', 'second fermentation', 'tank method'],
     "Bubbles come from a second fermentation that traps carbon dioxide. In the 'traditional method' "
     "used for Champagne and Cava it happens inside each individual bottle, giving fine bubbles and "
     "toasty flavours; in the 'tank method' used for Prosecco it happens in a large pressurised tank, "
     "keeping the wine fruitier and cheaper."),

    # ------------------------------------------------------------------
    # LABELS & TERMINOLOGY
    # ------------------------------------------------------------------
    (['read a label', 'wine label', 'label mean', 'understanding labels'],
     "A label usually tells you the producer, region or appellation, vintage year, grape variety "
     "(on New World wines), and alcohol percentage. European labels often name the place instead of "
     "the grape, so 'Chablis' means Chardonnay and 'Rioja' means mostly Tempranillo. Terms like "
     "Reserva or Riserva indicate longer legally required ageing."),

    (['brut', 'extra dry', 'demi sec', 'sec'],
     "On sparkling wine, sweetness terms are counter-intuitive: Brut Nature is driest, then Extra "
     "Brut, Brut, Extra Dry, Sec, Demi-Sec, and Doux, which is sweetest. Confusingly, 'Extra Dry' "
     "is sweeter than 'Brut'. Brut is the standard style most people expect."),

    (['appellation', 'aoc', 'doc', 'docg', 'ava', 'denominazione'],
     "An appellation is a legally defined wine region with rules about which grapes can be grown "
     "and how the wine is made — AOC in France, DOC/DOCG in Italy, DO/DOCa in Spain, AVA in the "
     "USA. It guarantees origin and style, not quality. It's why the region name on a European "
     "label tells you so much."),

    (['reserve', 'reserva', 'riserva', 'gran reserva'],
     "In Spain and Italy, Reserva/Riserva is legally defined and means the wine was aged longer "
     "before release — Gran Reserva longest of all. In the USA and much of the New World, "
     "'Reserve' has no legal meaning and is often just marketing. Check the country before reading "
     "anything into it."),

    (['sommelier'],
     "A sommelier is a trained wine professional, usually working in a restaurant, who manages the "
     "wine list and helps guests choose. Certification takes years of study and blind tasting. In "
     "a restaurant, telling them your budget and what you're eating gets you a better bottle than "
     "trying to guess."),

    (['estate bottled', 'domaine', 'chateau'],
     "'Estate bottled', 'Domaine', and 'Château' all indicate that the producer grew the grapes and "
     "made the wine on their own property, rather than buying in fruit. It suggests more control "
     "over quality, though it's not a guarantee. Négociant wines, by contrast, are made from "
     "purchased grapes."),

    # ------------------------------------------------------------------
    # PRACTICAL / BUYING / HEALTH
    # ------------------------------------------------------------------
    (['how to choose', 'which wine should i', 'recommend a wine', 'beginner wine',
      'start with', 'first wine', 'best wine for beginners', 'what should i drink',
      # 'try first' added after a probe question ("what wine should I try
      # first?") fell through to the generic catch-all despite this entry
      # being exactly the right answer.
      'try first', 'should i try', 'new to wine', 'know nothing about wine'],
     "If you're new, start with softer, fruit-forward wines: Merlot or Pinot Noir for red, Pinot "
     "Grigio or Sauvignon Blanc for white, or a dry rosé that sits between the two. Buy two "
     "different bottles at once and taste them side by side — comparison teaches you far more than "
     "one bottle at a time. Note what you liked and build from there."),

    (['expensive wine', 'cheap wine', 'price', 'is expensive better', 'worth the money',
      'good value'],
     "Price reflects land cost, yields, oak, ageing, and brand as much as quality, and blind "
     "tastings regularly show people can't reliably tell cheap from expensive. The sweet spot for "
     "value is usually just above the cheapest tier, and lesser-known regions offer the most wine "
     "per rupee. VinoInsight estimates a price range from a wine's measured chemistry."),

    (['calories', 'how many calories', 'diet', 'carbs'],
     "A 150ml glass of dry wine has roughly 120-130 calories, most of it from alcohol rather than "
     "sugar. Sweet and higher-alcohol wines have more; light, low-alcohol wines have fewer. Dry "
     "wines contain very little residual carbohydrate."),

    (['health', 'good for you', 'benefits', 'resveratrol', 'healthy'],
     "Older studies suggested moderate red wine intake might help heart health via compounds like "
     "resveratrol, but more recent and better-designed research has largely undercut that idea, and "
     "major health bodies now say no level of alcohol is risk-free. Wine is best treated as "
     "something to enjoy in moderation, not as health food. For personal guidance, ask a doctor."),

    (['hangover', 'headache', 'why does wine give me'],
     "Wine headaches are most often caused by alcohol and dehydration, plus compounds such as "
     "histamines and tannins in some people — sulphites are usually blamed but rarely the culprit. "
     "Drinking water alongside, eating first, and choosing lower-alcohol wines all help. If red wine "
     "specifically triggers it, try a low-tannin red like Pinot Noir."),

    (['how many bottles', 'how much wine for a party', 'party', 'wedding'],
     "Plan on about half a bottle per guest for a meal, or two to three glasses each for a longer "
     "party — that's roughly one bottle for every two people. Sparkling wine goes fastest at the "
     "start of an event. Buy a little more than you need; unopened bottles keep."),

    # ------------------------------------------------------------------
    # HOW THE SYSTEM WORKS (explainable AI, models, inputs)
    # ------------------------------------------------------------------
    # Added after an independent coverage probe found the offline bot could not
    # answer questions about VinoInsight's own core concepts — including "What
    # is SHAP?", which is the project's central explainability idea, and
    # "chlorides", which is one of the model's own eleven inputs. Those are
    # exactly the questions likely to be asked during a demo, and exactly the
    # moment the live AI might be unavailable.
    (['shap', 'shapley', 'feature importance', 'explainable ai', 'explainability',
      'xai', 'why this prediction', 'why did it predict', 'how do you explain',
      'feature impact', 'interpretability'],
     "SHAP (SHapley Additive exPlanations) is how VinoInsight shows its working. It comes from "
     "game theory: each chemical property is treated like a player in a team, and SHAP works out "
     "how much each one pushed the prediction up or down compared with an average wine. On the "
     "Results page the green bars are properties that raised the prediction and the red bars are "
     "ones that lowered it, so you can see exactly why a wine scored the way it did rather than "
     "just being handed a number."),

    (['how does the prediction work', 'how does it predict', 'how does the model work',
      'how do the predictions work', 'how does prediction work', 'what model',
      'which algorithm', 'what algorithm', 'machine learning model',
      'how does the ai work', 'how is the prediction made'],
     "You enter eleven measured chemical properties and the system runs them through five trained "
     "machine-learning models — one for each output. Quality Score uses a Random Forest regressor; "
     "Quality Range, Price Range, Aroma Profile, and Consumer Segment use Random Forest and XGBoost "
     "classifiers. They were trained on the public Wine Quality dataset of 6,497 red and white "
     "wines. SHAP then explains which properties drove each individual result."),

    (['how accurate', 'accuracy', 'how reliable', 'is it accurate',
      'how good is the model', 'error rate'],
     "On a held-out test split: Quality Range 83.6% accuracy, Price Range 81.7%, and Consumer "
     "Segment 80.2%. Quality Score is a regression with R²=0.488 and an average error of about "
     "0.45 points out of 10. Aroma Profile shows 100%, but only because its label was rule-derived "
     "from the same input features — the project documents that openly rather than presenting it "
     "as a real result. Predictions are decision support, not a substitute for tasting."),

    (['chloride', 'salt in wine', 'salty', 'saltiness'],
     "Chlorides are the salt content of a wine, measured in grams per cubic decimetre. Most wines "
     "sit very low, around 0.04–0.10, and at that level you don't taste salt at all. High chloride "
     "usually points to grapes grown in salty soil or near the coast, and too much makes a wine "
     "taste faintly briny or harsh. It's one of the eleven inputs VinoInsight uses."),

    (['balanced', 'balance', 'well balanced', 'what does balanced mean'],
     "A balanced wine is one where no single element shouts over the others — the fruit, acidity, "
     "sweetness, tannin, and alcohol all feel proportionate. If a wine tastes too sharp, too sweet, "
     "too bitter, or too hot with alcohol, it's out of balance. Balance is one of the main things "
     "tasters judge, and it matters more to quality than any single component on its own."),

    # ------------------------------------------------------------------
    # ADDITIONAL REGIONS / TOPICS
    # ------------------------------------------------------------------
    (['italian wine', 'wine from italy', 'italy', 'tuscany', 'piedmont', 'barolo',
      'valpolicella', 'amarone'],
     "Italy makes a huge range of wines from hundreds of native grapes. The best known are Chianti "
     "and Brunello from Tuscany (both Sangiovese, savoury and food-friendly), Barolo and Barbaresco "
     "from Piedmont (Nebbiolo — pale but powerful and tannic), Amarone from the Veneto (rich and "
     "raisiny), plus Prosecco and Pinot Grigio. Italian wines are usually built to be drunk with "
     "food, so they tend to have bright acidity."),

    (['napa', 'napa valley', 'california wine', 'californian', 'sonoma',
      'american wine', 'wine from america', 'us wine'],
     "Napa Valley in California is one of the world's most famous wine regions, best known for rich, "
     "ripe, full-bodied Cabernet Sauvignon and buttery, oaked Chardonnay. Its warm climate gives "
     "wines with more fruit, higher alcohol, and softer acidity than European equivalents — a classic "
     "New World style. Neighbouring Sonoma is cooler and does very good Pinot Noir."),

    (['spanish wine', 'wine from spain', 'spain', 'ribera', 'albarino', 'cava'],
     "Spain's signature red grape is Tempranillo, the backbone of Rioja and Ribera del Duero — "
     "smooth, savoury reds often aged in oak, with Rioja labels telling you how long (Crianza, "
     "Reserva, Gran Reserva). Spain also makes Albariño, a crisp coastal white that's excellent "
     "with seafood, and Cava, its traditional-method sparkling wine, which is usually great value."),

    (['wine as a gift', 'gift', 'present', 'what wine to buy someone',
      'buy for someone', 'wine for a gift'],
     "Safe crowd-pleasers make the best gifts: Champagne or a good Cava for a celebration, a "
     "Rioja Reserva or a New Zealand Sauvignon Blanc if you don't know their taste. Choosing "
     "something with a sense of place — a named region rather than a generic label — reads as more "
     "thoughtful than simply spending more. If they cook, a versatile food wine like Chianti is "
     "always welcome."),

    (['bad', 'gone off', 'spoiled', 'spoilt', 'off wine', 'has my wine gone',
      'can wine go bad', 'is my wine still good', 'vinegar'],
     "Yes. An unopened bottle stored badly — upright, warm, or in sunlight — can dry out its cork "
     "and oxidise. Once opened, most wine is past its best after three to five days. Signs it has "
     "gone: a vinegary or nail-polish smell, a flat brown colour, or a wet-cardboard, musty smell "
     "(that last one is 'cork taint' and means the bottle was faulty, not mistreated). Spoiled wine "
     "tastes unpleasant but isn't dangerous."),

    (['thanks', 'thank you', 'cheers', 'appreciate it', 'that helps', 'helpful',
      'bye', 'goodbye', 'see you'],
     "You're very welcome — enjoy the wine! Ask me anything else any time, whether it's picking a "
     "bottle, pairing it with dinner, or understanding what VinoInsight's predictions mean."),
]


# The response used when nothing in the knowledge base matches. It names the
# topic areas so a beginner knows what they can ask next, and is deliberately
# honest about being the offline mode.
FALLBACK_DEFAULT = (
    "I don't have a stored answer for that one — the live AI assistant isn't reachable "
    "right now, so I'm running on my offline wine knowledge base. Try asking about wine "
    "types, grape varieties, taste and aroma, food pairing, serving temperature, storage, "
    "wine regions, how wine is made, wine terminology, or how VinoInsight's predictions work."
)

GREETING = (
    "Hello! I'm the VinoInsight wine assistant. Ask me anything about wine — grape "
    "varieties, wine styles, taste and aroma, food pairing, serving and storage, wine "
    "regions, how wine is made, or how this app's predictions work. No prior wine "
    "knowledge needed."
)
