# -*- coding: utf-8 -*-
"""Builder for h3_prompt_v9_grp3.json - compiles 9 H3 single-segment prompts (S11b2..S17).
Output schema mirrors prior rounds: {"group":"grp3","shots":[{"shot_id":...,"prompt":...}]}"""
import json, io, os

OUT = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\h3_prompt_v9_grp3.json"

CHAR_ZY = ("<Subject {n}> is Zhou Ye, the about-26-year-old Chinese man in <Picture {n}>, with a clear-cut "
           "slightly long face and a defined jaw, straight fairly thick eyebrows, calm restrained eyes, and neat "
           "short black hair; he wears a deep-navy simple zip jacket over a plain dark crew-neck top, dark trousers, "
           "and simple shoes. His appearance follows the sheet throughout.")
CHAR_MO = ("<Subject {n}> is Mother, the about-52-year-old Chinese woman in <Picture {n}>, slender and "
           "even-postured, her black hair with a few fine grey strands at the temples woven into a low bun at the "
           "back; she wears a plain dusty-purple knitted top, dark loose trousers, and a beige home apron. Her "
           "appearance follows the sheet throughout.")

STYLE = "The target video uses a 3D animated film style with warm home lighting at night."
NOCUT = "The camera stays locked in this single continuous shot throughout, no cuts."
BOARD = "<Picture {n}> is a storyboard reference for [Shot 1], defining its viewpoint, subject placement, and shot order."

def subject_defs_4(space):
    return "\n".join([CHAR_ZY.format(n=1), CHAR_MO.format(n=2), space.format(n=3), BOARD.format(n=4)])

def subject_defs_zy(space):   # mother back-only: only Zhou Ye tracked
    return "\n".join([CHAR_ZY.format(n=1), space.format(n=2), BOARD.format(n=3)])

def subject_defs_mo(space):   # mother subject only (Zhou Ye back to camera)
    return "\n".join([CHAR_MO.format(n=1), space.format(n=2), BOARD.format(n=3)])

def ret4():
    return "\n".join([
        "<Subject 1> (appears in [Shot 1]): fully_preserved - his clear-cut face, neat short black hair, deep-navy zip jacket, plain dark crew-neck top, dark trousers, and simple shoes are kept exactly as on the sheet.",
        "<Subject 2> (appears in [Shot 1]): fully_preserved - her low bun with fine grey strands at the temples, dusty-purple knitted top, dark loose trousers, and beige home apron are kept exactly as on the sheet.",
        "<Subject 3> (appears in [Shot 1]): fully_preserved - the single space described above is the only space in the shot.",
        "<Picture 4> (appears in [Shot 1]): partially_preserved - its viewpoint, subject placement, and shot order are realized in the single continuous shot."])

def ret_zy(space_short):
    return "\n".join([
        "<Subject 1> (appears in [Shot 1]): fully_preserved - his clear-cut face, neat short black hair, deep-navy zip jacket, plain dark crew-neck top, dark trousers, and simple shoes are kept exactly as on the sheet.",
        "<Subject 2> (appears in [Shot 1]): fully_preserved - " + space_short + " is the only space in the shot.",
        "<Picture 3> (appears in [Shot 1]): partially_preserved - its viewpoint, subject placement, and shot order are realized in the single continuous shot."])

def ret_mo(space_short):
    return "\n".join([
        "<Subject 1> (appears in [Shot 1]): fully_preserved - her low bun with fine grey strands at the temples, dusty-purple knitted top, dark loose trousers, and beige home apron are kept exactly as on the sheet.",
        "<Subject 2> (appears in [Shot 1]): fully_preserved - " + space_short + " is the only space in the shot.",
        "<Picture 3> (appears in [Shot 1]): partially_preserved - its viewpoint, subject placement, and shot order are realized in the single continuous shot."])

def refs4():
    return ("Zhou Ye's appearance follows <Picture 1>, Mother's appearance follows <Picture 2>, the space follows "
            "<Picture 3>, and the viewpoint, subject placement, and shot order follow the storyboard reference <Picture 4>.")

def refs_zy():
    return ("Zhou Ye's appearance follows <Picture 1>, the space follows <Picture 2>, and the viewpoint, subject "
            "placement, and shot order follow the storyboard reference <Picture 3>.")

def refs_mo():
    return ("Mother's appearance follows <Picture 1>, the space follows <Picture 2>, and the viewpoint, subject "
            "placement, and shot order follow the storyboard reference <Picture 3>.")

# ---------------- per-shot prompts ----------------
S = {}

S["S11b2"] = f"""subject_definitions:
{subject_defs_zy("<Subject {n}> is the single space of this shot: the kitchen of the continuous home in <Picture {n}>, with its wooden countertop, sink, stove, and the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Zhou Ye speaks the rest of his confession toward Mother's turned back at the kitchen counter; his breath catches on the words about missing her, and the final phrase trails low and stops, the quiet settling between them. {refs_zy()} Mother keeps her back turned through the whole take, her grey-streaked low bun, dusty-purple top, and beige home apron visible on her turned figure.

retention_analysis:
{ret_zy("the kitchen with its wooden countertop")}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium-close frame at eye level holds Zhou Ye as its subject: he stands at the sink side of the wooden counter with his face toward Mother, and Mother stands at the stove side of the counter with her back fully turned toward him, her head lowered over the cutting board before her, the crumpled tissue still held in the hand at her side, her shoulders still. At 00:00.300 he begins, his voice low and even, his gaze resting on the line of her turned shoulders, <Subject 1> (S1): <d>[Chinese] 我也想你。</d> At 00:01.100 the words about missing her break his breath for a beat; he pauses with his mouth half open, swallows, and steadies himself, his eyes staying on her back. At 00:01.900 he goes on in a lower, quicker stream, the words crowding out of him, his gaze dropping to the counter between them and rising again to her shoulders, his hands hanging loose at his sides, <Subject 1> (S1): <d>[Chinese] 在外面看见别人打电话回家，我会想起你。想打的时候，又不知道该从哪句开始。</d> At 00:05.400 his pace slows and his voice thins low, the words sinking, <Subject 1> (S1): <d>[Chinese] 后来拖着拖着，就更不知道了。</d> As the last word falls, the fingers of the hand at his side curl once and ease open again, and he closes his mouth and stands still, letting the quiet settle around them. Mother keeps her back turned, her shoulders unmoving, the crumpled tissue held steady in her hand, and the take holds on the two of them in the warm kitchen light through the final frames.

overall_soundscape:
Dialogue carries the segment; the ambient sound stays very low through the kitchen at night, with one audible intake of breath just before the words about missing her, and the quiet rustle of the tissue as her hand shifts once.

non_diegetic_music:
N/A"""

S["S11c1"] = f"""subject_definitions:
{subject_defs_mo("<Subject {n}> is the single space of this shot: the kitchen of the continuous home in <Picture {n}>, with its wooden countertop, sink, stove, and the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Mother, her eyes still red-rimmed, asks Zhou Ye to make the future concrete across the kitchen counter: she asks what he will do from now on, hears his answer, and presses once more, softly, for every day. {refs_mo()} Zhou Ye stands at the sink side of the counter with his back toward the camera, his answers reaching her from where he stands.

retention_analysis:
{ret_mo("the kitchen with its wooden countertop")}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium-close frame at eye level holds Mother as its subject across the wooden counter of the kitchen: her eyes are still red-rimmed, her face soft and open, and her hands rest at the edge of the counter before her; Zhou Ye stands at the sink side of the counter facing her, his back toward the camera. At 00:00.300 she asks, her voice tight and low, her gaze holding his eyes, Mother (S2): <d>[Chinese] 那你以后呢？</d> She waits through a half beat of quiet, her hands still on the counter edge, her gaze steady on him. At 00:02.300 Zhou Ye's answer reaches her from the sink side of the counter, even and sure, Zhou Ye (S1): <d>[Chinese] 以后我说。</d> The words stop her for a beat: she goes still, her chin lifting a fraction, her breath gathering and held. At 00:03.000 she asks again, the two words soft and precise, her eyes fixed on his, unblinking, the hand at her front gripping the hem of her apron once, Mother (S2): <d>[Chinese] 每天？</d> The last syllable hangs in the air between them, and after it she lets her held breath out in one quiet release, her gaze still on his face, and the take holds there through the final frames.

overall_soundscape:
The three spoken lines each keep half a beat of quiet around them; the final question trails off softly, with only the low room tone of the kitchen underneath.

non_diegetic_music:
N/A"""

S["S11c2"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the kitchen of the continuous home in <Picture {n}>, with its wooden countertop, sink, stove, and the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Zhou Ye gives Mother his promise across the kitchen while she rounds the wooden counter and comes to stand close before him; her hand rises, and her fingertips meet the side of his face as the take ends. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium-close frame at eye level holds Zhou Ye as its subject: he stands at the sink side of the wooden counter with his face toward the stove side, and Mother stands across the kitchen near the stove, her face toward him, her eyes still red-rimmed, her hands at her sides. At 00:00.400 he meets her gaze and speaks the promise whole, his voice low and steady, his hands loose at his sides, <Subject 1> (S1): <d>[Chinese] 不一定每天都能说，但我不再让你猜。</d> At 00:02.900, as the last words settle, he lets out one long breath, his shoulders easing, his gaze following her the whole way. Mother leaves her place near the stove, rounds the end of the wooden counter, and walks to stand close before him, her steps light and unhurried; as she arrives at 00:05.200, she lifts her eyes to his face, and a half beat of stillness holds between them, their breathing the only motion. At 00:06.000 her hand rises, slow and light; at 00:06.600 her fingertips meet the side of his face, the touch barely resting there, his face quiet and soft above her hand, and the take holds on the contact through the final frames of the segment.

overall_soundscape:
A beat of quiet holds after his words, then the sound of the two breathing; her light steps cross the kitchen floor as she comes around the counter.

non_diegetic_music:
N/A"""

S["S12"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the kitchen counter of the continuous home in <Picture {n}>, the dough basin standing on the wooden countertop under the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Mother draws her hand back from Zhou Ye's face and pulls the evening back to the dough, saying it still needs kneading; Zhou Ye steps up and takes over the kneading, and the two settle into the work together. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed near frame at eye level keeps Mother as its subject at the counter: Zhou Ye stands close at her side, his face toward hers, and her fingertips still rest at the side of his face, the dough basin standing on the wooden countertop before them. At 00:00.600 she holds the touch through half a beat more, her eyes warm on his; at 00:01.400 she slips her hand back from his cheek, her fingers coming down to the rim of the dough basin. Her gaze drops to the dough in the basin, her face settling back into the evening's work, and she speaks, plain and even, <Subject 2> (S2): <d>[Chinese] 面还没和好。</d> At 00:03.800 Zhou Ye steps up to the counter's main position, his hands reaching toward the dough, and answers, low and warm, <Subject 1> (S1): <d>[Chinese] 我来。</d> At 00:04.600 his hands close on the dough in the basin and begin to knead, folding and pressing, the basin ringing softly against the wood with each press, his eyes lowered on the dough. Mother lifts her hands off the rim and lets them rest at her sides, empty, watching the dough move under his hands, her face easing. At 00:06.500 she lets out the long held breath, her shoulders dropping; at 00:07.200 he exhales once in return, his kneading settling into a steady rhythm, her gaze soft on the dough, and the take holds in the warm kitchen light through the final frames.

overall_soundscape:
The soft ring of the dough basin against the counter with each press of kneading, the low sounds of the dough under his hands, and the slow release of two long breaths sound through the quiet kitchen.

non_diegetic_music:
N/A"""

S["S13"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the cutting-board workspace of the kitchen of the continuous home in <Picture {n}>, a flour-dusted wooden board holding small dough pieces, a glass bowl of filling, a neat stack of rolled skins, and a rolling pin resting on the flour, under the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Mother demonstrates wrapping a dumpling across the cutting board while Zhou Ye watches her hands and then makes three dumplings of his own, each steadier than the last, trading short lines with her until she tells him this one will do and he asks her to teach him. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium-close frame looks down over the flour-dusted cutting board at an angle of about thirty degrees, the four hands of Mother and Zhou Ye the subject of the take: Mother works at the stove side of the board and Zhou Ye at the sink side, facing each other across it, both leaning in over the work, small dough pieces lying in a row on the flour with the glass bowl of filling and the rolling pin at hand. At 00:00.500 Mother's hands take up a rolled skin, lay a spoon of filling in its center, and fold it over, her voice low and easy as she begins the lesson, <Subject 2> (S2): <d>[Chinese] 你擀皮，我包。</d> At 00:01.900 Zhou Ye answers, his eyes still on her hands, <Subject 1> (S1): <d>[Chinese] 好。</d> Her fingers press the seam closed in even pleats, her wrist steady, one clean dumpling set down on the flour; Zhou Ye watches her hands, then looks down at his own. At 00:04.600 his first attempt comes together lopsided, its belly uneven and its seam crooked; he turns it in his palm and sets it aside, his brows drawing together. At 00:06.800 his second attempt seals too tightly, the pleats squeezed until the dumpling sits pinched and small. At 00:09.000 his hands slow on the third piece, working with care, his breath held as the pleats close evenly and the seam eases shut; at 00:10.300 he sets the dumpling down and it stands steady on its base, and he lets the held breath out. At 00:11.000 Mother's eyes rest on the standing dumpling and her voice warms, <Subject 2> (S2): <d>[Chinese] 这个可以。</d> At 00:12.100 Zhou Ye's eyes lift to her face, a small hope in them, <Subject 1> (S1): <d>[Chinese] 及格了？</d> At 00:13.000 she answers, her eyes crinkling, <Subject 2> (S2): <d>[Chinese] 还早。</d> At 00:13.600 he leans in, his voice eager and low, <Subject 1> (S1): <d>[Chinese] 那你教我。</d> and the take holds on the two of them over the board through the final frames.

overall_soundscape:
The small, close sounds of the dough and the filling: skins pressed thin by the rolling pin, filling spooned from the glass bowl, pleats pinched shut, with the two voices trading short lines over the board.

non_diegetic_music:
N/A"""

S["S14"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the kitchen counter of the continuous home in <Picture {n}> at its cutting-board corner, with the wooden tray lined with neat rows of wrapped dumplings, the flour-dusted cutting board, and the glass bowl holding the last of the filling, under the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Zhou Ye sets his clumsiest dumpling in front of Mother and claims it for himself, Mother smooths its pleats back into place, and the two trade easy lines about tomorrow and the day after while the last of the filling is scraped clean. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium frame at eye level holds the two across the cutting-board counter: Mother works at the stove side of the board and Zhou Ye at the sink side, facing each other over the flour-dusted surface, wrapped dumplings standing in rows on the wooden tray, the glass bowl holding the last of the filling. At 00:00.700 Zhou Ye sets a clumsy dumpling down before Mother, its seam crooked, and says it with a small grin, his eyes flicking up to her face, <Subject 1> (S1): <d>[Chinese] 这个归我自己吃。</d> At 00:03.000 Mother's hands take the dumpling up, press the pleats back into place one by one, unhurried, and set it in line with the others, her voice warm as she answers, <Subject 2> (S2): <d>[Chinese] 够两个人吃了。</d> His hands go on shaping another skin between his fingers, the rolling pin rocking over the flour as he works. At 00:05.800 he asks in a light, easy tone, stealing a glance at her face, <Subject 1> (S1): <d>[Chinese] 妈，明天还包吗？</d> At 00:07.800 she answers with her eyes on her work, <Subject 2> (S2): <d>[Chinese] 明天吃面。</d> At 00:09.600 he presses, his brows lifting, <Subject 1> (S1): <d>[Chinese] 后天呢？</d> At 00:10.800 she answers, and her hand reaches for the spatula beside the glass bowl, <Subject 2> (S2): <d>[Chinese] 后天再说。</d> At 00:11.800 she scrapes the bowl clean, the spatula sweeping the last smear of filling into the final skin, and folds it shut; the emptied bowl is set aside, and the take holds on the two of them across the board in the warm kitchen light through the final frames.

overall_soundscape:
The dull thud of the rolling pin on the board and the soft stirring of the meat filling between the lines, with the light scrape of the spatula clearing the last of the filling at the close.

non_diegetic_music:
N/A"""

S["S15"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the stove corner of the kitchen of the continuous home in <Picture {n}>, with the large pot on the lit burner and the wooden counter beside the stove, under the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Zhou Ye brings the tray of wrapped dumplings to the stove, slides them into the boiling water, watches them float up, and lifts one out, blows it cool, and lowers it into the small bowl held in Mother's hands; Mother receives it with steady hands and warm eyes. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium frame at eye level holds the stove corner of the kitchen: Mother stands before the stove beside the large pot on the lit burner, her small bowl held in both hands before her chest, her face turned toward the rolling water as steam rises from it. At 00:00.400 Zhou Ye comes to the stove carrying the wooden tray of wrapped dumplings in both hands, his eyes on the tray; at 00:02.500 he sets the tray down on the counter beside the stove, takes up the dumplings one after another, and slides them into the boiling water. The water swallows them and rolls again; the two watch the surface, their gazes on the pot, her bowl still held before her chest. At 00:05.800 the dumplings bob up one by one and float, their skins turning slightly translucent in the rolling water. At 00:08.800 he takes up the slotted spoon resting against the pot's rim, dips it in, and lifts out one dumpling; at 00:09.600 he raises it before his lips and blows across it in short careful breaths, one hand steady on the spoon and the other cupped loosely beneath, his eyes soft and intent on the dumpling. Mother watches him, her lips parting as if she would say she can take it herself, then curving into a quiet smile, and she stays silent, holding her bowl beneath the spoon, her eyes warm. At 00:11.000 he lowers the cooled dumpling into the bowl in her hands; she holds the bowl steady to receive it, her gaze dropping to the dumpling and then lifting to his face, her eyes glistening. At 00:11.700 he sets the spoon against the pot's rim with a light clink, his face easing into quiet warmth as he looks back at her, his hand coming to rest on the counter beside the tray; steam drifts between them above the low roll of the water, and the take holds there in the warm kitchen light.

overall_soundscape:
The low boil of the water in the large pot, the soft splash of the dumplings going in, the light clink of the slotted spoon against the pot's rim, and the quiet room tone of the kitchen at night.

non_diegetic_music:
N/A"""

S["S16"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the dining corner of the continuous home in <Picture {n}>, with its wooden table draped in a blue cloth and its wooden chairs, under the warm lamplight of the night.")}

summary:
[reference generation] In one continuous shot, Mother starts the meal with her chopsticks and then pushes the key across the tabletop toward Zhou Ye, telling him to remember it this time; he takes it into his open palm, closes his fingers around it with one light squeeze, and answers that he will carry it. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A fixed medium-close frame at eye level holds the two across the blue-clothed dining table: Mother sits at one side and Zhou Ye at the other, facing each other, bowls of dumplings before each of them, and a small key lying on the cloth beside Mother's bowl. At 00:00.400 Mother takes up her chopsticks, and her voice comes easy and firm as the meal begins, <Subject 2> (S2): <d>[Chinese] 先吃饭。</d> At 00:01.800 Zhou Ye answers, low and agreeable, <Subject 1> (S1): <d>[Chinese] 好。</d> He lifts a dumpling from his bowl and eats quietly, his eyes warm on her. At 00:03.000 Mother sets her chopsticks down, her hand moving to the key beside her bowl; at 00:03.400 she pushes it across the tabletop toward him, the key scraping softly over the blue cloth, her eyes following it, and then lifting to his face. At 00:05.200 she reminds him, her voice quiet and steady, <Subject 2> (S2): <d>[Chinese] 别又忘了带。</d> At 00:07.200 Zhou Ye sets down his chopsticks and watches the key glide to a stop before his hand; at 00:07.600 he reaches out, palm up, his eyes on the key, <Subject 1> (S1): <d>[Chinese] 不会。</d> At 00:09.000 the key comes to rest in his open palm; at 00:09.800 his fingers close around it, giving one light squeeze, his gaze on the key in his hand. At 00:10.800 he lifts his eyes to her face, and she watches him with her face eased, and the take holds on the two of them across the table through the final frames.

overall_soundscape:
The light scrape of the key pushed across the wooden tabletop, the small sounds of the meal between the lines, and the quiet room tone of the dining corner at night.

non_diegetic_music:
N/A"""

S["S17"] = f"""subject_definitions:
{subject_defs_4("<Subject {n}> is the single space of this shot: the open kitchen-and-dining space of the continuous home in <Picture {n}>, with its blue-clothed wooden dining table and the stove with the large pot on the counter, under the warm overhead light of the night.")}

summary:
[reference generation] In one continuous shot, Zhou Ye takes up his empty bowl and follows Mother across the open kitchen toward the stove; she slows her steps to let him draw near, and the two stop before the pot, where two dumplings drift in the gently swaying water, and the film settles into its close. {refs4()}

retention_analysis:
{ret4()}

detailed_description:
{STYLE}
{NOCUT}
[Shot 1] A medium frame at eye level follows the two across the open kitchen-and-dining space in the warm night light: at the blue-clothed dining table, Zhou Ye takes up his empty white bowl from the tabletop and rises to his feet, his face quiet and easy; Mother is already on her feet ahead of him, walking toward the stove at the far counter, her hands empty at her sides. At 00:01.200 Zhou Ye falls in behind her, half a step back, the bowl held before him in both hands, his steps even and unhurried, his gaze resting on her back as he follows. At 00:03.500 Mother slows her steps to wait for him, her pace easing as he draws up beside her. At 00:05.000 the two reach the stove together and stop before it, Mother at the pot's side; at 00:05.600 Zhou Ye sets his bowl down on the counter beside the pot, his hands coming to rest on the countertop, and looks into the water. Two dumplings drift in the pot, turning gently in the swaying surface of the soup, steam rising slow between them. His gaze rests on the water, his face settling into quiet ease; Mother stands beside him, her gaze soft on the pot, and the take holds on the two of them there as the evening closes around the kitchen.

overall_soundscape:
The slow, even footsteps of the two across the floor, the soft thud of the bowl set down on the counter, and the low gentle sway of the water in the pot, with the two dumplings shifting softly inside it, sound through the quiet kitchen at night.

non_diegetic_music:
N/A"""

shots = [{"shot_id": sid, "prompt": S[sid].strip() + "\n"} for sid in ["S11b2", "S11c1", "S11c2", "S12", "S13", "S14", "S15", "S16", "S17"]]
data = {"group": "grp3", "shots": shots}
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
print("written", OUT, os.path.getsize(OUT), "bytes; shots:", len(shots))
for s in shots:
    print(s["shot_id"], len(s["prompt"]))
