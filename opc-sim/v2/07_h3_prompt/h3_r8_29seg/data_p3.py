# -*- coding: utf-8 -*-
"""Shot content r8 — part 3: S11a1..S17 (和解、包饺、钥匙、终场)."""
from common import ZY, MO, CAP, HOME, CORR

KITCHEN = ("the kitchen zone of the family home at night: a long work counter with the dough basin on it, a sink "
 "on Zhou Ye's side of the counter and a stove on the mother's side, the counter running between them; the "
 "kitchen zone follows the home sheet")
DINING_LATE = ("the living-room dining corner of the family home late at night: the rectangular wooden dining "
"table with its light-blue cloth, two chairs facing each other across it, the table lamp lit, and a potted "
"plant on the windowsill; the corner follows the home sheet")
HOME_KITCHEN_TABLE = ("the continuous interior of the family home at night from the living-room dining corner to "
"the kitchen zone: the dining table with its light-blue cloth at one end, the pass-through gap and the "
"refrigerator between the two areas, the kitchen counter, sink and stove at the other end; the continuous "
"space follows the home sheet")

P3 = [
# ============================ S11a1 ============================
dict(sid="S11a1", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the water no longer running, the room very still."),
summary=("A video of Zhou Ye speaking to his mother's back: standing half a step behind her at the counter, he "
         "calls out softly - Ma - and when she does not turn, after one held beat, he says the apology he owes "
         "her, word by word, low - I am sorry - the last syllable trembling slightly, his hand at his side "
         "clenching and loosening once as he waits for her. His appearance follows <Picture 1>, the mother's "
         "back follows <Picture 2>, the kitchen zone follows <Picture 3>, and the framing follows the storyboard "
         "reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of Zhou Ye as he stands half a step behind the mother at the sink side of the counter, speaking "
 "to her back; her back and the far edge of the counter fill the far side of the frame, the tissue still in "
 "her hand, her shoulders settling. He looks at the line of her shoulders and calls out softly, carefully "
 "(S1) \"<d>[Chinese] 妈。</d>\". She does not turn. He waits one held beat, then speaks again, the words put "
 "down low, one by one (S1) \"<d>[Chinese] 对不起。</d>\" - the last syllable carrying a faint tremor. His hand "
 "at his side clenches once and loosens; he stands still, watching her shoulder line, waiting for her. The "
 "camera stays locked in this single continuous shot, no cut."))],
sound=("A quiet silence between the soft call and the apology; the room's low hum; his breathing.")),

# ============================ S11a2 ============================
dict(sid="S11a2", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1]),
 dict(role="zy", pic=2, indoor=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the close shot on her face as she looks back."),
summary=("A video of the mother turning her head toward the apology: the word reaches her and her shoulders "
         "pause, the tissue still clutched in her hand; she looks back over her shoulder at Zhou Ye half a step "
         "behind her, her eyes red, her gaze softening before her voice, and answers hoarse and low - do not "
         "say you are sorry the moment you come home - gently turning the words away. Her appearance follows "
         "<Picture 1>, the kitchen zone follows <Picture 3>, and the framing follows the storyboard reference "
         "<Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of the mother from the sink side, her face caught as she looks back over her shoulder; the "
 "apology lands and her shoulders pause, the tissue still clutched in her hand, a faint rustle from her "
 "fingers. She turns her head toward Zhou Ye standing half a step behind her, no more than a turn of the head, "
 "her body still facing the counter; her eyes are red, and they soften before her voice does. She draws a "
 "breath to press the crying down and answers, hoarse and low, gently pushing the words back (S1) "
 "\"<d>[Chinese] 别一回来就说对不起。</d>\" - her grip on the tissue not letting go. The camera stays locked "
 "in this single continuous shot, no cut."))],
sound=("A rustle of the tissue in her hand; her hoarse low answer; the kitchen quiet around her voice.")),

# ============================ S11b1 ============================
dict(sid="S11b1", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the two of them still in their places at the counter."),
summary=("A video of Zhou Ye explaining himself to his mother's lowered head: he takes up her words, his voice "
         "hurrying a beat before he steadies it - it was never because she waited; he thought not telling her "
         "was how he set her mind at ease, taking care of himself so she would not worry - but he understands "
         "now that what she wanted to know was never only whether he was hurt; the last sentence stops him, and "
         "he waits. His appearance follows <Picture 1>, the kitchen zone follows <Picture 3>, and the framing "
         "follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of Zhou Ye standing half a step behind the mother, speaking to her back; she faces the counter "
 "before her, listening, her head slowly lowering as she hears him out. He takes up her words, his voice "
 "hurrying a beat before he steadies it, the whole confession coming out in one push as if held for a long "
 "time (S1) \"<d>[Chinese] 不是因为你等我。是我以为不说就算是让你放心。</d>\" (S1) \"<d>[Chinese] 我把自己照"
 "顾好，就觉得你也会放心。</d>\" - he draws one breath and presses on, the core of it (S1) \"<d>[Chinese] 可你"
 "不是只想知道我有没有受伤。</d>\". At the last sentence he stops, his throat working once; he looks at the "
 "back of her lowered head and waits for her to take it in. The camera stays locked in this single continuous "
 "shot, no cut."))],
sound=("The dialogue leads, the pauses between his sentences short; her listening silence; the room low.")),

# ============================ S11b2 ============================
dict(sid="S11b2", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the close shot on his face as he speaks to her back."),
summary=("A video of Zhou Ye saying what he has never said: with his mother's back bowed over the counter before "
         "him, he admits he missed her too - seeing other people call home when he was away made him think of "
         "her, yet when he wanted to call he never knew which sentence to start with, and the longer he put it "
         "off the less he knew; the words about missing her make his breath catch once, and he stops at the end, "
         "not urging her to turn. His appearance follows <Picture 1>, the kitchen zone follows <Picture 3>, and "
         "the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of Zhou Ye's face at the sink side of the counter; before him the mother's back stays bowed "
 "toward the dough, her shoulder line unmoving, the tissue still in her hand. He looks at her back and goes "
 "on, his voice quiet and level, the words he has carried coming out at last (S1) \"<d>[Chinese] 我也想你。在"
 "外面看见别人打电话回家，我会想起你。</d>\" - at the words about missing her his breath breaks one beat - "
 "(S1) \"<d>[Chinese] 想打的时候，又不知道该从哪句开始。后来拖着拖着，就更不知道了。</d>\" - the tail "
 "sinking lower, his finger at his side curling once at the last words. He stops and does not urge her to turn "
 "around. The camera stays locked in this single continuous shot, no cut."))],
sound=("The dialogue leads against a very low room tone; one intake of breath before the words about missing "
       "her.")),

# ============================ S11c1 ============================
dict(sid="S11c1", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1]),
 dict(role="zy", pic=2, indoor=True, sid="S2", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, mother and son facing each other across the counter."),
summary=("A video of the mother asking for the concrete promise: turned back to face Zhou Ye across the counter, "
         "her eyes still red, she asks in a tight voice - and what about you, afterwards - and when he answers "
         "from across the counter that he will tell her from now on, she pauses a beat, then asks the two words "
         "very lightly, her eyes straight on him without blinking - every day? Her appearance follows "
         "<Picture 1>, the kitchen zone follows <Picture 3>, and the framing follows the storyboard reference "
         "<Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of the mother from the sink side of the counter, facing Zhou Ye across the counter; her eyes "
 "are still red, her hands resting before her. She asks first, her voice tight (S1) \"<d>[Chinese] 那你以后"
 "呢？</d>\". From across the counter Zhou Ye answers as an off-frame voice, steady and plain (S2) "
 "\"<d>[Chinese] 以后我说。</d>\" - the four words landing, and she pauses a beat at them. Then, very lightly, "
 "the two words put out as her own request, her eyes on him without blinking, the breath held until they are "
 "out (S1) \"<d>[Chinese] 每天？</d>\" - her hand at her front gathering the edge of her apron for a moment as "
 "she asks, then letting it go. The camera stays locked in this single continuous shot, no cut."))],
sound=("Half a beat of quiet between each of the three lines; the last two words spoken lightly; the room low.")),

# ============================ S11c2 ============================
dict(sid="S11c2", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1,2]),
 dict(role="mo", pic=2, apron=True, appears=[1,2]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the reconciliation drawing close."),
summary=("A video of the promise that settles the night: Zhou Ye meets her eyes and gives her his word - he "
         "cannot promise to speak every single day, but he will not make her guess anymore; the mother walks "
         "around the end of the counter to stand before him, looks up at him, and lifts her hand to touch the "
         "side of his face, her fingertips light - the touch landing as the shot holds. Appearances follow "
         "<Picture 1> and <Picture 2>, the kitchen zone follows <Picture 3>, and the two-stage sequence follows "
         "the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "A medium shot of Zhou Ye at the sink side of the counter, the mother across the counter at the stove side, "
  "her eyes still red. He meets her gaze and gives her his word, steady and unhurried (S1) \"<d>[Chinese] 不一"
  "定每天都能说，但我不再让你猜。</d>\" - the promise landing; he lets out a long breath. She leaves her place, "
  "walks around the end of the counter and comes to stand before him, closing the space between them, her "
  "steps unhurried; he watches her come.")),
 dict(t=4.3, body=(
  "a close shot of the two of them face to face: she looks up at him, raises her hand, and her fingertips come "
  "to rest very lightly against the side of his face - the touch landing, and the shot holds there an instant "
  "before the segment ends."))],
sound=("A beat of silence, then the two of them breathing; her footsteps crossing the kitchen floor.")),

# ============================ S12 ============================
dict(sid="S12", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1,2]),
 dict(role="zy", pic=2, indoor=True, sid="S2", appears=[1,2]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=KITCHEN, appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the reconciliation settling into the evening's work."),
summary=("A video of the moment passing into the ordinary: her fingertips rest on his cheek a half-beat longer, "
         "then she withdraws her hand and turns back to the counter, grounding them with the words that the "
         "dough is not finished yet; Zhou Ye steps to the counter and takes over the kneading with a single "
         "word - I will - and the two of them return to their places at the counter, each letting out a breath. "
         "Appearances follow <Picture 1> and <Picture 2>, the kitchen zone follows <Picture 3>, and the "
         "two-stage sequence follows the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "A close shot holding the match-on-action from the previous instant: the mother's fingertips still rest "
  "against the side of Zhou Ye's face; they stay a half-beat, then withdraw, her hand coming back to her side. "
  "She turns back toward the counter, grounding them both, and says, low and level (S1) \"<d>[Chinese] 面还没和"
  "好。</d>\".")),
 dict(t=3.4, body=(
  "a medium shot at the counter: Zhou Ye steps forward to the main position at the sink side, puts his hands "
  "to the dough in the basin and takes over the kneading, saying simply (S2) \"<d>[Chinese] 我来。</d>\"; the "
  "mother stands at the stove side, and the two of them settle back into the division of the work, each letting "
  "out a breath as the dough comes alive under his hands."))],
sound=("A soft sound of the basin as the kneading resumes; the two short lines; the room quiet and warm.")),

# ============================ S13 ============================
dict(sid="S13", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1]),
 dict(role="zy", pic=2, indoor=True, sid="S2", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=("the kitchen zone of the family home at night, the work counter laid with the rolling pin, the "
                 "dough pieces, the filling and a tray, the mother at the stove side, Zhou Ye at the sink side, "
                 "facing each other across the board; the kitchen zone follows the home sheet"),
      appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, a high angle over the dumpling work on the board."),
summary=("A video of the mother teaching Zhou Ye to fold dumplings, hands in close view over the board: she "
         "demonstrates - wrapper in the palm, filling in the center, fold and pinch - and he follows, his three "
         "attempts coming closer each time, uneven, then too tight, then standing firm; she tells him the third "
         "one will do, answers his question that it is barely passing, and when he asks her to teach him the "
         "work goes on between them. Appearances follow <Picture 1> and <Picture 2>, the work counter follows "
         "<Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot from a high angle over the board, the hands and forearms of the two of them in the "
 "frame, the mother at the stove side, Zhou Ye at the sink side, the rolling pin, dough pieces and a bowl of "
 "filling between them. She lays a wrapper in her palm and demonstrates - filling in the center, the wrapper "
 "folded, the edge pinched shut with steady wrists - and says (S1) \"<d>[Chinese] 你擀皮，我包。</d>\"; he "
 "answers (S2) \"<d>[Chinese] 好。</d>\" and sets to work, watching her hands and then his own. His three "
 "attempts come closer each time: the first uneven, the second pinched too tight, and the third standing firm "
 "on the board, made with his breath held. She takes it in and says, approving (S1) \"<d>[Chinese] 这个可"
 "以。</d>\"; he asks (S2) \"<d>[Chinese] 及格了？</d>\"; she answers, not letting him off (S1) "
 "\"<d>[Chinese] 还早。</d>\"; and he asks, learning (S2) \"<d>[Chinese] 那你教我。</d>\". The camera stays "
 "locked in this single continuous shot, no cut."))],
sound=("The small soft sounds of wrapper and filling under their hands beneath the dialogue.")),

# ============================ S14 ============================
dict(sid="S14", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S2", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home",
      zone_text=("the kitchen zone of the family home at night, the work counter laid with the board, the tray "
                 "of folded dumplings and the last of the filling, the mother at the stove side, Zhou Ye at the "
                 "sink side, facing each other across the board; the kitchen zone follows the home sheet"),
      appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, the folding of dumplings turning into easy household talk."),
summary=("A video of the two of them finishing the dumplings in easy talk: Zhou Ye puts his misshapen dumpling "
         "before his mother, claiming it for himself, while she re-presses its pleats and lines it up on the "
         "tray; he asks whether they will make dumplings tomorrow and the day after, and she answers - noodles "
         "tomorrow, and the day after we will see - as the last of the filling is scraped clean. Appearances "
         "follow <Picture 1> and <Picture 2>, the work counter follows <Picture 3>, and the framing follows the "
         "storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium shot over the counter, the two of them facing each other across the board, the tray of folded "
 "dumplings between them, the last of the filling in its bowl. Zhou Ye sets his one misshapen dumpling down "
 "before his mother and says, claiming it (S1) \"<d>[Chinese] 这个归我自己吃。</d>\"; she re-presses its "
 "pleats unhurriedly and lines it up on the tray (S2) \"<d>[Chinese] 够两个人吃了。</d>\". He asks, lighter "
 "now (S1) \"<d>[Chinese] 妈，明天还包吗？</d>\"; she answers as she scrapes the last of the filling from the "
 "bowl (S2) \"<d>[Chinese] 明天吃面。</d>\"; he tries again (S1) \"<d>[Chinese] 后天呢？</d>\"; she answers, "
 "the tray lined up with small gaps between the dumplings (S2) \"<d>[Chinese] 后天再说。</d>\". He steals a "
 "look at her as she works. The camera stays locked in this single continuous shot with the slightest shift, "
 "no cut."))],
sound=("The low muffled sound of the rolling pin and the soft scrape of the filling beneath the easy dialogue.")),

# ============================ S15 ============================
dict(sid="S15", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1,2]),
 dict(role="mo", pic=2, apron=True, appears=[1,2]),
 dict(role="space", pic=3, img=HOME, zone_label="kitchen zone of the family home, at the stove",
      zone_text=("the kitchen zone of the family home at night, the stove with its pot of boiling water, the "
                 "counter, and the window beginning to fog with steam, the mother at the stove side and Zhou Ye "
                 "beside her; the kitchen zone follows the home sheet"),
      appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the kitchen lamp is lit "
       "at night, white steam rising from the pot and beginning to fog the window."),
summary=("A video of the dumplings going into the pot: Zhou Ye carries the tray to the stove, the water boils, "
         "the dumplings go in and float up, and then, in close view, he picks one out, blows it cool, and "
         "places it into his mother's bowl - her brow knitting as if to say she could manage, yet her hand "
         "receiving it steadily, the small settlement of the whole evening in a bowl. Appearances follow "
         "<Picture 1> and <Picture 2>, the stove zone follows <Picture 3>, and the two-stage sequence follows "
         "the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "A medium shot at the stove: Zhou Ye carries the tray of folded dumplings to the stove where the mother "
  "stands at the stove side; the water in the pot boils, he slides the dumplings in, and they sink and then "
  "float up one by one, the white steam rising and beginning to fog the window; the two of them watch the pot "
  "together, his serious care as he blows nothing yet - the work of the evening settling into the pot.")),
 dict(t=7.2, body=(
  "a close shot of the bowl and the hands: Zhou Ye lifts one dumpling out with the strainer, blows on it "
  "carefully until it is cool, and places it into the bowl before his mother; her brow knits faintly as if to "
  "say she could manage on her own, yet her hand comes forward and receives the bowl steadily; he turns the "
  "fire low to keep the pot at a simmer. The shot holds on the bowl with the single dumpling and her steady "
  "hand."))],
sound=("The water boiling; the strainer meeting the pot's rim; the small sounds of the kitchen at work.")),

# ============================ S16 ============================
dict(sid="S16", subjects=[
 dict(role="mo", pic=1, apron=True, sid="S1", appears=[1,2]),
 dict(role="zy", pic=2, indoor=True, sid="S2", appears=[1,2]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home, late at night",
      zone_text=DINING_LATE, appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; late at night after the "
       "meal, the dining lamp lit over the table, the blue cloth and the empty bowls between them."),
summary=("A video of the handing over of the keys across the dining table, late at night: the mother says to "
         "start eating and, as they do, pushes the keys on the table corner toward Zhou Ye, telling him not to "
         "forget them again; he answers that he will not, closes his hand over the keys, holds them a moment, "
         "and tucks them into his pocket - the whole film's key object coming home. Appearances follow "
         "<Picture 1> and <Picture 2>, the dining corner follows <Picture 3>, and the two-stage sequence "
         "follows the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "A medium shot across the dining table late at night, the two of them seated facing each other, the empty "
  "bowls before them. The mother says (S1) \"<d>[Chinese] 先吃饭。</d>\"; Zhou Ye answers (S2) "
  "\"<d>[Chinese] 好。</d>\" and picks up his chopsticks; she reaches out and pushes the set of door keys lying "
  "on the corner of the table toward his side, saying, her tone level (S1) \"<d>[Chinese] 别又忘了带。</d>\".")),
 dict(t=6.3, body=(
  "a very close shot of the keys and the hands: the keys slide across the blue cloth and come to rest toward "
  "him; Zhou Ye's palm opens beneath them, closes over them, holds them a moment with a light squeeze, and "
  "then tucks them into his jacket pocket, answering simply (S2) \"<d>[Chinese] 不会。</d>\" - the keys "
  "settling into the pocket, the small click of metal against cloth the only sound."))],
sound=("The light sound of the keys against the table; the four short lines of dialogue in the quiet night.")),

# ============================ S17 ============================
dict(sid="S17", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1,2]),
 dict(role="mo", pic=2, apron=True, appears=[1,2]),
 dict(role="space", pic=3, img=HOME, zone_label="home interior from the dining corner to the kitchen, late at night",
      zone_text=HOME_KITCHEN_TABLE, appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; late at night after the "
       "meal, the kitchen lamp lit, the window still fogged from the steam."),
summary=("A video of the night closing quietly: Zhou Ye carries the two empty bowls and follows the mother into "
         "the kitchen; she turns off the fire at the stove, he sets the bowls gently into the sink with a soft "
         "click, and the soup in the pot shudders once and slowly stills; then he turns on the tap and the two "
         "of them stand side by side, sleeves rolled, washing the dishes in rhythm, no one speaking - the "
         "kitchen lamp on, the window fog unmelted, the landing outside the door dark all night with no "
         "footsteps. Appearances follow <Picture 1> and <Picture 2>, the continuous interior follows "
         "<Picture 3>, and the two-stage sequence follows the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "A medium shot follows the two of them in the same direction from the dining corner into the kitchen zone: "
  "Zhou Ye carries the two empty bowls, half a step behind the mother; she reaches the stove and turns off the "
  "fire, the flame dying under the pot; he steps to the sink, sets the two bowls gently into it - the bowl "
  "bottoms meeting the metal with one soft click - and in the pot the soup with its two remaining dumplings "
  "shudders once and slowly stills.")),
 dict(t=6.3, body=(
  "a wide shot of the kitchen as the night settles: Zhou Ye turns on the tap and the water runs; the two of "
  "them roll their sleeves to the forearms and stand side by side at the sink washing the bowls and the pot "
  "in rhythm, unhurried, no one speaking, only the water; the shot holds to the end - the kitchen lamp on, "
  "the fog still on the window, mother and son side by side at the sink as the night goes quiet around them."))],
sound=("The fire clicking off; the soft click of the bowl bottoms in the sink; the water running as the washing "
       "begins; no footsteps from the landing outside all night.")),
]
