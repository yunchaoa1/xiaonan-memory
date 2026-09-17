# 官方原生 r2v 模板提示词样例（MiniMaxH3ReferenceToVideo，非 Director 六段）

适用：ComfyUI 0.30.0 自带官方模板「MiniMax H3：参考生视频」（前端 Library→Video）
提示词格式 = **单段自然语言**（英文）+ `<Picture N>` 引用 + `<d>[Language] 台词</d>`。
不用 Director 的 subject_definitions/summary/retention_analysis 六段结构。
参考图挂 ref_image_0..8（LoadImage 节点）；ResolutionSelector 控分辨率（megapixels 0.4→2.0）；
Duration 填秒，官方自动算 17n+5 帧（8s=192 帧、15s=362 帧、5s=124 帧）。
纯文本全正向；画面方向以主体自身为锚点；单镜加 locked camera/no cuts 声明。

## 8s 入门镜（回家·门口，音频验证通过版）

A warm 3D animated film style, cinematic soft indoor lighting. A young woman around 20 years old, black long straight hair with a white hair clip on the left side, cream knit cardigan over a white camisole, silver necklace with a blue teardrop pendant, light blue cuffed jeans and black shoes, exactly matching the character sheet <Picture 1>. She stands in the entryway of a modest living room, a closed front door directly behind her, warm living room before her. She looks slightly down at first, hands resting naturally at her sides, then lifts her eyes from the floor toward the living room, a soft fond smile forming; her fingers curl gently against the hem of her cardigan, she takes a small breath and holds it a beat, then speaks in a soft warm sweet young female voice at a gentle pace: <d>[Chinese] 爷爷，我回来了。</d> As she finishes, her smile deepens, her eyes soften, and she takes one relaxed half-step forward into the living room, letting the breath out slowly. Soft quiet indoor ambience, faint muffled sounds from outside the closed front door, the light rustle of her cardigan as she moves, the soft fabric sound of her step forward, clear clean audio.

## 15s 长镜（进门→见爷爷→依偎，H3 时长上限压测）

Warm 3D animated film style, cinematic soft indoor lighting, one continuous locked camera shot throughout, no cuts, a gentle 15 seconds of everyday homecoming. A young woman around 20, black long straight hair with a white hair clip on the left side, cream knit cardigan over a white camisole, silver necklace with a blue teardrop pendant, light blue cuffed jeans and black shoes, exactly matching the character sheet <Picture 1>.

The front door of a modest warm home opens inward and she steps into the entryway carrying a small cloth tote bag, closes the door softly behind her with a gentle click, sets the bag down on the low wooden shoe bench, and slips off her shoes. She takes a slow breath of the warm air, walks two relaxed steps into the living room, and her eyes search softly toward an armchair by the window where her grandfather is dozing. Her face lights up with a fond, tender smile. She pads quietly closer, stops beside the armchair, tilts her head warmly, and speaks in a soft, warm, sweet young female voice at a gentle pace: <d>[Chinese] 爷爷，我回来了。</d> Her grandfather stirs awake with a drowsy blink and returns a crinkly smile; she giggles softly, kneels down beside the armchair, and rests her head briefly against his knee, eyes closing in quiet contentment.

Soft indoor ambience: faint muffled street sounds from behind the closed front door, the quiet creak of floorboards under her steps, the light rustle of her cardigan, the grandfather's slow gentle breathing, warm clean room tone, clear clean audio.

## 写作要点

- 15s 长镜动作多：用自然顺序词(first/then/after/and)串动作弧线，台词放中后段；未锁参考的角色（如爷爷）=生成角色，接受漂移
- 第二角色互动可写（打盹的爷爷/醒来笑），但别让非锁定角色抢戏
- 台词 `<d>[Chinese] 台词。</d>`（[Chinese] 后带空格；句末标点）
- 音景 2-3 句收尾（环境声+衣物声+角色呼吸），正向无否定词
