# -*- coding: utf-8 -*-
"""Shot content r8 — part 2: S06..S10b (进厨房和面 + 母亲独白释放)."""
from common import ZY, MO, CAP, HOME, CORR

KITCHEN = ("the kitchen zone of the family home at night: a long work counter with the dough basin on it, a sink "
 "on Zhou Ye's side of the counter and a stove on the mother's side, the counter running between them; the "
 "kitchen zone follows the home sheet")
HOME_KITCHEN_TABLE = ("the continuous interior of the family home at night from the living-room dining corner to "
 "the kitchen zone: the dining table with its light-blue cloth at one end, the pass-through gap and the "
 "refrigerator between the two areas, the kitchen counter, sink and stove at the other end; the continuous "
 "space follows the home sheet")

P2 = [
# ============================ S06 ============================
dict(sid="S06", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S2", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="home interior from the dining corner to the kitchen",
      zone_text=HOME_KITCHEN_TABLE, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the evening is fully dark "
       "outside, the living room lamp lit, the kitchen light ahead as they move toward it."),
summary=("A video of the two of them moving from the dining table into the kitchen to start making dumplings: the "
         "mother stands and walks to the refrigerator, takes out the bag of flour and the box of minced meat and "
         "turns back, while Zhou Ye asks after her back and rises to meet her at the pass-through, taking the "
         "mixing basin from her hands. Appearances follow <Picture 1> and <Picture 2>, the continuous interior "
         "follows <Picture 3>, and the movement sequence follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium shot begins at the dining table in the living room: the mother and Zhou Ye sit facing each other over "
 "the light-blue tablecloth, then the mother stands up and walks toward the kitchen zone of the home, past the "
 "pass-through gap, to the refrigerator. As she walks Zhou Ye watches her back and asks, concerned (S1) "
 "\"<d>[Chinese] 你不是说腰疼？</d>\". She opens the refrigerator, takes out the bag of flour and the box of "
 "minced meat, and as she turns back she answers, easing his worry (S2) \"<d>[Chinese] 擀几张皮，没事。</d>\" - "
 "her free hand briefly touching her lower back as she turns. Zhou Ye rises and comes to the pass-through to "
 "meet her; she passes him the mixing basin, he receives it in both hands, and together they move on into the "
 "kitchen light, the making of the dumplings begun. The camera follows her walk with a light tracking move and "
 "settles as he receives the basin; the dining corner stays behind them, no flip."))],
sound=("The refrigerator door opening and closing; her light footsteps; the basin set into his hands; their two "
       "short lines of dialogue in the quiet room.")),

# ============================ S07 ============================
dict(sid="S07", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S2", appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit, "
       "the night fully dark outside, the dough work on the counter between them."),
summary=("A video of the two of them kneading dough together in the kitchen for the first time in years: Zhou Ye "
         "with his sleeves rolled up works the dough in the basin at the sink side of the counter, the mother "
         "across from him at the stove side presses the dough to feel its state, tells him there is too much "
         "water, and he adds flour and keeps kneading - the natural division of labor of two people relearning "
         "a familiar rhythm. Appearances follow <Picture 1> and <Picture 2>, the kitchen zone follows "
         "<Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium shot from a slight high angle over the counter: the two face each other across the work counter with "
 "the dough basin between them, Zhou Ye on the sink side with his sleeves rolled up, kneading the dough with "
 "even, rhythmic pressure, the mother on the stove side, her hand pressing the dough to feel its state. She "
 "judges the dough and says plainly (S1) \"<d>[Chinese] 水多了。</d>\"; Zhou Ye looks at the dough under his "
 "hands and answers as he reaches for the flour (S2) \"<d>[Chinese] 我再加面。</d>\". He adds flour and keeps "
 "kneading, his breathing even, the two of them settling into the shared work. The camera stays locked in this "
 "single continuous shot, no cut."))],
sound=("The low sounds of kneading and water in the dough as a floor beneath the two short lines of dialogue.")),

# ============================ S08a ============================
dict(sid="S08a", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S2", appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the counter work continuing between them."),
summary=("A video of the mother opening an old memory while the kneading goes on: she looks down at the dough and "
         "mentions the day he left, the two pairs of socks she packed for him, while Zhou Ye's hands pause a "
         "half-beat in the dough before he answers softly that he remembers - both of them back on that day for a "
         "moment. Appearances follow <Picture 1> and <Picture 2>, the kitchen zone follows <Picture 3>, and the "
         "framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot of the mother at the stove side of the counter, speaking while her hands rest on the rim "
 "of the dough basin; at the near edge of the frame Zhou Ye's hands knead the dough on the sink side, his face "
 "kept out of frame. She looks at the dough, not raising her eyes to him, and begins, the words light and "
 "careful (S1) \"<d>[Chinese] 你走那天，我给你装了两双袜子。</d>\" - the words for the socks coming out "
 "softly. Zhou Ye's kneading hands pause a half-beat in the dough, then resume; from off-frame his voice "
 "answers low and quiet (S2) \"<d>[Chinese] 我记得。</d>\". She keeps her eyes on the dough, the memory "
 "surfacing between them. The camera stays locked in this single continuous shot with a slow push-in toward "
 "her, no cut."))],
sound=("The kneading sounds growing lighter beneath the dialogue; her words about the socks spoken softly.")),

# ============================ S08b ============================
dict(sid="S08b", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the kitchen quiet except for her voice."),
summary=("A video of the mother's monologue over the dough, the grievance held under a calm surface coming out "
         "sentence by sentence: she waited for his calls week after week, alone in the house since his father "
         "passed, not daring to fall ill or fall or sleep too deeply - and unable to tell him any of it, because "
         "he would only worry from far away. Her appearance follows <Picture 2>, the kitchen zone follows "
         "<Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of the mother at the stove side of the counter, her eyes on the dough, her hands resting on the "
 "basin rim, the fingers pressing white at the knuckles. Calmly at first, the grievance pressing up beneath "
 "her flat voice, she speaks (S1) \"<d>[Chinese] 我还以为你会打电话。第一周等，第二周也等。</d>\" - then, "
 "each sentence carrying the next (S1) \"<d>[Chinese] 你爸不在以后，家里就剩我一个人。</d>\" (S1) "
 "\"<d>[Chinese] 我不敢病，不敢摔，不敢晚上睡得太死。</d>\" - her breaths growing shallower between the "
 "words about not daring - and at last, softer, tired (S1) \"<d>[Chinese] 可我又不能跟你说这些。你在外面，听"
 "见了只会分心。</d>\". She looks up toward him once and lets her eyes fall back to the dough; beside her on "
 "the sink side his kneading hands slow. The camera stays locked in this single continuous shot with a slow "
 "push-in toward her, no cut."))],
sound=("The kitchen is quiet, only her breathing and the pauses between her sentences; the kneading sounds fade "
       "nearly to nothing.")),

# ============================ S09a ============================
dict(sid="S09a", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=2, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=3, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the room still around her."),
summary=("A video of the mother telling the softest memory from the night of a blackout: she thought it was him "
         "coming home, and only later remembered - his keys had been with her all along; as she says the words "
         "about the keys her voice breaks and she stops, lowering her head, her hand still resting on the rim of "
         "the dough basin. Her appearance follows <Picture 1>, the kitchen zone follows <Picture 2>, and the "
         "framing follows the storyboard reference <Picture 3>."),
shots=[dict(t=None, body=(
 "A close shot of the mother at the stove side of the counter, her hands on the rim of the dough basin, her "
 "fingers unconsciously tracing the basin edge. She begins, the memory rising (S1) \"<d>[Chinese] 有一次半夜停"
 "电……我以为是你回来了。</d>\" - as she says the words about thinking it was him, her gaze drifts toward the "
 "direction of the front door and then comes back; a half-beat of held breath after the word for the blackout. "
 "Then, quieter, the voice suddenly giving out (S1) \"<d>[Chinese] 后来才想起来，你的钥匙一直在我这儿。</d>\" "
 "- her voice breaks off, she lowers her head and stops, her hand still resting on the basin rim. The camera "
 "stays locked in this single continuous shot with a slow push-in toward her; only her eyes turn toward the "
 "door, her body does not turn, no cut."))],
sound=("The kneading sounds slow and stop; after the words about the keys her voice breaks and leaves a half-beat "
       "of silence.")),

# ============================ S09b ============================
dict(sid="S09b", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the kitchen quiet."),
summary=("A video of the mother putting her wish into words: she knows he has his own life and that his service "
         "was not a game, but she wants him to know someone at home is waiting for him - not asking him back at "
         "once, not asking for promises, only that once in a while he says he is doing well. Her appearance "
         "follows <Picture 2>, the kitchen zone follows <Picture 3>, and the framing follows the storyboard "
         "reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of the mother at the stove side of the counter, her eyes first on the dough, then lifting to "
 "look at Zhou Ye across the counter for one glance before falling back to the dough. Her voice carries both "
 "understanding and the held-back grievance as she speaks (S1) \"<d>[Chinese] 我知道你有你的事。我也知道当兵不"
 "是去玩。</d>\" - then the core of it, the words put out plainly (S1) \"<d>[Chinese] 可我就是想让你知道，家里有"
 "人等你。</d>\" - and at the end, gentle, the request light as a sigh (S1) \"<d>[Chinese] 不是要你马上回来，也不"
 "是要你保证什么。我只是想让你偶尔说一句，你还好。</d>\" - the last three words almost a breath. Across the "
 "counter on the sink side, Zhou Ye's kneading hands stop and rest in the dough. The camera stays locked in "
 "this single continuous shot with a slow push-in toward her, no cut."))],
sound=("The kitchen is quiet; her words carry the room; the kneading has stopped.")),

# ============================ S10a ============================
dict(sid="S10a", subjects=[
 dict(role="mo", pic=1, apron=True, appears=[1]),
 dict(role="space", pic=2, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=3, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the close shot filled with her alone."),
summary=("A video of the mother's grief finally breaking, face to the camera, without turning away: her palm "
         "presses into the dough until the fingers sink in, she wipes her eyes with the hem of her apron and the "
         "tears only come more, until at last both hands brace on the counter edge and she lowers her head, her "
         "shoulders trembling with a suppressed sob. Her appearance follows <Picture 1>, the kitchen zone "
         "follows <Picture 2>, and the framing follows the storyboard reference <Picture 3>."),
shots=[dict(t=None, body=(
 "A close shot of the mother at the stove side of the counter, facing the dough, the tears held back until the "
 "limit gives. Her palm presses into the dough, the fingertips sinking in; she holds her breath to the edge "
 "and lets it out, and wipes her eyes with the hem of her apron - the tears only coming more, her hand pausing "
 "in mid-air. Then both hands brace on the edge of the counter and she lowers her head, her shoulders "
 "trembling, one suppressed sob escaping her as she breathes out. She stays facing the counter throughout, "
 "never turning away, her face visible and broken in the close shot. The camera stays locked in this single "
 "continuous shot with a slow push-in, no cut."))],
sound=("A held breath released; one suppressed sob; the kitchen otherwise silent.")),

# ============================ S10b ============================
dict(sid="S10b", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the water running at the sink."),
summary=("A video of Zhou Ye answering his mother's tears with an action instead of words: he goes to the sink "
         "with his flour-dusted hands, washes them under the tap and turns the water small, pulls out a tissue, "
         "and steps to her side to offer it - she, still facing away at the counter with trembling shoulders, "
         "reaches back and takes it without turning around. Appearances follow <Picture 1> and <Picture 2>, the "
         "kitchen zone follows <Picture 3>, and the action sequence follows the storyboard reference "
         "<Picture 4>."),
shots=[dict(t=None, body=(
 "A medium shot at the sink side of the kitchen counter: the mother stands at the counter with her back to Zhou "
 "Ye, her head lowered, her shoulders trembling, the dough before her. Zhou Ye, his hands dusted with flour, "
 "turns to the sink beside his standing place, no more than a quarter turn, and opens the tap; the water runs "
 "large over his hands, washing the flour away, then he turns it small until only a thin stream and a drip "
 "remain - his fingers giving the handle one extra half-turn. He dries his hands, takes a tissue from the "
 "nearby holder, and steps half a step toward her, holding the tissue out to her hand; without turning around "
 "she reaches a hand back and takes it. He lets out the breath he was holding and stands waiting beside her. "
 "The camera stays locked with a light follow of his movement; her back stays toward him throughout, no "
 "turn, no cut."))],
sound=("The water running large, then small, then only dripping; the rustle of the tissue; her uneven breathing.")),
]
