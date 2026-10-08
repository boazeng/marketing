# -*- coding: utf-8 -*-
"""
The two scripts, as data.

Both address the DEVELOPER -- he is who pays. The young couple and their new
apartment appear as the *result* he delivers, never as the hero. Structure per
the brief: a little pain first, then the benefits.

Nothing here mentions Google Play, and nothing claims compliance with the Sale
Law -- the same two prohibitions that govern every other asset in this folder.

`vo` is what the narrator says, mostly vocalised -- but the rule is not
"niqqud everywhere", and it is not the same rule for both engines.

ElevenLabs reads the niqqud and needs it: unpointed, "בדק" came back as *vedek*
and "מרכז" as the noun *merkaz* instead of the verb *merakez*. Deepdub runs its
own Hebrew diacritiser, and where the two disagree the diacritiser wins -- it
reads the consonant skeleton and re-points it. So a word whose POINTED spelling
is defective loses: `דַּיָּר` has the skeleton דיר, and came back as *dir*. The
niqqud was on the wire -- verified codepoint by codepoint -- and was overruled.

The fix is spelling, not pointing: write those words in ktiv male and unpointed
(`דייר`), leaving a skeleton with only one sensible reading. Words whose full
spelling is still ambiguous keep their niqqud.

Four were caught this way, and all four sounded like different words on the
first take: `דייר` (was דַּיָּר -> dir), `מדווח` (was מְדַוֵּחַ -> madoah),
`מסווג` (was מְסֻוָּג -> misug) and `מתועד` (was מְתֹעָד -> meta'ed). The class
is mechanical -- a holam with no vav, a qubuts, or a consonantal vav that ktiv
male doubles -- so it can be scanned for rather than heard for. Do that before
paying for a take, not after. `visual` is the prompt sent to
the video model.
`card` marks a beat rendered in Chromium instead, where Hebrew type has to be
exact -- video models cannot render readable Hebrew, so anything the viewer
must actually READ is never left to them.
"""

# ---------------------------------------------------------------------------
# Narration engines
#
# Two, and both stay runnable. Deepdub is the current take; ElevenLabs was the
# first and is kept because it is already paid for and because "which one is
# better" is a question you answer by playing them back to back, not by
# remembering. `make_vo.py --engine <name>` picks one, and each writes into its
# own `audio/<engine>/` so switching never re-pays for a take you already have.
# ---------------------------------------------------------------------------

# ElevenLabs -- the first take. One voice per film: GAL narrates "sheket"; ron
# was chosen for "shlita" by ear, he is faster and carries the harder, more
# direct register the control-and-documentation story wants.
ELEVEN_VOICE_BY_SLUG = {
    "sheket": "HCy9u0HRUW3d9Q2Osk04",       # GAL - movie speaker
    "shlita": "xbggSeOFR54UUWAyXu40",       # ron - movie voice
}

# Deepdub -- our own voice prompts, built by clone_voice.py from the ElevenLabs
# take. The catalogue was not an option: a style suffix invented for a speaker
# who does not carry that style comes back 404, and the REST API exposes no
# listing -- `GET /voice` returns only prompts you uploaded yourself. Cloning
# also keeps the thing that was already right. The complaint about the first
# films was the Hebrew accent, never the voices; sampling them and letting
# Deepdub do the pronunciation changes the one without touching the other.
DEEPDUB_VOICE_BY_SLUG = {
    "sheket": "5165a6eb-950e-477e-99c7-50fa178f7640",   # GAL, resampled
    "shlita": "de60d54e-a914-4439-8b17-f1ce0217aa9e",   # ron, resampled
}

# Deepdub uses this for language-specific handling -- for Hebrew, which way to
# resolve an unvocalised word. It is not cosmetic: get it wrong and verbs come
# back inflected for the other gender.
DEEPDUB_GENDER_BY_SLUG = {"sheket": "male", "shlita": "male"}

# Alternative voices, tried without disturbing the ones above. `--take <name>`
# selects one and sends its narration to `audio/deepdub-<name>/`, so an
# experiment can never overwrite an approved take.
#
# `gender` is not decoration: Deepdub uses it to diacritise Hebrew, and it is
# classified from the sample by clone_voice.py rather than assumed.
# Every key is optional: leave one out and the take keeps what the films
# already use. A take that changes only the model keeps both narrators.
DEEPDUB_TAKES = {
    "noa": {
        # cloned from a 62s recording, 2026-09-12
        "voice": "100bce89-4199-4387-b727-8f193bf3ebe0",
        "gender": "female",
    },
}

# How much longer than its natural reading each line should take.
#
# ⚠️ Dormant on the model the films use. dd-etts-3.4 ignores `targetDuration`,
# so make_vo.py sends these only to a model in PACED_MODELS (3.0 today). They
# are kept because the numbers were tuned by ear and are what a paced model
# should be given again; on 3.4 the rhythm is TAIL, below.
#
# Deepdub's default pace is a newsreader's, and these are not news: at 1.0 the
# narrator reaches the end of the sentence before the shot has finished moving.
#
# ⚠️ `tempo` is NOT the control for this. It is accepted, it is silently
# ignored, and two generations of one line at 0.95 and 0.85 came back the same
# length to the millisecond. `targetDuration` is the parameter that works, and
# it takes absolute seconds -- so make_vo.py measures each line once at default
# pace, caches that in `audio/deepdub/natural.json`, and multiplies by these.
#
# Per-beat overrides carry the weight of the beat: the ones that turn the film
# get room to land, and the one already near the length of its clip does not.
# Pace and silence are set together, because they pull opposite ways. Slowing
# the reading to give a line weight makes the narrator sound tired; the weight
# actually comes from the silence AFTER the line, not from the words being
# drawn out. So: read close to natural speed, and hold longer before the cut.
PACE = 1.05

PACE_BY_BEAT = {
    # the reveal, the two turns, and the end lines -- what people remember.
    # Only a little slower than the rest; TAIL_BY_BEAT is what makes them land.
    "a1": 1.20, "a3": 1.15, "a7": 1.20,
    "b3": 1.15, "b7": 1.20,
}

# Air after each line, before the cut -- the silence that carries the rhythm.
#
# It lives here rather than in build.py because it is an editorial decision
# about how the film breathes, not an assembly mechanic. build.py imports it.
#
# ⚠️ It is inside the shot, not between shots: build.py trims each clip to
# `line + tail`. Raising it lengthens every shot, and the fal clips are 5.03s,
# so it trades directly against the picture speed.
TAIL = 0.75

# Empty: every beat now fits its clip at the full hold. It was not always so
# -- a4 ran tight here until it was split in two.
TAIL_BY_BEAT = {}

# Shared visual language, appended to every generation prompt. Keeping it in
# one string is what makes six separate clips look like one film.
LOOK = (
    "Cinematic realistic footage, modern Israeli residential apartment building, "
    "handover of a new apartment. Natural daylight through large windows, warm "
    "neutral palette, soft shadows, shallow depth of field, 35mm lens, subtle "
    "slow camera movement on a gimbal, no text, no captions, no logos, "
    "no on-screen graphics, photorealistic, high detail, calm professional mood."
)

VIDEOS = [
    {
        "slug": "sheket",
        "title": "שקט",
        "hook": "הטלפון מפסיק לצלצל",
        "beats": [
            {
                "id": "a1",
                "vo": "הַטֶּלֶפוֹן שֶׁלְּךָ מְצַלְצֵל. דייר.",
                "visual": "Tight close-up of a smartphone lying face-up on a wooden "
                          "office desk, screen glowing with an incoming call, the phone "
                          "vibrating slightly, rolled building plans and a coffee cup "
                          "softly out of focus behind it, warm desk lamp light, "
                          "shallow depth of field.",
            },
            {
                "id": "a2",
                "vo": "עוֹד דייר. וְאַתָּה כְּבָר לֹא זוֹכֵר מָה נִסְגַּר וּמָה לֹא.",
                "visual": "A man in his forties at a cluttered office desk, rubbing his "
                          "forehead, looking at a spreadsheet on a laptop and a stack of "
                          "printed papers, phone pressed to his shoulder, late afternoon "
                          "light, mild frustration.",
            },
            {"id": "a3", "card": "turn", "vo": "בֶּדֶק עוֹשֶׂה אֶת זֶה אַחֶרֶת."},
            # Two beats, not one. As a single line this ran 5.59s against a
            # 5.03s clip, and build.py had to slow the picture to 0.83x --
            # visible slow motion in the middle of the film. Splitting also
            # reads better: the claim lands, then the proof.
            {
                "id": "a4",
                "vo": "הדייר מדווח לְבַד.",
                "visual": "A young woman in her late twenties in the bright empty "
                          "living room of a brand new apartment, holding her smartphone "
                          "up close to a window frame at eye level, her partner behind "
                          "her looking on, moving boxes on the floor, warm daylight. "
                          "No camera equipment, no tripod, no film crew.",
            },
            {
                "id": "a4b",
                "vo": "קִישּׁוּר אֶחָד לַדִּירָה, בְּלִי הוֹרָדָה וּבְלִי סִיסְמָה.",
                # Her hands and the phone, nothing to read. The screen is
                # turned away on purpose -- a generated interface in Hebrew
                # comes back as letter-shaped noise, and this beat is about
                # how little there is to do, not about what is on the screen.
                "visual": "Close-up of a young woman's hands holding a smartphone in "
                          "a bright new apartment, her thumb moving on the screen, the "
                          "screen angled away from view, a sunlit window and stacked "
                          "moving boxes soft in the background, unhurried, warm "
                          "daylight, shallow depth of field.",
            },
            {
                "id": "a5",
                "vo": "הוּא רוֹאֶה שֶׁהַתַּקָּלָה נִפְתְּחָה. הוּא רוֹאֶה שֶׁהִיא נִסְגְּרָה.",
                "visual": "Over-the-shoulder shot of a young woman in a new apartment "
                          "looking at her phone with a calm satisfied expression, "
                          "her partner walking past carrying a cardboard box, "
                          "bright modern interior, soft focus background.",
            },
            {
                "id": "a6",
                "vo": "וְאַתָּה לֹא צָרִיךְ לַעֲנוֹת.",
                "visual": "A calm man in his forties in a tidy office, closing a laptop "
                          "and looking out of a window at a residential building under "
                          "soft evening light, relaxed posture, quiet confident mood.",
            },
            {"id": "a7", "card": "end", "vo": "בֶּדֶק. הַשֶּׁקֶט חוֹזֵר אֵלֶיךָ."},
        ],
    },
    {
        "slug": "shlita",
        "title": "שליטה",
        "hook": "כל הפרויקטים במסך אחד",
        "beats": [
            {
                "id": "b1",
                "vo": "כַּמָּה תַּקָּלוֹת פְּתוּחוֹת לְךָ עַכְשָׁיו?",
                "visual": "Wide shot of a modern residential building exterior at "
                          "golden hour, several balconies, a delivery van parked below, "
                          "slow push-in, clean architectural lines.",
            },
            {
                "id": "b2",
                "vo": "מִי מֵהַקַּבְּלָנִים בְּפִיגּוּר? וּמָה נֶאֱמַר לדייר לִפְנֵי שָׁנָה?",
                "visual": "Two men in an unfinished apartment, one in a hard hat holding "
                          "a clipboard, the other pointing at a wall, both looking "
                          "uncertain, bare concrete and plaster, harsh work light, "
                          "documents scattered on a folding table.",
            },
            {"id": "b3", "card": "turn", "vo": "אִם אַתָּה צָרִיךְ לְחַפֵּשׂ — אֵין לְךָ שְׁלִיטָה."},
            {
                "id": "b4",
                "vo": "בֶּדֶק מְרַכֵּז אֶת כָּל הַפְּרוֹיֶקְטִים בְּמָסָךְ אֶחָד.",
                "visual": "A woman in a bright modern office studying a large monitor, "
                          "confident posture, floor to ceiling window behind her "
                          "overlooking residential buildings, clean minimal desk, "
                          "morning light.",
            },
            {
                "id": "b5",
                "vo": "הַמְּפַקֵּחַ סוֹגֵר מֵהַשֶּׁטַח, עִם תְּמוּנוֹת וַחֲתִימָה.",
                "visual": "A site inspector in a safety vest standing inside a finished "
                          "apartment, holding a phone at chest height and photographing "
                          "a door frame, natural window light, focused and unhurried.",
            },
            {
                "id": "b6",
                "vo": "וְדוֹחַ בֶּדֶק שֶׁאַתָּה מַעֲלֶה, נִקְרָא וְנִכְנָס מסווג. לְבַד.",
                "visual": "Close shot of hands placing a printed report on a desk beside "
                          "a laptop in a bright office, shallow depth of field, "
                          "warm daylight, calm and orderly.",
            },
            {"id": "b7", "card": "end", "vo": "בֶּדֶק. הַכֹּל מתועד."},
        ],
    },
]
