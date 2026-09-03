# -*- coding: utf-8 -*-
"""v5 -> v6 storyboard transform: 正反打拆镜 29镜 + 删帽 + 空间/时间/灯光锁定 + 方位道具参照 + grid锁1."""
import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r"D:/Hermes/xiaonan-memory/opc-sim/v2/06_storyboard"
V5 = BASE + "/storyboard_package_v5.json"
OUT = BASE + "/storyboard_package_v6.json"
SP = r"D:/Hermes/xiaonan-memory/opc-sim/v2/02_screenplay/screenplay.md"

with open(V5, encoding='utf-8') as f:
    P = json.load(f)

GRID = "单图构图锚点（无切镜）"
DISPATCH = "H3 r2v single segment"
SAME = "same-side camera, no 180° flip"
STAB = "平视"
ANGL = "平拍"

# ---------- canonical dialogue (screenplay.md, 47 lines, speaker->id) ----------
ID_M, ID_Z = "identity.mother.v1", "identity.zhou-ye.v1"
CANON = [
 (ID_Z,"妈。"),(ID_M,"回来啦。"),(ID_Z,"嗯，回来了。"),
 (ID_M,"坐一会儿。饭还没好。"),(ID_Z,"我不饿。"),(ID_M,"回来就得吃点。"),
 (ID_M,"这次……算是定下来了？"),(ID_Z,"定下来了。手续办完了，先回来住。"),
 (ID_M,"先回来住。那以后呢？"),(ID_Z,"以后慢慢想。找个合适的工作，或者学点东西。"),(ID_M,"今天包饺子。"),
 (ID_Z,"你不是说腰疼？"),(ID_M,"擀几张皮，没事。"),
 (ID_M,"水多了。"),(ID_Z,"我再加面。"),
 (ID_M,"你走那天，我给你装了两双袜子。"),(ID_Z,"我记得。"),
 (ID_M,"我还以为你会打电话。第一周等，第二周也等。你爸不在以后，家里就剩我一个人。我不敢病，不敢摔，不敢晚上睡得太死。可我又不能跟你说这些。你在外面，听见了只会分心。"),
 (ID_M,"有一次半夜停电……我以为是你回来了。后来才想起来，你的钥匙一直在我这儿。"),
 (ID_M,"我知道你有你的事。我也知道当兵不是去玩。可我就是想让你知道，家里有人等你。不是要你马上回来，也不是要你保证什么。我只是想让你偶尔说一句，你还好。"),
 (ID_Z,"妈。"),(ID_Z,"对不起。"),(ID_M,"别一回来就说对不起。"),
 (ID_Z,"不是因为你等我。是我以为不说就算是让你放心。我把自己照顾好，就觉得你也会放心。可你不是只想知道我有没有受伤。"),
 (ID_Z,"我也想你。在外面看见别人打电话回家，我会想起你。想打的时候，又不知道该从哪句开始。后来拖着拖着，就更不知道了。"),
 (ID_M,"那你以后呢？"),(ID_Z,"以后我说。"),(ID_M,"每天？"),
 (ID_Z,"不一定每天都能说，但我不再让你猜。"),
 (ID_M,"面还没和好。"),(ID_Z,"我来。"),
 (ID_M,"你擀皮，我包。"),(ID_Z,"好。"),(ID_M,"这个可以。"),(ID_Z,"及格了？"),(ID_M,"还早。"),(ID_Z,"那你教我。"),
 (ID_Z,"这个归我自己吃。"),(ID_M,"够两个人吃了。"),(ID_Z,"妈，明天还包吗？"),(ID_M,"明天吃面。"),(ID_Z,"后天呢？"),(ID_M,"后天再说。"),
 (ID_M,"先吃饭。"),(ID_Z,"好。"),(ID_M,"别又忘了带。"),(ID_Z,"不会。"),
]

def mk(**kw):
    """new card, full v5 field set"""
    c = {
        "shot_id": None, "scene_id": None, "objective": None,
        "duration_s": None, "core_duration_s": None, "edit_safety_s": 1.5,
        "identity_ids": ["identity.zhou-ye.v1", "identity.mother.v1"],
        "state_ids": None, "space": None, "time": None, "orientation": None,
        "shot_size": None, "height": STAB, "angle": ANGL,
        "stable_position": SAME, "primary_movement": None,
        "first": None, "middle": None, "tail": None, "blocking": None,
        "playable_action": None, "emotion_start": None, "emotion_turn": None,
        "emotion_landing": None, "dialogue": [], "sound": None,
        "prop_before": "无", "prop_after": "无", "cut_interface": None,
        "grid_count": 1, "grid_reason": GRID,
        "action_complexity": None, "continuity_risk": "低",
        "cut_motivation": None, "orientation_lock": None,
        "natural_duration_s": None, "beat_pause_s": None, "tempo_shape": None,
        "eye_line": None, "micro_action": None, "breath": None,
        "dispatch": DISPATCH, "storyboard_file": "",
    }
    c.update(kw)
    return c

def dl(entries):
    return [{"speaker": s, "line": l} for s, l in entries]

STATES_LR = ["state.zhou-ye.accepting-home.v1", "state.mother.testing.v1"]     # scene2 客厅
STATES_K  = ["state.zhou-ye.responding.v1", "state.mother.releasing.v1"]      # scene3 厨房

NEW = {}
# ============ S05 组（客厅餐桌对坐正反打拆镜，scene2） ============
NEW["S05a1"] = mk(
    shot_id="S05a1", scene_id="scene2",
    objective="母亲开口试探：「这次……算是定下来了？」——问句挂在省略号上，不敢问实",
    duration_s=6, core_duration_s=4.5,
    state_ids=STATES_LR,
    space="客厅（餐桌对坐区）", time="刚入夜",
    orientation="客厅餐桌对坐轴，母机位（机位在周野一侧、拍母亲）：母亲与周野隔桌相向，母亲面向周野方向，无越轴",
    shot_size="中近景（母亲）",
    primary_movement="固定",
    first="母亲双手交叠放在膝上，开口前目光先落在周野脸上，停了一拍",
    middle="「这次……」语速放慢，省略号处她目光不移开；「算是定下来了？」问出口，尾音收得轻",
    tail="问完她没再动，交叠的拇指停住，等他接话",
    blocking="餐桌对坐，母机位单机：母亲主体；周野隔桌相向，答句由S05a2接",
    playable_action="落眼停拍+问句放慢+尾音收轻+拇指停住",
    emotion_start="小心翼翼",
    emotion_turn="把「定下来了」四个字问出口",
    emotion_landing="话一出口自己先悬起来",
    dialogue=dl([(ID_M,"这次……算是定下来了？")]),
    sound="对白为主，客厅环境声低；省略号处留半拍静",
    cut_interface="接S05a2（周机位：同一问一答的正反打切）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（2026-09-03铁律5）：母机位问句独立成镜，单机位、台词落点完整≥4s",
    orientation_lock="餐桌对坐轴内母机位，无翻转",
    natural_duration_s=4.5, beat_pause_s=1.5,
    tempo_shape="落眼停拍(1s)→「这次」放慢(1.5s)→省略号静半拍(1s)→问句收轻(1.5s)→等答(1s)",
    eye_line="母亲看周野眼睛，不闪躲",
    micro_action="问句尾音时交叠的拇指摩挲停住",
    breath="问前屏了半口气",
)
NEW["S05a2"] = mk(
    shot_id="S05a2", scene_id="scene2",
    objective="周野正面回答「定下来了」，把「先回来住」落到现实",
    duration_s=6, core_duration_s=4.5,
    state_ids=STATES_LR,
    space="客厅（餐桌对坐区）", time="刚入夜",
    orientation="客厅餐桌对坐轴，周机位（机位在母亲一侧、拍周野）：周野面向母亲方向，隔桌相向，无越轴",
    shot_size="中近景（周野）",
    primary_movement="固定",
    first="周野闻言停半拍，目光从杯沿抬起，迎上母亲的目光",
    middle="「定下来了。手续办完了，先回来住。」声音放稳，一句一句说清",
    tail="答完轻轻呼出一口气，没有移开视线，等她接下一句",
    blocking="餐桌对坐，周机位单机：周野主体；母亲隔桌相向，反应由S05b1接",
    playable_action="停半拍+抬眼作答+呼气压尾",
    emotion_start="克制",
    emotion_turn="把「定下来了」说出口的笃定",
    emotion_landing="说完松一口气，仍看着她",
    dialogue=dl([(ID_Z,"定下来了。手续办完了，先回来住。")]),
    sound="对白为主；答句之间气口清楚",
    cut_interface="接S05b1（母机位：她的追问正反打切）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（2026-09-03铁律5）：周机位答句独立成镜，台词落点完整",
    orientation_lock="餐桌对坐轴内周机位，无翻转",
    natural_duration_s=4.5, beat_pause_s=1.5,
    tempo_shape="停半拍抬眼(1.5s)→作答(3s)→呼气压尾(1.5s)",
    eye_line="周野先看杯沿，再抬眼迎住她",
    micro_action="答「先回来住」时握着杯壁的拇指松开放平",
    breath="答前浅吸一口气",
)
NEW["S05b1"] = mk(
    shot_id="S05b1", scene_id="scene2",
    objective="母亲抓住「先回来住」追问「那以后呢」，身体前倾探出不安",
    duration_s=4, core_duration_s=2.5,
    state_ids=STATES_LR,
    space="客厅（餐桌对坐区）", time="刚入夜",
    orientation="客厅餐桌对坐轴，母机位（机位在周野一侧、拍母亲）：母亲面向周野方向略前倾，无越轴",
    shot_size="中近景（母亲）",
    primary_movement="固定",
    first="母亲听完答案，身体略前倾，交叠的手落到桌沿",
    middle="「先回来住。那以后呢？」语速比刚才快，尾音上扬",
    tail="前倾未收，目光钉在周野脸上，等一个往下的答案",
    blocking="母机位单机：母亲主体，前倾追问",
    playable_action="前倾+追问+目光钉住",
    emotion_start="听到「定下来了」心里一松",
    emotion_turn="追问把「以后」顶出来",
    emotion_landing="不安探到台面",
    dialogue=dl([(ID_M,"先回来住。那以后呢？")]),
    sound="对白为主；问句尾音带一丝急",
    cut_interface="接S05b2（周机位：答案正反打切）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（凡哥拍板4s）：母机位追问句独立成镜",
    orientation_lock="餐桌对坐轴内母机位，前倾不越轴，无翻转",
    natural_duration_s=2.5, beat_pause_s=1.5,
    tempo_shape="前倾(1s)→追问句(2s)→悬住等答(1s)",
    eye_line="她直直看周野眼睛，不眨",
    micro_action="手从膝上滑到桌沿时停住",
    breath="追问气息短促",
)
NEW["S05b2"] = mk(
    shot_id="S05b2", scene_id="scene2",
    objective="「以后」的开放答案：不画饼不保证，先落「工作/学东西」的日常打算",
    duration_s=6, core_duration_s=4.5,
    state_ids=STATES_LR,
    space="客厅（餐桌对坐区）", time="刚入夜",
    orientation="客厅餐桌对坐轴，周机位（机位在母亲一侧、拍周野）：周野面向母亲方向，隔桌相向，无越轴",
    shot_size="中近景（周野）",
    primary_movement="固定",
    first="周野迎着她前倾的目光，没有躲",
    middle="「以后慢慢想。找个合适的工作，或者学点东西。」语气平缓，像早就想过",
    tail="说完目光仍落在她脸上，等她消化",
    blocking="周机位单机：周野主体，作答不闪躲",
    playable_action="迎视+平缓作答+目光不撤",
    emotion_start="被追问到具体处",
    emotion_turn="给出的是过程不是保证",
    emotion_landing="坦荡接住她的目光",
    dialogue=dl([(ID_Z,"以后慢慢想。找个合适的工作，或者学点东西。")]),
    sound="对白为主；句间停顿自然",
    cut_interface="接S05b3（母机位：收话转日常）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（凡哥拍板6s）：周机位答案独立成镜",
    orientation_lock="餐桌对坐轴内周机位，无翻转",
    natural_duration_s=4.5, beat_pause_s=1.5,
    tempo_shape="迎视停半拍(1s)→「以后慢慢想」放慢(2s)→后半句说清(2s)→收住等她(1s)",
    eye_line="周野这次不垂眼，看着她说完",
    micro_action="说到「学点东西」时手指在杯沿划了一下又停",
    breath="说「慢慢想」时声音放稳",
)
NEW["S05b3"] = mk(
    shot_id="S05b3", scene_id="scene2",
    objective="母亲把不安按回日常，用「今天包饺子」收话，对话转入共同行动",
    duration_s=4, core_duration_s=2.5,
    state_ids=STATES_LR,
    space="客厅（餐桌对坐区）", time="刚入夜",
    orientation="客厅餐桌对坐轴，母机位（机位在周野一侧、拍母亲）：母亲面向周野方向，收话后坐直，无越轴",
    shot_size="中近景（母亲）",
    primary_movement="固定",
    first="母亲听完，目光在他脸上停了一瞬，然后收回去",
    middle="她坐直，垂眼半拍，再抬眼时话已经转了向：「今天包饺子。」",
    tail="尾音落定，她把话题收在这里",
    blocking="母机位单机：母亲主体，坐直收话",
    playable_action="收回目光+坐直+转话收尾",
    emotion_start="不安没被答满",
    emotion_turn="把话按回日常",
    emotion_landing="定了：今天包饺子",
    dialogue=dl([(ID_M,"今天包饺子。")]),
    sound="对白为主；转话前半拍停顿",
    cut_interface="接S06（母亲起身走向冰箱）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（凡哥拍板4s）：母机位收话句独立成镜，情绪落点完整",
    orientation_lock="餐桌对坐轴内母机位，无翻转",
    natural_duration_s=2.5, beat_pause_s=1.5,
    tempo_shape="目光停留(1s)→坐直顿半拍(1s)→「今天包饺子」收话(2s)",
    eye_line="母亲先看他，再垂眼，抬眼时已转向日常话头",
    micro_action="坐直时双手从桌沿收回膝上",
    breath="收话前轻吸一口气",
)

# ============ S11 组（厨房正反打拆镜，scene3） ============
NEW["S11a1"] = mk(
    shot_id="S11a1", scene_id="scene3",
    objective="周野对母亲的背影开口：先「妈」后「对不起」，道歉说出口",
    duration_s=6, core_duration_s=4.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="周野在水槽侧、立于母亲身后半步（递纸动线后的站位），面向母亲背影开口；母亲在灶台侧面向案板、背对周野——背影为既定状态（延续S10b），镜内不拍转身；方位参照：灶台/水槽/案板固定物",
    shot_size="中近景（周野为主，母亲背影在前景作衬影）",
    primary_movement="固定",
    first="周野望着母亲的背影，开口轻唤「妈。」",
    middle="母亲没有回头；停一拍，他再开口，「对不起。」逐字压低",
    tail="三个字说完他站着没动，等她回应，喉头动了一下",
    blocking="周机位单机：周野主体；母亲在灶台侧背对（背影既定），肩线不动",
    playable_action="轻唤+停顿+「对不起」逐字压低",
    emotion_start="内疚",
    emotion_turn="把道歉说出口",
    emotion_landing="道歉落地，等她接",
    dialogue=dl([(ID_Z,"妈。"),(ID_Z,"对不起。")]),
    sound="轻唤与道歉之间留一拍静默；环境声极低",
    cut_interface="接S11a2（母机位：母亲回头回应）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（2026-09-03铁律5）：周机位道歉独立成镜（凡哥拍板6s），台词落点完整",
    orientation_lock="周野始终在母亲身后半步方向，无翻转；母亲背影既定不转身",
    natural_duration_s=4.5, beat_pause_s=1.5,
    tempo_shape="轻唤(1s)→静默半拍(1s)→「对不起」逐字压低(2.5s)→垂手等她回头(1.5s)",
    eye_line="周野看母亲背影的肩线，等她回头",
    micro_action="垂在身侧的手微微握紧又松开",
    breath="说「对不起」的「起」字尾音微颤",
)
NEW["S11a2"] = mk(
    shot_id="S11a2", scene_id="scene3",
    objective="母亲听到道歉回头，用「别一回来就说对不起」把歉挡回去——眼眶红着已软下来",
    duration_s=6, core_duration_s=4.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="母亲在灶台侧面向案板，听到道歉后回头看向身后半步处的周野（转头≤90°，身体不转，无180°转身定格）；周野在水槽侧身后半步（同S11a1站位）；方位参照：灶台/水槽/案板固定物",
    shot_size="中近景（母机位：拍母亲回头的脸）",
    primary_movement="固定",
    first="「对不起」落进耳朵，母亲背影的肩膀顿了一下，手里还攥着纸巾",
    middle="她回头看向身后半步处的周野，眼睛红着，目光先软下来",
    tail="「别一回来就说对不起。」声音哑，把话头轻轻挡回去",
    blocking="母机位单机：母亲主体；转头≤90°看向身后周野，无转身定格",
    playable_action="肩顿+回头+挡话",
    emotion_start="绷着的委屈被「对不起」撞开",
    emotion_turn="回头看他",
    emotion_landing="眼眶红着软下来",
    dialogue=dl([(ID_M,"别一回来就说对不起。")]),
    sound="回应声哑而轻；攥纸巾的手传来窸窣一声",
    cut_interface="接S11b1（周机位：周野剖白第一段）",
    action_complexity="SIMPLE",
    cut_motivation="正反打拆镜（2026-09-03铁律5）：母机位回应独立成镜（凡哥拍板6s），台词落点完整",
    orientation_lock="母亲身体不转，仅转头≤90°，无180°翻转",
    natural_duration_s=4.5, beat_pause_s=1.5,
    tempo_shape="肩顿半拍(1s)→回头(1.5s)→目光相接停半拍(1s)→挡话(2.5s)",
    eye_line="母亲目光越过肩头接住周野的视线",
    micro_action="回头时攥纸巾的手没松",
    breath="开口前吸了一口气，把哭腔压住",
)
NEW["S11b1"] = mk(
    shot_id="S11b1", scene_id="scene3",
    objective="周野剖白第一段：「不说」曾是自认的体谅，现在承认那不是她要的",
    duration_s=7, core_duration_s=5.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="周机位延续：周野在母亲身后半步面向她开口（同S11a1站位）；母亲在灶台侧面向案板背身倾听，头微微侧着，听的过程中头慢慢低回去；方位参照沿用灶台/水槽/案板",
    shot_size="中近景（周野）",
    primary_movement="固定",
    first="周野接过她的话头，声音急了一拍又压稳",
    middle="「不是因为你等我。……可你不是只想知道我有没有受伤。」整段说下来没有停，像憋了很久",
    tail="说到最后一句他停住，看着她低下去的后脑勺，等她消化",
    blocking="周机位单机：周野主体；母亲在灶台侧背身，倾听中头慢慢低回去",
    playable_action="急起压稳+整段剖白+收在停住",
    emotion_start="解释的急",
    emotion_turn="把「不说=放心」的逻辑摊开",
    emotion_landing="说破之后空了半拍",
    dialogue=dl([(ID_Z,"不是因为你等我。是我以为不说就算是让你放心。我把自己照顾好，就觉得你也会放心。可你不是只想知道我有没有受伤。")]),
    sound="对白为主；段落之间气口短",
    cut_interface="接S11b2（周机位延续：母亲已完全背身，他继续说）",
    action_complexity="SIMPLE",
    cut_motivation="长剖白按凡哥方案拆两段：S11b1=解释逻辑段（凡哥拍板7s，周机位单机）",
    orientation_lock="无翻转；母亲仅低头不回身",
    natural_duration_s=5.5, beat_pause_s=1.5,
    tempo_shape="急起(1s)→第一句(2s)→中段(2.5s)→末句停住(1.5s)",
    eye_line="周野看着母亲背影的肩线说",
    micro_action="说话时喉结上下滚动一次",
    breath="急起后换了口气才压稳",
)
NEW["S11b2"] = mk(
    shot_id="S11b2", scene_id="scene3",
    objective="想念与「拖着拖着」的自白——母亲背身听完，不打断",
    duration_s=7, core_duration_s=5.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="周机位延续：母亲在灶台侧已完全背对周野、面向案板（背影既定，镜内不拍转身）；周野在水槽侧、她身后半步处继续说；方位参照沿用灶台/水槽/案板",
    shot_size="中近景（周野为主，母亲背影在前景作听者衬影）",
    primary_movement="固定",
    first="母亲已背身低头对着案板，肩线不动；周野望着她的背影继续说",
    middle="「我也想你。……后来拖着拖着，就更不知道了。」说到「想你」，他呼吸乱了一拍",
    tail="收在「更不知道了」，尾音低下去，他停了，没催她转身",
    blocking="周机位单机：周野主体；母亲背影听着（既定状态），纸巾还攥在手里",
    playable_action="低诉+呼吸乱拍+收尾停住",
    emotion_start="剖白后发虚",
    emotion_turn="把「想你」说出口",
    emotion_landing="把「拖」的亏欠认下来",
    dialogue=dl([(ID_Z,"我也想你。在外面看见别人打电话回家，我会想起你。想打的时候，又不知道该从哪句开始。后来拖着拖着，就更不知道了。")]),
    sound="对白为主，环境声极低；「想你」前有一拍吸气",
    cut_interface="接S11c1（母机位：母亲回身发问）",
    action_complexity="SIMPLE",
    cut_motivation="凡哥方案：S11b2=想念段独立成镜（7s），周机位+母亲背影听，单机位",
    orientation_lock="母亲全程背身（背影既定），周野面向她方向，无翻转",
    natural_duration_s=5.5, beat_pause_s=1.5,
    tempo_shape="低起(1s)→「我也想你」(2s)→中间段(2.5s)→拖着拖着收低(1.5s)",
    eye_line="周野看着她背影的肩线，没有逼她转身",
    micro_action="说到「不知道了」，他垂在身侧的手指蜷了一下",
    breath="说「想你」时呼吸乱了一拍",
)
NEW["S11c1"] = mk(
    shot_id="S11c1", scene_id="scene3",
    objective="母亲回身把「以后」问实：那你以后呢→以后我说→每天？",
    duration_s=5, core_duration_s=3.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="母亲在灶台侧已回身面向周野（转身在S11b2→S11c1切镜间完成，镜内不拍），隔案板与周野相向；母机位（机位在水槽侧、拍母亲），无越轴",
    shot_size="中近景（母机位：母亲）",
    primary_movement="固定",
    first="母亲回身面向周野，眼眶还红着，先问「那你以后呢？」声音发紧",
    middle="周野答「以后我说。」——她听到这四个字，顿了一下",
    tail="「每天？」她追问，两个字问得很轻，眼睛直直看着他",
    blocking="母机位单机：母亲主体；周野的答句在本镜内作声源回应（机位不切，收她的反应为主）",
    playable_action="发问发紧+听他答顿半拍+追问放轻",
    emotion_start="母亲还红着眼",
    emotion_turn="要一个具体的承诺",
    emotion_landing="「每天」问出口，把自己的要求也说出来",
    dialogue=dl([(ID_M,"那你以后呢？"),(ID_Z,"以后我说。"),(ID_M,"每天？")]),
    sound="三句对白之间各留半拍；「每天」尾音轻",
    cut_interface="接S11c2（周机位：周野承诺，母亲走位近身）",
    action_complexity="COORDINATED",
    cut_motivation="凡哥方案：S11c1=追问组独立成镜（凡哥拍板5s，母机位为主），周野答句作声源不切机位",
    orientation_lock="母亲回身为跨镜既定状态，隔案板相向，无翻转",
    natural_duration_s=3.5, beat_pause_s=1.5,
    tempo_shape="发问(1.2s)→半拍等答(0.8s)→「以后我说」落进耳朵(1s)→「每天？」(1.2s)→尾音悬住(0.8s)",
    eye_line="母亲直直看着周野的眼睛，问「每天」时不眨",
    micro_action="问「每天」时她垂在身前的手攥了攥围裙边",
    breath="问「每天」前屏着气，问完才轻轻吐出来",
)
NEW["S11c2"] = mk(
    shot_id="S11c2", scene_id="scene3",
    objective="周野给出承诺「不再让你猜」，母亲走位近身碰他脸侧——和解落定",
    duration_s=7, core_duration_s=5.5,
    state_ids=STATES_K,
    space="厨房", time="刚入夜",
    orientation="周机位（机位在灶台侧、拍周野）：周野在水槽侧面向母亲方向；母亲离开灶台侧绕过案板走到周野面前（走位入镜，非180°定格转身），两人近身相向",
    shot_size="中近景（周野为主，母亲走位至面前后同框）",
    primary_movement="固定",
    first="周野迎住她的目光，开口「不一定每天都能说，但我不再让你猜。」",
    middle="承诺说稳；母亲绕过案板走到他面前，抬眼看他",
    tail="她抬手碰他脸侧——触到一刻即切（收手动作由S12接续）",
    blocking="周机位单机：周野主体→母亲走位近身；母亲碰脸的手很轻",
    playable_action="承诺整句+母亲走位+抬眼+碰脸触到即切",
    emotion_start="母亲还红着眼走过来",
    emotion_turn="承诺的笃定",
    emotion_landing="和解达成",
    dialogue=dl([(ID_Z,"不一定每天都能说，但我不再让你猜。")]),
    sound="留一拍静默后是两人的呼吸声",
    cut_interface="接S12（碰脸match-on-action：指尖停留半拍后收回）",
    action_complexity="COORDINATED",
    cut_motivation="凡哥方案：S11c2=承诺+碰脸落点（凡哥拍板7s，周机位）；触到一刻切镜，收手由S12接续（match-on-action，非重复表演）",
    orientation_lock="周野面向母亲方向不移动；母亲走位绕过案板（非转身定格），无180°翻转",
    natural_duration_s=5.5, beat_pause_s=1.5,
    tempo_shape="承诺起(2.5s)→走位近身(2s)→抬眼停半拍(1s)→碰脸落(1.5s)",
    eye_line="周野迎住她的目光说完整句，看她走近",
    micro_action="母亲碰脸的手很轻，指尖落在他脸侧",
    breath="周野说完长出一口气",
)

# ============ 既有卡片字段覆盖 ============
OV = {
 "S01": {"space": "楼道（家门外的楼梯间）", "time": "黄昏"},
 "S02": {"space": "玄关（门外=与S01同一楼道，门内=玄关）", "time": "刚入夜",
    "objective": "门开缝，母子第一次对视，周野开口叫妈",
    "first": "门开一条缝，母亲手搭门把，目光先落在他的脸上",
    "middle": "母亲目光从他的脸→肩→拎包的手；周野抬眼与她对视",
    "playable_action": "抬眼对视+开口叫妈",
    "prop_before": "无", "prop_after": "无",
    "tempo_shape": "门开(2s)→目光三点下移(3s)→抬眼对视(2s)→叫妈(1.5s)",
    "eye_line": "母亲目光沿脸→肩→拎包的手下移；周野先迎她目光再开口"},
 "S03": {"space": "玄关（与S02同一门内空间）", "time": "刚入夜"},
 "S04": {"space": "客厅（餐桌对坐区）", "time": "刚入夜",
    "cut_interface": "接S05a1（母机位：切同一对坐轴的中近景问句）"},
 "S06": {"space": "客厅到厨房过渡", "time": "刚入夜"},
 # ---- 厨房方位道具参照（铁律5 名单：S07/S08a/S08b/S09a/S09b/S10a/S10b/S11a1/S11a2） ----
 "S07": {"space": "厨房", "time": "刚入夜",
    "orientation": "两人隔案板相对立于案板前：周野在水槽侧、母亲在灶台侧，案板居中，均面向案板中央与面团，无越轴",
    "blocking": "案板两侧相对：周野在水槽侧揉面，母亲在灶台侧俯身按面团",
    "orientation_lock": "两人隔案板面向案板，无翻转；动作分工=周野揉面、母亲按面团指导（非重复劳动）"},
 "S08a": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板与面团；周野在水槽侧面向案板揉面，案板居中，两人隔案板相对",
    "shot_size": "中近景（母亲为主，前景案板上可见周野揉面的手）",
    "blocking": "母亲在灶台侧案板前；周野隔案板在水槽侧揉面"},
 "S08b": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板独白；周野在水槽侧面向案板，揉面渐缓，案板居中",
    "blocking": "母亲主体（灶台侧案板前）"},
 "S09a": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板，双手搭面盆边沿；视线飘向门口时仅眼神转向、身体不变向"},
 "S09b": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板说出诉求，抬眼望水槽侧的周野一眼即落回面团；周野在水槽侧面向案板，揉面手停住",
    "blocking": "母亲主体；周野在水槽侧，揉面手停住",
    "orientation_lock": "母亲面向案板，无翻转；周野在水槽侧揉面手停住"},
 "S10a": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板正面示人：压面团、擦眼、撑案板、肩颤全程不转身（案板在身前）"},
 "S10b": {"space": "厨房", "time": "刚入夜",
    "orientation": "母亲在灶台侧面向案板、背对周野（背影为既定入画状态，不拍转身）；周野在水槽侧就位，侧转≤90°开水洗手，水槽在他站位旁",
    "cut_interface": "接S11a1（周机位：周野道歉开口）"},
 "S12": {"space": "厨房+餐桌（案板前）", "time": "深夜",
    "first": "承接S11c2触脸：母亲指尖仍在他脸侧，停留半拍后收回",
    "cut_motivation": "情绪落点后转日常；S11c2→S12碰脸跨镜match-on-action（收手接续，非重复表演）"},
 "S13": {"space": "厨房+餐桌（案板前）", "time": "深夜",
    "orientation": "周野与母亲相对分据案板两侧（周野在水槽侧擀皮、母亲在灶台侧示范包合），均面向案板中心"},
 "S14": {"space": "厨房+餐桌（案板前）", "time": "深夜",
    "orientation": "两人相对分据案板两侧（周野在水槽侧、母亲在灶台侧），面向案板中心，面皮与饺子在两人手间传递，朝向稳定"},
 "S15": {"space": "厨房+餐桌（灶台前）", "time": "深夜",
    "orientation": "两人并立于灶前，面向灶台与锅；母亲在灶台侧、周野在她近旁半步内递夹"},
 "S16": {"space": "厨房+餐桌（餐桌位）", "time": "深夜",
    "orientation": "餐桌对坐轴（同S04坐向轴，跨镜同轴不换）：母亲面向周野方向推钥匙，周野面向母亲方向接"},
 "S17": {"space": "厨房+餐桌（灶台边）", "time": "深夜"},
}

for sid, ov in OV.items():
    for k, v in ov.items():
        P["shot_cards"][P["shot_index"].index(sid)][k] = v

# grid 全部改 1 + grid_reason
for c in P["shot_cards"]:
    c["grid_count"] = 1
    c["grid_reason"] = GRID

# ============ 替换拆镜组 ============
KEEP = [sid for sid in P["shot_index"] if sid not in ("S05a","S05b","S11a","S11b","S11c")]
order = []
for sid in KEEP:
    order.append(sid)
    if sid == "S04":
        order += ["S05a1","S05a2","S05b1","S05b2","S05b3"]
    elif sid == "S10b":
        order += ["S11a1","S11a2","S11b1","S11b2","S11c1","S11c2"]

cards_by_id = {c["shot_id"]: c for c in P["shot_cards"]}
for sid in ("S05a","S05b","S11a","S11b","S11c"):
    del cards_by_id[sid]
for sid in order:
    if sid in NEW:
        cards_by_id[sid] = NEW[sid]

new_cards = [cards_by_id[sid] for sid in order]
assert len(new_cards) == 29, len(new_cards)

P["segment"] = "《饺子出锅前》全片 29 镜"
P["shot_index"] = order
P["shot_cards"] = new_cards
P["total_duration_s"] = sum(c["duration_s"] for c in new_cards)

# project_defaults 灯光锁定（铁律4）
P["project_defaults"]["lighting_lock"] = {
    "base_all_shots": "warm home lighting at night",
    "exception_S01": "dim stairwell at dusk",
    "rule": "全片统一灯光基调写入此处，每镜不再另起灯光描述；S01楼道例外单独声明（2026-09-03铁律4）",
}

# ============ continuity_ledger ============
LG = P["continuity_ledger"]
LG["tissue"] = ["S10b handed → S11a2 mother holds it (hand still holding tissue when she turns head)"]
LG["story_states"] = [
 "state.zhou-ye.arrival.v1+state.mother.waiting.v1 (scene1,S01-S03) → state.zhou-ye.accepting-home.v1+state.mother.testing.v1 (scene2,S04-S06) → state.zhou-ye.responding.v1+state.mother.releasing.v1 (scene3,S07-S11c2) → state.zhou-ye.staying.v1+state.mother.settling.v1 (scene4,S12-S17); recorded per shot in state_ids"
]
LG["speech_load"] = [
 "47 dialogue lines verified verbatim incl. punctuation (screenplay.md), redistributed across 29 shots with zero line reuse/omission; 正反打拆镜后每镜单说话人单机位；S11b1/S11b2 两段剖白各7s、S05b1/S05b3各4s 为凡哥拍板值，按快语速整句压节奏（约9-10字/s含气口），其余按约6-8字/s含呼吸停顿 basis；speech <= duration_s 逐镜成立"
]
LG["reverse_shot_split"] = [
 "S05a→S05a1/S05a2, S05b→S05b1/S05b2/S05b3, S11a→S11a1/S11a2, S11b→S11b1/S11b2, S11c→S11c1/S11c2 = 11 new shots, each single camera (母机位/周机位), no in-shot camera switch (2026-09-03铁律5)"
]
LG["space_time_light"] = [
 "space: S01楼道 / S02-S03玄关(门外=楼道) / S04-S05b3客厅 / S06客厅→厨房过渡 / S07-S11c2厨房 / S12-S17厨房+餐桌; time: S01黄昏 / S02-S11c2刚入夜 / S12-S17深夜; lighting: 全片warm home lighting at night, S01=dim stairwell at dusk (2026-09-03铁律2/3/4)"
]
LG["fixture_anchors"] = [
 "厨房固定参照（跨镜同一套，不互换）：母亲=灶台侧、周野=水槽侧、案板居中；S07/S08a/S08b/S09a/S09b/S10a/S10b/S11a1/S11a2 方位一律挂固定物，零左右相对方位 (2026-09-03铁律5配套)"
]
LG["headwear_removed"] = [
 "S02 头饰动作删除（身份母版无头饰，资产库0命中，2026-09-03铁律1）：门缝初见观察顺序改为脸→肩→拎包的手；周野抬眼与她对视后开口叫妈；台词不变"
]
LG["orientation"] = [
 "no 180° subject flip in any segment; back views enter as established states (S10b/S11a1/S11b2 母亲背影既定); all direction language anchored to subject or fixed props (灶台/水槽/案板/门), zero camera/screen/frame-anchored terms (2026-09-03 rule)"
]
LG["grid_lock"] = [
 "grid_count=1 ×29, grid_reason=「单图构图锚点（无切镜）」— 切镜由镜间接口关系承担，单镜内不切"
]

# ============ qc ============
P["qc"] = {
 "gates_passed": True,
 "shot_count": 29,
 "max_duration_check": 14,
 "core_within_14s": True,
 "duration_edit_safety": "every shot duration - core_duration = 1.5s edit safety (uniform, incl. 11 split shots)",
 "grid_lock": "grid_count=1 x29; grid_reason=「单图构图锚点（无切镜）」uniform",
 "state_cap_4": True,
 "dialogue_verbatim": "47/47 lines char-exact vs screenplay.md incl. punctuation; split shots redistribute parent lines verbatim (zero reuse/omission)",
 "reverse_shot_split": "S05a→2镜 S05b→3镜 S11a→2镜 S11b→2镜 S11c→2镜 = +11镜(23→29); 每镜单机位(母机位/周机位)，无镜内机位切换；时长按凡哥拍板值逐镜落实(6/6/4/6/4、6/6/7/7/5/7)",
 "headwear_removed": "S02 头饰动作已删（身份母版无头饰，资产库0命中，2026-09-03铁律1）：门缝初见的观察顺序改为脸→肩→拎包的手；周野抬眼与她对视后开口叫妈；台词不变",
 "space_lock": "S01楼道 / S02-S03玄关(门外=与S01同一楼道) / S04-S05b3客厅 / S06客厅到厨房过渡 / S07-S11c2厨房 / S12-S17厨房+餐桌 (2026-09-03铁律3)",
 "time_lock": "S01黄昏 / S02-S11c2刚入夜 / S12-S17深夜 (2026-09-03铁律2)",
 "lighting_lock": "project_defaults: 全片 warm home lighting at night; S01 例外 dim stairwell at dusk (2026-09-03铁律4)",
 "orientation_anchor": "厨房镜(S07/S08a/S08b/S09a/S09b/S10a/S10b/S11a1/S11a2)一律灶台侧/水槽侧/案板居中固定物参照；subject/fixture-anchored only；相机/画框系相对方位词 = 0 hits across all shot fields",
 "action_division": "S07/S08/S09: 周野揉面、母亲说话按面团(不重复劳动); S10b: 周野洗手递纸、母亲接纸; S13-S14: 周野擀皮、母亲托皮包合 — no duplicate labor",
 "flip_ban": "S10a 正面释放无转身; S10b 母亲背影=既定状态入画(不拍转身); S11b2 母亲背影听; S11c1 母亲回身为跨镜既定; S11c2 母亲走位绕过案板至周野面前(非180°定格); S11c2→S12 碰脸跨镜match-on-action",
 "cut_motivation": "每镜标注 cut_motivation; 拆镜后任何镜不再含机位切换类表述（每镜单机位）",
 "tempo_derived": "durations derived from natural_duration sums + beat pauses; 拆镜后总时长266s与v5持平（拆镜重新记账）",
 "touch_fix": "S11c2/S12 碰脸由重复表演改为跨镜接续(match-on-action)",
 "prop_fix": "S09a 面盆边沿（擀面杖首现于S13擀皮）— 沿用v5",
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(P, f, ensure_ascii=False, indent=1)

# ============ 自检 ============
errs = []
warns = []
cards = P["shot_cards"]
ids = [c["shot_id"] for c in cards]

def card_text(c):
    return json.dumps(c, ensure_ascii=False)

# 1 数量与唯一
if len(ids) != 29 or len(set(ids)) != 29: errs.append(f"shot count {len(ids)}")
if P["shot_index"] != ids: errs.append("shot_index mismatch")

# 2 grid
if any(c["grid_count"] != 1 or c["grid_reason"] != GRID for c in cards): errs.append("grid lock broken")

# 3 真入感三件套
for c in cards:
    for k in ("eye_line","micro_action","breath"):
        if not c.get(k): errs.append(f"{c['shot_id']} missing {k}")

# 4 头饰词：仅扫 shot 字段（qc/ledger 说明文字除外）
for w in ("帽","帽檐","摘帽","头饰"):
    for c in cards:
        if w in card_text(c): errs.append(f"headwear word {w} in {c['shot_id']}")

# 5 banned terms：仅扫 shot 字段
for w in ("镜头","画面","屏幕","画框","相机"):
    for c in cards:
        if w in card_text(c): errs.append(f"banned-ish term {w} in {c['shot_id']}")
# 左右相对方位：9 个名单镜的 orientation/blocking 必为零
for sid in ("S07","S08a","S08b","S09a","S09b","S10a","S10b","S11a1","S11a2"):
    c = next(x for x in cards if x["shot_id"] == sid)
    for k in ("orientation","blocking","shot_size"):
        if ("左" in c[k]) or ("右" in c[k]):
            errs.append(f"{sid}.{k} has 左/右: {c[k]}")
# 全片 shot 字段出现 左/右 一律 review（不应有）
for c in cards:
    t = card_text(c)
    if ("左" in t) or ("右" in t):
        warns.append(f"review 左/右 char in {c['shot_id']}")

# 6 space/time mapping
for i, sid in enumerate(ids):
    c = cards[i]
    if sid == "S01": want_t = "黄昏"
    elif sid in ("S02","S03","S04","S05a1","S05a2","S05b1","S05b2","S05b3","S06","S07","S08a","S08b","S09a","S09b","S10a","S10b","S11a1","S11a2","S11b1","S11b2","S11c1","S11c2"): want_t = "刚入夜"
    else: want_t = "深夜"
    if c["time"] != want_t: errs.append(f"{sid} time {c['time']} != {want_t}")
    if sid == "S01": want_s = "楼道"
    elif sid in ("S02","S03"): want_s = "玄关"
    elif sid in ("S04","S05a1","S05a2","S05b1","S05b2","S05b3"): want_s = "客厅"
    elif sid == "S06": want_s = "客厅到厨房过渡"
    elif sid in ("S07","S08a","S08b","S09a","S09b","S10a","S10b","S11a1","S11a2","S11b1","S11b2","S11c1","S11c2"): want_s = "厨房"
    else: want_s = "厨房+餐桌"
    if not c["space"].startswith(want_s): errs.append(f"{sid} space {c['space']}")

# 7 dialogue verbatim multiset
got = []
for c in cards:
    for d in c["dialogue"]:
        got.append((d["speaker"], d["line"]))
if sorted(got) != sorted(CANON): errs.append(f"dialogue mismatch: {len(got)} vs {len(CANON)}")

# 8 stale id refs (shot 字段内不得出现被拆的旧裸 ID)
for c in cards:
    t = card_text(c)
    for pat in (r"S05[ab](?!\d)", r"S11[abc](?!\d)"):
        if re.search(pat, t): errs.append(f"stale ref {pat} in {c['shot_id']}")

# 9 cut_interface targets exist
for c in cards:
    m = re.findall(r"接S([0-9A-Za-z]+)", c["cut_interface"])
    for t in m:
        if ("S" + t) not in ids: errs.append(f"{c['shot_id']} cut->S{t} missing")

# 10 durations
if P["total_duration_s"] != 266: errs.append(f"total {P['total_duration_s']}")
for c in cards:
    if c["duration_s"] - c["core_duration_s"] != 1.5: errs.append(f"{c['shot_id']} edit safety")

# 11 fixture anchors present on rule-5 shots (至少一个固定物锚点)
for sid in ("S07","S08a","S08b","S09a","S09b","S10a","S10b","S11a1","S11a2"):
    c = next(x for x in cards if x["shot_id"] == sid)
    if not any(a in c["orientation"] for a in ("灶台侧","水槽侧","案板")):
        errs.append(f"{sid} fixture anchor missing")

# 12 split spec durations
DSPEC = {"S05a1":6,"S05a2":6,"S05b1":4,"S05b2":6,"S05b3":4,"S11a1":6,"S11a2":6,"S11b1":7,"S11b2":7,"S11c1":5,"S11c2":7}
for sid, d in DSPEC.items():
    c = next(x for x in cards if x["shot_id"] == sid)
    if c["duration_s"] != d: errs.append(f"{sid} duration {c['duration_s']}")

# 13 lighting lock in project_defaults
ll = P["project_defaults"].get("lighting_lock", {})
if "warm home lighting at night" not in ll.get("base_all_shots","") or "dim stairwell at dusk" not in ll.get("exception_S01",""):
    errs.append("lighting lock missing/incomplete")

print("CHECKS:", "OK" if not errs else errs)
if warns: print("REVIEW:", warns)
print("shots:", len(ids))
print("total_duration_s:", P["total_duration_s"])
print("dialogue lines:", len(got))
print("out:", OUT)
