# 星火智画 实际路由表（2026-07-17 从JS bundle提取）

## 前台页面路由（非API）

```
/                              ✅ 着陆页
/login                         ✅ 登录
/register                      ✅ 注册
/forgot-password               ❌ 忘记密码
/workspace-select              ✅ 工作空间选择
/personal-scene-select         ✅ 个人场景选择
/scene-selection               ❌ 场景选择（另一视图）
/dashboard                     ✅ 短剧工作台
/dashboard/ecommerce           ❌ 电商工作台（路径需修正）
/dashboard/media               ❌ 新媒体工作台（路径需修正）
/adaptations                   ✅ 剧本项目列表
/adaptation                    ✅ 剧本改编
/import-screenplay             ❌ 导入剧本
/new                           ❌ 快速新建项目
/image-creation                ✅ 图片设计
/product-images                ❌ 产品图生成（电商）
/asset-library                 ✅ 资产库（路径需修正）
/video-fusion                  ✅ 视频创作
/audio-generation              ❌ 音频生成
/creative-canvas               ❌ 创意画布（图片生成主界面）
/ai-usage                      ❌ AI用量统计
/credits                       ❌ 积分中心
/deliverables                  ❌ 交付物管理
/submit                        ❌ 提交发布
/task                          ❌ 任务
/tasks                         ❌ 任务列表
/team                          ❌ 团队主页
/team/setup/join               ❌ 加入团队
/invite                        ❌ 邀请页
/settings                      ✅ 设置
/status                        ❌ 状态页
/events                        ❌ 事件
/user-feedback                 ❌ 用户反馈
/privacy                       ❌ 隐私政策
/terms                         ❌ 服务条款
/content-policy                ❌ 内容政策

/tools/cover-gen               ❌ 封面生成
/tools/ecommerce-video-remake  ❌ 电商视频重制
/tools/subtitle-removal        ❌ 字幕擦除
/tools/video-breakdown         ❌ 视频拆解
/tools/video-remake            ❌ 视频重制
/tools/video-translation       ❌ 视频翻译
/tools/video-upscale           ❌ 视频增强
/tools/viral-video-remake      ❌ 爆款视频重制
```

## 统计

- 总路由：约40个
- 已复刻：约22个 ✅
- 待补：约18个 ❌
- 需修正路径：3个（ecommerce→/dashboard/ecommerce等）
