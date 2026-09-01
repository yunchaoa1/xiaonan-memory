# OPC道具分级与场景一致性查证记录 v0.1

## 已锁定结论

主体资产不等于剧本拆解清单。剧本拆解应记录演员使用、携带或交互的全部道具；主体资产只生成英雄/高视觉一致性道具。

独立道具主体图的判断条件：计划特写或插入镜头；剧情专属且观众必须识别的独特轮廓/标记/结构；同一独特物件跨镜或跨场反复成为视觉焦点；或可见状态变化必须靠同一具体外观辨认。仅仅被拿取、交接、具有象征意义或存在状态链，不足以升级。

普通家用钥匙在《饺子出锅前》中没有特写、独特外观或高视觉识别要求，因此降为B级镜头道具：保留持有/交接连续性，不生成独立主体图。周野的包仍因贯穿入场、放置和结尾留在玄关而保留独立道具资产。

## 两层主体资产流程

第一层为客户确认模板：

- 场景：正交或近正交俯视、去顶/剖切的完整空间图，显示四面墙、门窗/开口、固定家具、关键地标坐标、人物活动区、动线、尺度、材质和主色。模板尺寸按空间形状自适应。
- 人物：上半身五官与造型特写模板，只包含人物外观、服装和佩戴配饰，不带外部道具。
- 道具：正面模板；有打开/关闭/点火等视觉功能状态时，每个必要状态各一张正面模板，锁定不变量和变化部件。

客户可要求重做；只有客户确认并锁定模板后才进入第二层。第二层全部正式扩展图统一16:9原生4K（3840×2160），扩展必须以锁定模板为首张参考。人物扩展为正面全身、单张侧面全身、背面全身、五官特写四格；场景逐机位扩展后机械拼格；道具扩展视角和已确认功能状态。

## 场景一致性方法

一次文字生成四宫格只能作为概念草图，不能直接作为场景资产。先锁一个空间母版，再从同一母版编辑不同机位；需要强几何保证时使用同一3D场景共享物体/材质，只切换相机；视角单独生成后再机械拼格。失败图表现为面板数量失控、门窗/墙体开口变化、家具新增或重排、厨房拓扑变化、餐桌移位、材质和装饰漂移。

## 查证来源

- OpenAI Image Generation：https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Image Edit API：https://developers.openai.com/api/reference/resources/images/methods/edit
- Adobe Firefly Composition Reference：https://helpx.adobe.com/firefly/web/work-with-images/generate-images/match-image-composition-to-reference-image.html
- Adobe Scene to Image：https://helpx.adobe.com/firefly/web/generate-images-with-text-to-image/generate-images-using-3d-scenes/scene-to-image.html
- Blender Scene Introduction：https://docs.blender.org/manual/en/latest/scene_layout/scene/introduction.html
- Blender Camera View：https://docs.blender.org/manual/en/latest/editors/3dview/navigate/camera_view.html
- HowToFilmSchool Hero：https://howtofilmschool.com/dictionary/hero/
- HowToFilmSchool Prop：https://howtofilmschool.com/dictionary/prop/
- No Film School Hero Prop访谈：https://nofilmschool.com/hero-prop-production-designer
- StudioBinder Script Breakdown：https://www.studiobinder.com/blog/the-complete-guide-to-mastering-script-breakdown-elements
