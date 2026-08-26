# -*- coding: utf-8 -*-
"""
The two scripts, as data.

Both address the DEVELOPER -- he is who pays. The young couple and their new
apartment appear as the *result* he delivers, never as the hero. Structure per
the brief: a little pain first, then the benefits.

Nothing here mentions Google Play, and nothing claims compliance with the Sale
Law -- the same two prohibitions that govern every other asset in this folder.

`vo` is what the narrator says, FULLY VOCALISED. Hebrew without niqqud is
ambiguous to the engine and it guesses badly -- "בדק" came back as *vedek*, and
"מרכז" would read as the noun *merkaz* instead of the verb *merakez*. Same fix
that made TACT pronounce correctly as בְּטַאקְט. Keep the niqqud on any word
whose consonant skeleton has more than one reading. `visual` is the prompt sent to the video model.
`card` marks a beat rendered in Chromium instead, where Hebrew type has to be
exact -- video models cannot render readable Hebrew, so anything the viewer
must actually READ is never left to them.
"""

# One voice per film. GAL narrates "shalom"; ron was chosen for "shlita" by
# ear -- he is faster and carries the harder, more direct register the
# control-and-documentation story wants.
VOICE_GAL = "HCy9u0HRUW3d9Q2Osk04"          # GAL - movie speaker
VOICE_RON = "xbggSeOFR54UUWAyXu40"          # ron - movie voice

VOICE_BY_SLUG = {"sheket": VOICE_GAL, "shlita": VOICE_RON}

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
                "vo": "הַטֶּלֶפוֹן שֶׁלְּךָ מְצַלְצֵל. דַּיָּר.",
                "visual": "Tight close-up of a smartphone lying face-up on a wooden "
                          "office desk, screen glowing with an incoming call, the phone "
                          "vibrating slightly, rolled building plans and a coffee cup "
                          "softly out of focus behind it, warm desk lamp light, "
                          "shallow depth of field.",
            },
            {
                "id": "a2",
                "vo": "עוֹד דַּיָּר. וְאַתָּה כְּבָר לֹא זוֹכֵר מָה נִסְגַּר וּמָה לֹא.",
                "visual": "A man in his forties at a cluttered office desk, rubbing his "
                          "forehead, looking at a spreadsheet on a laptop and a stack of "
                          "printed papers, phone pressed to his shoulder, late afternoon "
                          "light, mild frustration.",
            },
            {"id": "a3", "card": "turn", "vo": "בֶּדֶק עוֹשֶׂה אֶת זֶה אַחֶרֶת."},
            {
                "id": "a4",
                "vo": "הַדַּיָּר מְדַוֵּחַ לְבַד. קִישּׁוּר אֶחָד לַדִּירָה, בְּלִי הוֹרָדָה וּבְלִי סִיסְמָה.",
                "visual": "A young woman in her late twenties in the bright empty "
                          "living room of a brand new apartment, holding her smartphone "
                          "up close to a window frame at eye level, her partner behind "
                          "her looking on, moving boxes on the floor, warm daylight. "
                          "No camera equipment, no tripod, no film crew.",
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
                "vo": "מִי מֵהַקַּבְּלָנִים בְּפִיגּוּר? וּמָה נֶאֱמַר לַדַּיָּר לִפְנֵי שָׁנָה?",
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
                "vo": "וְדוֹחַ בֶּדֶק שֶׁאַתָּה מַעֲלֶה, נִקְרָא וְנִכְנָס מְסֻוָּג. לְבַד.",
                "visual": "Close shot of hands placing a printed report on a desk beside "
                          "a laptop in a bright office, shallow depth of field, "
                          "warm daylight, calm and orderly.",
            },
            {"id": "b7", "card": "end", "vo": "בֶּדֶק. הַכֹּל מְתֹעָד."},
        ],
    },
]
