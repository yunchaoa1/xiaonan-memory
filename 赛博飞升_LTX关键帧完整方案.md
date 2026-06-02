# 赛博飞升 — LTX2.3 关键帧 + 提示词 完整方案
# 5段 × 5关键帧 = 25张图
# 总时长: 4+4+7+7+7 = 29秒 ≤ 30秒 ✅
# 
# 角色说明：
#   白绮罗 = 白绮罗 LoRA (3000步)
#   阿念 = 旧白绮罗 LoRA 替代
#
# 出图策略：
#   人物特写/近景 → Z-Image Turbo + 白绮罗 LoRA
#   人物+场景融合 → Z-Image LoRA人物 + Qwen2511 img2img融合裁切场景
#   纯场景/空镜 → Z-Image Turbo (不经过Qwen，因为Qwen会加人)
#   系统界面/武器道具 → Z-Image Turbo 独立生成

================================================================================
段1：镜1前半 — 睁眼→坐起→跳下→看面板
⏱ 4秒 / 96帧 / 无台词
================================================================================

【关键帧1-1】睁眼瞬间
生图提示词：
天南白绮罗，古风少女，身穿白色古装长裙，躺在床上双眼紧闭，突然猛地睁开双眼，瞳孔放大，震惊困惑的表情，脸部近景特写，茅草屋内景床上，从窗户射入的柔和晨光洒在脸上，丁达尔光效，电影质感，85mm浅景深

【关键帧1-2】从床上猛然坐起
生图提示词：
天南白绮罗，古风少女白色长裙，从茅草屋的木床上猛地坐起，上半身中景，一手撑着床板一手揉眼睛，头发凌乱，表情困惑迷惘环顾四周，茅草屋内景背景虚化，侧面角度，晨光从窗户斜射，电影质感

【关键帧1-3】发现手中武器
生图提示词：
天南白绮罗，古风少女白色长裙，坐在床边低头看着自己的右手，手中凭空出现一把散发淡蓝色微光的未来科技武器，武器表面有电路纹理和流动光点，近景特写，聚焦手和武器，表情从困惑转为惊讶，茅草屋背景虚化，暖黄光线

【关键帧1-4】跳下床站稳+系统界面弹出
生图提示词：
天南白绮罗，古风少女白色长裙，从床上跳到夯土地面双脚站稳，身体微微下蹲，面前空气中浮现一个半透明蓝色全息系统面板，面板上显示数据和操作按钮发出幽蓝光芒，主角抬头盯着面板，表情惊喜恍然大悟，茅草屋内景中景全景，光线从全息面板照亮面部

【关键帧1-5】转头看四周确认环境
生图提示词：
天南白绮罗，古风少女白色长裙，站在茅草屋中央，左手握武器右手去触碰全息面板，转头环顾四周，全景展示茅草屋全貌包括木桌厨房区域和半开木门，脸上带着兴奋跃跃欲试的表情，全息面板的蓝光和窗外暖黄自然光混合照明

--- LTX PromptRelay Block ---
Scene 1: Close-up of a young woman's face, eyes closed, lying on a straw bed in an ancient Chinese thatched hut interior, soft morning light coming through lattice window with dust particles floating in god rays. She suddenly opens her eyes wide, pupils dilating, shocked and confused expression. Camera static, 85mm close-up, shallow depth of field.
Scene 2: She sits up abruptly on the wooden bed, one hand on the bed frame the other rubbing her eyes, disheveled hair, looking around the room disoriented. Medium shot, side angle. Warm morning light from window. Slight camera movement following her motion upward.
Scene 3: She looks down at her right hand in surprise. A futuristic weapon materializes in her palm, glowing with faint blue circuit patterns and flowing light particles. Extreme close-up on hand and weapon, bokeh background. Expression shifting from confusion to awe.
Scene 4: She jumps off the bed and lands on the dirt floor, slightly crouched. A translucent holographic blue interface panel materializes in the air in front of her, displaying data and buttons with cyan glow. She stares at it, mouth slightly open, expression turning to delighted realization. Wide shot showing the room. Holographic blue light illuminating her face from below.
Scene 5: She stands in the center of the thatched hut, weapon in left hand, right hand reaching out to touch the holographic panel. She turns her head to scan the room, excited eager expression. Wide panoramic shot showing the full hut interior — wooden table and kitchen area on left, the bed behind her, double wooden doors on right. Mixed lighting: warm sunbeam from window and cool blue from holographic panel.
================================================================================

================================================================================
段2：镜1后半 — 大笑台词→抱武器
⏱ 4秒 / 96帧
🎤 台词：「哈哈哈哈！去xx的修仙，血肉苦弱！科技飞升！」
================================================================================

【关键帧2-1】仰头开始笑
生图提示词：
天南白绮罗，古风少女白色长裙，站在茅草屋内，仰头眯起眼睛，嘴角上扬开始咧嘴大笑，全息面板的蓝光从下方照亮面部，仰拍中景角度，能看到茅草屋顶木梁结构，表情从兴奋过渡到狂喜

【关键帧2-2】眯眼张嘴大笑（台词前半「哈哈哈哈！去xx的修仙」）
生图提示词：
天南白绮罗，古风少女，仰头眯眼张嘴大笑，露出牙齿，全情释放的狂笑表情，全息面板蓝光从下方打光形成戏剧性阴影，仰拍中景，头发因动作飞扬，武器握在手中微微发光，热血沸腾的氛围

【关键帧2-3】大笑+台词后半「血肉苦弱！科技飞升！」
生图提示词：
天南白绮罗，古风少女，仰头大笑达到高潮的瞬间定格，手臂微微张开像是在拥抱空气，全息面板的蓝光和窗外金色阳光在脸上形成冷暖对比，仰拍特写，眼神中充满狂喜和释放，嘴角极限上扬

【关键帧2-4】笑声渐收，低头看武器
生图提示词：
天南白绮罗，古风少女白色长裙，大笑之后笑声逐渐收敛，低下头看着手中的科技武器，眼神从狂喜转为珍爱和满足，嘴角仍挂着笑意，近景特写胸口高度，双手把武器抱在胸前，武器表面蓝色电路纹理微光流动

【关键帧2-5】抱武器+坚定表情
生图提示词：
天南白绮罗，古风少女，把科技武器紧紧抱在胸前，低头看着它，眼神坚定充满决心，脸上残留笑意但更多是坚毅，近景胸口高度，全息面板的蓝光从侧面补光，暖光从背后窗户射入形成逆光轮廓

--- LTX PromptRelay Block ---
Scene 1: She tilts her head back, eyes narrowing, corners of her mouth curling into a grin, showing teeth. Blue holographic light from below illuminates her face dramatically. Low angle medium shot, thatched roof beams visible above her. Expression transitioning from excitement to wild joy.
Scene 2: Her laughter erupts fully, mouth wide open, eyes squeezed shut in pure ecstatic release. Hair flying with her movement. One hand gripping the glowing weapon. Dramatic underlighting from holographic panel creating theatrical shadows on her face. Low angle, intense energy.
Scene 3: Peak of her ecstatic laughter. Arms slightly spread as if embracing the air. Cool blue from holographic panel and warm golden sunlight from window creating dramatic split lighting on her face. Extreme close-up, fierce joy in her eyes. She shouts the line with wild abandon.
Scene 4: Her laughter gradually subsides. She lowers her head and looks down at the weapon in her hands. Expression shifts from wild joy to tender appreciation and satisfaction. Close-up at chest height. She cradles the weapon against her chest. Blue circuit patterns pulsing softly.
Scene 5: She holds the weapon tightly against her heart, gazing down at it. Her smile remains but eyes now show fierce determination and resolve. Close-up, warm backlight from window creating a halo effect around her silhouette, blue light from the weapon and panel softly illuminating her face from front.
================================================================================

================================================================================
段3：镜2-3 — 系统界面闪回→通关提示→继续狂笑
⏱ 7秒 / 168帧  
🎤 台词：「通关了？！哈哈哈哈哈哈！！」
================================================================================

【关键帧3-1】系统界面弹出新信息
生图提示词：
半透明蓝色全息系统面板特写，悬浮在茅草屋空气中，面板上显示闪烁的文字和进度条达到100%，数据快速流动，幽蓝色光芒四射，上方有通关成功的大字提示，界面边缘有电路纹路装饰，科技感十足的UI设计，科幻电影风格

【关键帧3-2】记忆中闪过游戏画面（闪回）
生图提示词：
两个场景画面叠加过渡效果，前景是半透明蓝色全息面板的通关提示界面，背景淡入一个像素风格的游戏画面场景，像是通关瞬间的画面定格，画面边缘有不规则的溶解转场，类似记忆碎片在脑海中闪过的视觉效果，电影手法

【关键帧3-3】看到通关提示，眼睛瞪大
生图提示词：
天南白绮罗，古风少女白色长裙，站在全息面板前瞪大双眼，瞳孔因震惊而放大，嘴巴微微张开，脸被面板蓝光照亮，面部近景特写，表情从惊讶逐渐过渡到难以置信再到狂喜，光线从面板底部投射形成戏剧性光影

【关键帧3-4】举起武器欢呼
生图提示词：
天南白绮罗，古风少女，右手高举科技武器过头顶，左手握拳，仰头闭眼大喊，全身中景，身体后仰幅度很大，白色长裙因为动作飘动，全息面板在背景中发出耀眼的蓝光，武器顶部爆发光芒，热血沸腾的构图

【关键帧3-5】狂笑中蹦跳
生图提示词：
天南白绮罗，古风少女白色长裙，在茅草屋夯土地面上开心得原地蹦跳的瞬间，双手高举武器，头发飘起，裙摆飞扬，张嘴大笑露出牙齿，全景展示茅草屋空间，全息面板蓝光源和窗外阳光混合照亮整个房间，充满释放的能量感

--- LTX PromptRelay Block ---
Scene 1: Extreme close-up on the holographic blue panel floating in the air of the thatched hut. Data streams flowing rapidly, a progress bar filling to 100% with a flash. Large text appears showing mission completion. Circuit patterns along the edges of the interface. Cyan blue glow intensifies. Futuristic sci-fi UI design.
Scene 2: Dissolve transition effect. The holographic panel remains in foreground, while a pixel-art style game victory screen fades in as a background layer — like a memory flashback fragmenting and reassembling. Irregular dissolve edges. Cinematic flashback technique.
Scene 3: Close-up on her face. Her eyes widen enormously, pupils dilating with shock and realization. Mouth drops open. Blue panel light illuminating her face from below. Expression rapidly transforms from shock to disbelief to overwhelming joy. Dramatic underlighting.
Scene 4: She throws her right arm high above her head holding the weapon triumphantly, left hand clenched in a fist. Head tilted back, eyes closed, shouting with pure jubilation. Full body medium shot. White dress flowing with the motion. Holographic panel exploding with bright blue light behind her. Weapon tip glowing intensely.
Scene 5: She jumps up and down on the packed earth floor in pure celebration, weapon held high with both hands, hair flying upward, dress swirling. Mouth wide open in ecstatic laughter. Wide shot showing the full hut interior. Blue holographic light and warm sunlight filling the entire room. Explosive energy and release.
================================================================================

================================================================================
段4：镜4-7 — 栽倒→成就提示→过渡→门外敲门声
⏱ 7秒 / 168帧
🎤 台词：系统提示音「成就解锁：修仙第一人」→ 门外敲门声「咚咚咚」
================================================================================

【关键帧4-1】嗨过头向后栽倒
生图提示词：
天南白绮罗，古风少女白色长裙，在茅草屋夯土地面上向后跌坐摔倒的瞬间，身体失去平衡向后仰，双手在空中挥舞，武器脱手飞在半空，表情从兴奋变成惊慌失措，眼睛瞪圆嘴巴张大，动态定格瞬间，全景展示茅草屋，地面扬起灰尘

【关键帧4-2】坐在地上，头上弹出成就提示
生图提示词：
天南白绮罗，古风少女，跌坐在地上双腿伸直，头发散乱，一脸懵的表情，头顶上方空气中弹出一个小型半透明全息成就徽章，上面写着成就解锁的文字和图标，徽章发出淡淡的金光和粒子效果，中景，表情从懵逼慢慢变成得意微微笑

【关键帧4-3】爬起来拍拍衣服
生图提示词：
天南白绮罗，古风少女白色长裙，从地上慢慢站起来，低头用手拍打裙子上的灰尘和草屑，动作随意自然，脸上的笑意还没消失，半身中景，背景茅草屋内景，光线恢复正常的暖黄室内光，全息面板在角落变成待机状态微微发光

【关键帧4-4】捡起武器，忽然听到敲门声，转头看门
生图提示词：
天南白绮罗，古风少女，弯腰捡起掉在地上的科技武器，突然听到声音，身体僵住，侧头看向右侧的木门方向，表情从轻松变成警觉戒备，侧身中景，能看到茅草屋右侧的双开木门，门缝透进外面光线，画面聚焦主角的警觉表情

【关键帧4-5】门外一只手握拳敲击木门（观众视角看门外）
生图提示词：
茅草屋的木门外视角，一只手握拳正在敲击木门，门板因敲击产生微小震动和灰尘，手的特写占据画面主体，背景可以看到屋外的光线和模糊的户外环境，门板上木纹和门环细节清晰，动态定格，电影质感

--- LTX PromptRelay Block ---
Scene 1: She loses balance from overexcitement and falls backward onto the dirt floor. Arms flailing in the air, weapon flying from her hand. Expression shifting from joy to panic. Dynamic freeze-frame moment. Wide shot of the entire hut, dust particles kicked up from the floor. Slow motion effect.
Scene 2: She sits on the floor, legs stretched out, hair disheveled, dazed expression. A small translucent holographic achievement badge materializes above her head with a soft golden glow and particle effects. Her expression slowly transforms from confusion to a proud smirk. Medium shot.
Scene 3: She slowly gets up, brushing dust and straw off her white dress casually. Soft smile still lingering on her face. Medium shot, warm natural indoor lighting returning to normal. Holographic panel dimming to standby in the corner. Her movement is relaxed and natural.
Scene 4: She picks up the weapon from the floor. Suddenly freezes, head snapping toward the right side of the room. Her expression instantly shifts from relaxed to alert and guarded. Side angle medium shot showing the double wooden doors on the right wall, light seeping through the gap. Focus on her alert face.
Scene 5: Close-up from outside the door. A hand forms a fist and knocks hard against the wooden door. The door panel vibrates slightly, dust particles shaking loose. Extreme close-up on the fist and door surface, wood grain and door knocker details visible. Bright outdoor light behind. Dynamic frozen action.
================================================================================

================================================================================
段5：镜8-9 — 门被踢飞→主角被撞→嵌墙上→竖中指→黑幕
⏱ 7秒 / 168帧
🎤 台词：阿念「出来！」→ 白绮罗（被撞后虚弱）「……滚」→ 竖中指
================================================================================

【关键帧5-1】门被从外面一脚踢飞
生图提示词：
茅草屋内景，右侧的双开木门被一脚从外面猛力踢开，门板断裂脱离门框向屋内飞过来，木屑碎片飞溅在空中，门板运动轨迹清晰可见，门外透进刺眼的白光中有一个模糊的人影轮廓，全景动态定格，爆炸性的力量和速度感

【关键帧5-2】主角被飞来的门板撞到
生图提示词：
天南白绮罗，古风少女白色长裙，被飞来的木板正面撞到的瞬间，身体向后飞起，表情痛苦扭曲眼睛紧闭嘴巴张开，头发全部向后飞散，双手向前试图格挡但来不及，冲击力让裙摆全部向后飘起，中景动态定格，背景茅草屋墙面快速后退

【关键帧5-3】主角嵌入对面墙上
生图提示词：
天南白绮罗，古风少女，身体嵌入门对面的夯土实心墙面，墙面被撞出凹陷和裂纹，一个人形凹痕在土墙上，主角陷在墙里眼神涣散意识模糊，双手无力下垂，嘴角有血迹，白色长裙沾满灰尘和土渣，近景特写嵌入墙面，周围散落着碎土块和木屑

【关键帧5-4】从墙上抬起头，看向门口，竖中指
生图提示词：
天南白绮罗，古风少女，嵌在夯土墙里艰难地抬起头，眼神虽然涣散但透出倔强和不屈服，用尽全力抬起右手对着门口方向竖起中指，嘴角带着一丝倔强的冷笑，近景特写手指和面部，虚化背景中能看到门口逆光下阿念的模糊身影轮廓

【关键帧5-5】黑幕过渡
生图提示词：
纯黑背景，画面从四周向中心逐渐变暗至全黑，正中央残留最后一丝微弱的蓝色全息面板光点逐渐熄灭，像电视关机一样的效果，最终完全黑屏，电影黑幕转场效果，无需人物，纯视觉特效

--- LTX PromptRelay Block ---
Scene 1: The double wooden door on the right wall is kicked open from outside with explosive force. The door panel breaks free from its frame and flies inward toward the camera. Wood splinters and debris spraying in the air. Blinding white light pours through the doorway, a vague human silhouette visible in the brightness. Wide shot, dynamic frozen action. Explosive impact.
Scene 2: The main character is hit square in the chest by the flying door panel. Her body is thrown backward through the air. Face contorted in pain, eyes squeezed shut, mouth wide open. Hair flying backward wildly. Arms raised too late to block. Dress billowing backward from the impact force. Medium shot, dynamic freeze-frame against the blurring hut background rushing past.
Scene 3: She is embedded in the solid rammed earth wall opposite the door. The wall surface has cracked and caved in around her body, forming a person-shaped crater. She is dazed, eyes unfocused, arms hanging limply. Small trickle of blood at the corner of her mouth. White dress covered in dust and dirt. Close-up showing the impact crater in the wall, fragments of dried mud and wood splinters scattered around.
Scene 4: She slowly lifts her head while still embedded in the wall. Her eyes are unfocused but hold fierce defiance. With tremendous effort, she raises her right hand toward the doorway and extends her middle finger. A stubborn, rebellious smirk on her face. Close-up on her hand and face. Background blurred, showing the silhouette of Ah Nian standing in the doorway backlit by bright outdoor light.
Scene 5: Screen darkens from edges toward center like an old TV powering off. The last faint blue glow of the holographic panel shrinks to a pinprick at the center of the frame, then extinguishes completely. Pure black screen. Cinematic fade-to-black transition. No characters, pure visual effect.
================================================================================

================================================================================
📋 汇总
================================================================================

段  | 时长 | 帧数   | 台词                         | 关键帧数量
-----|------|--------|------------------------------|-----------
1   | 4s   | 0-96   | (无)                         | 5张
2   | 4s   | 97-192 | 哈哈哈哈！去xx的修仙…          | 5张
3   | 7s   | 193-360| 通关了？！哈哈哈哈哈哈！！       | 5张
4   | 7s   | 361-528| (系统音) + 敲门声咚咚咚        | 5张
5   | 7s   | 529-696| 滚                           | 5张
-----|------|--------|------------------------------|-----------
合计 | 29s  | 696帧  |                              | 25张 ✅

出图顺序建议：先出场景/道具/空镜（段4-5、段5-1、段5-5），再出人物图
出图工具：人物用 Z-Image Turbo + 白绮罗 LoRA，场景融合用 Qwen 2511 img2img
