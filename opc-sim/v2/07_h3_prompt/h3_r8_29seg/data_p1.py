# -*- coding: utf-8 -*-
"""Shot content r8 — part 1: S01..S05b3 (门口玄关 + 客厅餐桌对白)."""
from common import ZY, MO, CAP, HOME, CORR

HOME_DINING = ("the living-room dining corner of the family home at night: a rectangular wooden dining table "
 "covered with a light-blue cloth, two chairs facing each other across it, and a potted plant on the windowsill; "
 "the corner follows the home sheet")

P1 = [
# ============================ S01 ============================
dict(sid="S01", subjects=[
 dict(role="zy", pic=1, indoor=False, appears=[1]),
 dict(role="space", pic=2, img=CORR, zone_label="dim stairwell landing outside the family front door",
      zone_text=("the dim top-floor stairwell landing outside the family home's front door at dusk, the closed "
                 "front door directly before Zhou Ye, the last two steps descending beside him, and the dark dome "
                 "of the sensor lamp overhead; the landing and the door follow the corridor sheet"),
      appears=[1]),
 dict(role="board", pic=3, appears=[1]),
 dict(role="cap", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the stairwell landing is "
       "dim at dusk, lit only by one sensor lamp that dies out as he stands still."),
summary=("A video of Zhou Ye, wearing his deep-navy cap and holding his dark canvas backpack by its top handle, "
         "standing alone outside his own front door on the dim landing at dusk, the lamp going dark, his raised "
         "hand pausing and loosening before he knocks twice, restrained and clear, then lets his hand drop and "
         "waits. His appearance and the cap follow <Picture 1> and <Picture 4>, the space follows <Picture 2>, and "
         "the state sequence follows the storyboard reference <Picture 3>."),
shots=[dict(t=None, body=(
 "A medium shot holds Zhou Ye standing sideways to the closed front door of his own home, the door panel directly "
 "before him, his dark canvas backpack held by its top handle in his hand at his side, the deep-navy plain cap "
 "with its curved brim on his head, his face composed and restrained. The sensor lamp above flickers as he "
 "arrives, then dies out as he stands still, the faint hum of its current fading; he stares at the door panel, "
 "then his gaze unfocuses on the door seam. He holds his breath for half a beat; his hand rises toward the door, "
 "stops, closes into a loose fist, opens again; his knuckles press lightly against the wood and pull away; the "
 "hesitation piles up and settles; he takes a short breath and knocks twice - restrained, clear - then lets his "
 "hand fall and stands waiting, his eyes steady on the door. The camera stays locked in this single continuous "
 "shot with an extremely slow push-in toward him; he never turns from the door; no cut."))],
sound=("The stairwell current hum fades as the sensor lamp dies out; two restrained knocks against the door panel; "
       "then near silence, his breathing barely audible.")),

# ============================ S02 ============================
dict(sid="S02", subjects=[
 dict(role="zy", pic=1, indoor=False, sid="S1", appears=[1,2]),
 dict(role="mo", pic=2, apron=False, appears=[1]),
 dict(role="space", pic=3, img=CORR, zone_label="doorway gap between the dim landing and the lit foyer",
      zone_text=("the doorway gap between the dim stairwell landing and the lamp-lit entry foyer of the family "
                 "home: Zhou Ye stands on the landing side facing the gap, the mother stands inside on the foyer "
                 "side facing the gap, the warm light of the foyer spilling through the crack across him; the "
                 "landing, the door and the light band follow the corridor sheet"),
      appears=[1,2]),
 dict(role="board", pic=4, appears=[1,2]),
 dict(role="cap", pic=5, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; at dusk on the dim landing, "
       "a warm band of foyer light cuts through the door crack and falls across his face."),
summary=("A video of the first gaze between mother and son through the door opened a crack: she sees his cap brim "
         "first, then his face, and looks him over slowly - brim, brow, shoulder, the hand holding the bag - while "
         "he takes off his cap, lifts his eyes to hers, and calls out in a low restrained voice. Appearances "
         "follow <Picture 1> and <Picture 2>, the gap and light follow <Picture 3>, the cap follows <Picture 5>, "
         "and the two-stage state sequence follows the storyboard reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "The front door opens a crack from inside, the warm light of the foyer widening across the dim landing. "
  "A medium shot holds the gap between them: inside, the mother stands with her hand on the door handle, her body "
  "still, her face appearing in the gap; outside, Zhou Ye stands facing the door, the deep-navy cap with its "
  "curved brim on his head. She sees the brim of his cap first, then his face, and her gaze moves slowly, "
  "carefully, from his brow down to his shoulder and to the hand that holds his dark canvas backpack; she looks "
  "him over without moving, her hand unmoving on the handle, her expression kept calm while recognition rises in "
  "her eyes. Neither crosses the door plane.")),
 dict(t=4.4, body=(
  "a close shot of Zhou Ye through the doorway gap, warm light on his face. He lifts his hand, takes off the cap, "
  "and lowers it to his side, held by its brim; he draws half a breath and raises his eyes to meet hers through "
  "the gap, his throat tight; in a low, restrained voice he calls out (S1) \"<d>[Chinese] 妈。</d>\" - one quiet "
  "call, held back and clear - then waits, the cap hanging at his side, his eyes not leaving hers."))],
sound=("A faint hinge sound as the door opens a crack; the barest rustle of fabric as he takes off the cap; one "
       "restrained low call; the low hum of the foyer light beyond the gap.")),

# ============================ S03 ============================
dict(sid="S03", subjects=[
 dict(role="zy", pic=1, indoor=False, sid="S2", appears=[1,2,3]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1,2,3]),
 dict(role="space", pic=3, img=HOME, zone_label="entry foyer of the family home",
      zone_text=("the entry foyer just inside the family home's front door at night: the front door, the wall "
                 "space beside it where he sets his bag, and the wooden shoe cabinet where he sets his cap and "
                 "arranges his shoes; the foyer follows the home sheet"),
      appears=[1,2,3]),
 dict(role="board", pic=4, appears=[1,2,3]),
 dict(role="cap", pic=5, appears=[1,2]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the foyer is lit warm at "
       "night, dusk fully fallen outside the closed door."),
summary=("A video of him coming home: Zhou Ye steps inside, sets his backpack against the wall, sets his cap onto "
         "the shoe cabinet, takes off his shoes and arranges them, while the mother watches and then reaches out "
         "through his sleeve to press his forearm once - the first touch of their reunion - exchanging two quiet "
         "words; she then turns to close the door, pushing the latch bolt twice before it catches, and he waits in "
         "the foyer without urging her. Appearances follow <Picture 1> and <Picture 2>, the space follows "
         "<Picture 3>, the cap follows <Picture 5>, and the three-stage action sequence follows the storyboard "
         "reference <Picture 4>."),
shots=[
 dict(t=None, body=(
  "The mother pulls the door fully open and steps aside to let him in. A medium shot follows Zhou Ye as he walks "
  "into the foyer, his cap still in his hand; he sets his dark canvas backpack against the wall beside the door, "
  "sets the cap onto the wooden shoe cabinet, then takes off his shoes and arranges them neatly. The mother "
  "stands beside the doorway watching him the whole while, her eyes on his shoulder and arm.")),
 dict(t=5.6, body=(
  "a close shot of mother and son at arm's length: as he straightens up, she steps close and reaches out, "
  "touching his forearm through the thin fabric of his sleeve, pressing once, holding for a moment, her relief "
  "settling through her fingers before she withdraws her hand. She speaks first, the words warm and held in "
  "(S1) \"<d>[Chinese] 回来啦。</d>\"; he lets out his breath and answers, low and steady, (S2) "
  "\"<d>[Chinese] 嗯，回来了。</d>\" - both of them loosening, the tension of the doorstep giving way.")),
 dict(t=9.4, body=(
  "a medium shot at the door as she turns toward the door panel and closes it, pushing the latch bolt twice "
  "before it aligns and clicks home; behind her Zhou Ye stands in the foyer, waiting without urging, his hands "
  "at rest. The shot ends on the door closing and her hand at the latch, then on him standing still in the warm "
  "light of the foyer."))],
sound=("The latch bolt clicking twice against the strike plate; his shoes set down softly; her voice warm and "
       "low; a brief quiet as the door closes.")),

# ============================ S04 ============================
dict(sid="S04", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S2", appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=HOME_DINING + " of the family home; the window with the potted plant is at one side of the table", appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night, the outdoor dark showing through the window."),
summary=("A video of the two of them at the dining table after he has come home: the mother sets a cup of warm "
         "water in front of Zhou Ye and sits down across from him, watching him while her thumbs turn over each "
         "other; he drinks a sip and sets the cup down, and they exchange a few quiet words about food while her "
         "gaze stays on him. Appearances follow <Picture 1> and <Picture 2>, the dining corner follows "
         "<Picture 3>, and the quiet two-shot follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium shot holds the dining table from one side, the light-blue tablecloth between them: the mother sets a "
 "cup of warm water down in front of Zhou Ye and sits on the chair across from him, facing him over the table; "
 "he sits facing her. She folds her hands on the table, her thumbs turning over each other as she watches him, "
 "her care held back; she says softly (S1) \"<d>[Chinese] 坐一会儿。饭还没好。</d>\"; he answers without "
 "looking up, (S2) \"<d>[Chinese] 我不饿。</d>\"; she watches him and says (S1) \"<d>[Chinese] 回来就得吃点。</d>\". "
 "He picks up the cup, drinks one sip, sets it down and lets out a long slow breath, then meets her eyes, and "
 "lets her keep looking at him. The camera stays locked in this single continuous shot; their two sides of the "
 "table stay constant, no cut."))],
sound=("The cup bottom meeting the table with a soft click; the dialogue in a low domestic quiet; small pauses "
       "between the lines.")),

# ============================ S05a1 ============================
dict(sid="S05a1", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=HOME_DINING, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night, the room quiet around the table."),
summary=("A video of the mother, seen from Zhou Ye's side of the dining table: she folds her hands on her knees, "
         "holds his face with her eyes for a beat, then asks her careful question - this time, is it settled - "
         "the words slow and soft, the question hanging in the air as her thumbs stop moving and she waits for "
         "his answer. Her appearance follows <Picture 1>'s subject line and <Picture 2>, the dining corner "
         "follows <Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot of the mother from Zhou Ye's side of the table, his side of the table barely entering the "
 "frame's near edge; she sits facing him across the light-blue tablecloth, her hands folded on her knees. She "
 "holds half a breath before speaking, her eyes first resting on his face for a beat without moving; then she "
 "speaks slowly, her gaze not leaving him, the words held back and careful (S1) \"<d>[Chinese] 这次……算是定下来"
 "了？</d>\" - the tail of the question soft and tucked in. The folded thumbs stop their small motion as the "
 "question lands, and she sits still, waiting for him to answer. The camera stays locked in this single "
 "continuous shot, no cut."))],
sound=("The dialogue leads; the room is low around it, a half-beat of quiet at the pause in her sentence.")),

# ============================ S05a2 ============================
dict(sid="S05a2", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=HOME_DINING, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night."),
summary=("A video of Zhou Ye, seen from the mother's side of the dining table: he pauses half a beat at her "
         "question, lifts his eyes from the rim of the cup to hers, and answers in a steady voice - it is settled, "
         "the paperwork is done, he will live here for now - then lets out a breath and holds her gaze, waiting "
         "for her next words. His appearance follows <Picture 1>, her presence follows <Picture 2>, the corner "
         "follows <Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot of Zhou Ye from the mother's side of the table; she sits across from him at the near edge "
 "of the frame. He pauses half a beat at her question, his gaze lifting from the rim of the cup on the "
 "light-blue tablecloth to meet hers, and answers with the words set down one by one, his voice steady (S1) "
 "\"<d>[Chinese] 定下来了。手续办完了，先回来住。</d>\" - at the words about living at home for now, the thumb "
 "against the cup wall relaxes and lies flat. When he finishes he lets out a light breath and does not look "
 "away, holding her gaze, waiting for her to speak next. The camera stays locked in this single continuous "
 "shot, no cut."))],
sound=("The dialogue leads; clear small pauses between his sentences; the room quiet around them.")),

# ============================ S05b1 ============================
dict(sid="S05b1", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=HOME_DINING, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night."),
summary=("A video of the mother leaning in across the table after his answer: her body comes forward, her folded "
         "hands slide to the table edge, and she presses on with her question - and what about afterwards - the "
         "words quicker, the tail rising, her eyes fixed on him without blinking, waiting for an answer that goes "
         "further down. Her appearance follows <Picture 2>, the corner follows <Picture 3>, and the framing "
         "follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot of the mother from Zhou Ye's side of the table. Hearing his answer, she leans slightly "
 "forward, her folded hands sliding from her knees onto the edge of the table and stopping there; her gaze "
 "locks onto his face, unblinking, as she asks, quicker than before and with the tail of the question rising "
 "(S1) \"<d>[Chinese] 先回来住。那以后呢？</d>\" - the short intake of her breath giving the words a faint "
 "urgency. She stays leaning forward, not drawing back, waiting for an answer that reaches further than "
 "settling down. The camera stays locked in this single continuous shot, no cut."))],
sound=("The dialogue leads; the tail of her question carries a faint hurry; a low domestic quiet beneath.")),

# ============================ S05b2 ============================
dict(sid="S05b2", subjects=[
 dict(role="zy", pic=1, indoor=True, sid="S1", appears=[1]),
 dict(role="mo", pic=2, apron=True, appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=("the living-room dining corner of the family home at night, the room lit warm while the night "
                 "outside is fully dark, the window glass at one side of the table reflecting the two of them"),
      appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night and the window glass reflects their two dim figures against the dark outside."),
summary=("A video of Zhou Ye answering the question of afterwards: instead of answering at once he looks toward "
         "the living-room window, where the night glass reflects the two of them, his mother's shoulder line "
         "thin and her clothes hanging loose; his gaze rests a moment on her reflection's shoulder, then returns "
         "to her face and he answers evenly - take the future slowly, find a suitable job or learn something - "
         "no grand promise, an honest plan, his eyes meeting hers. His appearance follows <Picture 1>, the corner "
         "and the window follow <Picture 3>, and the framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A close shot of Zhou Ye from the mother's side of the table. He does not answer at once: he turns his head "
 "toward the living-room window at one side of the table, no more than a quarter turn - outside the night is "
 "fully dark, and the glass throws back the reflections of the two of them, her shoulder line thin, her clothes "
 "hanging a little loose on her. His gaze stops on her reflection's shoulder for a moment, then comes back to "
 "her face, and he answers in an even tone, as if the words had long been thought out (S1) \"<d>[Chinese] 以后慢"
 "慢想。找个合适的工作，或者学点东西。</d>\" - as he says the words about learning something, a finger traces "
 "the rim of the cup and stops. He finishes with his eyes still on her, waiting for her to take it in. The "
 "camera stays locked in this single continuous shot; his turn toward the window stays within a quarter turn "
 "and returns, no flip."))],
sound=("The dialogue leads, with natural pauses between his sentences; the room quiet around the table.")),

# ============================ S05b3 ============================
dict(sid="S05b3", subjects=[
 dict(role="zy", pic=1, indoor=True, appears=[1]),
 dict(role="mo", pic=2, apron=True, sid="S1", appears=[1]),
 dict(role="space", pic=3, img=HOME, zone_label="living-room dining corner of the family home",
      zone_text=HOME_DINING, appears=[1]),
 dict(role="board", pic=4, appears=[1]),
],
style=("The target video uses a 3D animated film style with next-generation CG quality; the living room is lit "
       "warm at night."),
summary=("A video of the mother closing the subject: his answer does not fully settle her unease, so she lets her "
         "gaze fall, sits straight, draws a light breath, and when she lifts her eyes the topic has already "
         "turned - today we make dumplings - the words setting the evening's plan, her hands returning from the "
         "table edge to her lap. Her appearance follows <Picture 2>, the corner follows <Picture 3>, and the "
         "framing follows the storyboard reference <Picture 4>."),
shots=[dict(t=None, body=(
 "A medium-close shot of the mother from Zhou Ye's side of the table. She lets her gaze rest on his face for a "
 "moment after his answer, then lowers her eyes, sits straight, and draws a light breath before looking up "
 "again, the subject already turned; she says, settling it (S1) \"<d>[Chinese] 今天包饺子。</d>\" - the words "
 "landing softly, closing the topic here. As she sits straight her hands return from the table edge to her "
 "lap. The camera stays locked in this single continuous shot, no cut."))],
sound=("The dialogue leads; a half-beat pause before the subject turns; a low domestic quiet.")),
]
