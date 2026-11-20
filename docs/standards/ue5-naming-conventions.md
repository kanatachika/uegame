# UE5 资产与代码命名规范

做 UE5 项目最怕两件事：一是 `Content/` 里混进中文或空格导致打包莫名报错；二是资产全叫 `NewBlueprint`、`Test1`、`Jump2`，过两周连自己都分不清哪个是技能、哪个是贴图。

这份规范不搞繁琐教条，只定我们做《点数 / DICEBODY》真正常用的命名规则，大家起名时花 5 秒钟对齐一下就行。

---

## 1. 三条铁律（所有人必看）

1. **引擎内一切文件夹和资产名，只用英文、数字和下划线 `_`**
   - 严禁出现中文、空格、括号、斜杠等特殊字符（注：`docs/` 目录下的文档可以用中文，但 `Content/`、`Source/`、`Config/`、`Plugins/` 里绝对不行）。
   - 推荐大驼峰拼写（PascalCase）：`GA_Move_Sprint`、`WBP_BodySlot_HUD`。
2. **统一结构：`前缀_分类或部位_具体名称[_后缀]`**
   - 例子：`GA_Move_Slide`（技能_移动类_滑铲）、`T_Armor_Leg_D`（贴图_腿部护甲_基础色）。
   - 有了前缀，在 UE5 内容浏览器里直接搜 `GA_` 就能列出全部模块技能，搜 `DT_` 就能找到全部配表。
3. **改名或挪位置后，顺手清一下重定向器（Redirectors）**
   - 在 UE5 编辑器里移动或重命名资产后，右键对应文件夹点 **Fix Up Redirectors**，避免留下幽灵引用锁死旧路径。

---

## 2. 玩法与 GAS（Gameplay Ability System）前缀

本项目的核心能力、跨载体改造词条与机关系统预计基于 GAS + 配表来做（玩法规则见 [游戏设定集（草案 v2）](../design/游戏设定集_草案v2.md) 与 [成品 v1 基线](../design/游戏设定集_成品v1.md)），这一组前缀大家用得最多：

| 前缀 | 资产类型 | 在本项目里通常用来做什么 | 命名示例 |
| :--- | :--- | :--- | :--- |
| `GA_` | Gameplay Ability | 具体的动作、武器、防具与改造词条能力（滑铲、跳、爬、投掷、连发、震荡波） | `GA_Move_Slide`、`GA_Move_DoubleJump`、`GA_Mod_Shockwave` |
| `GE_` | Gameplay Effect | 扣防具耐久、触发流血、重置状态、发改造点、技能冷却（严守零数值成长） | `GE_Armor_CostDurability`、`GE_Status_Bleed`、`GE_Round_ResetState` |
| `GC_` | Gameplay Cue | 受击/碎甲飞片、机关 0.3s 咔哒闪红前摇、词条剪影特效（纯表现，不影响服务器结算） | `GC_Armor_Break`、`GC_Trap_Windup`、`GC_Mod_BurstVFX` |
| `DA_` | PrimaryDataAsset / DataAsset | 单个能力、词条或地图机关的“身份证”（图标、次数、绑定的 `GA_` / 机关蓝图） | `DA_Mod_Throw`、`DA_Trap_SpringPad` |
| `DT_` | Data Table | 策划配表（词条 × 三大类变形矩阵、公共盲盒机关池、防具功能表） | `DT_ModCarrierMatrix`、`DT_TrapDraftPool` |
| `CT_` | Curve Table / Curve | 镜头俯冲缓动曲线、缩圈节奏曲线（注意：不用于数值成长） | `CT_SandtableDiveCurve` |

---

## 3. 蓝图、输入与关卡前缀

| 前缀 | 资产类型 | 说明与用途 | 命名示例 |
| :--- | :--- | :--- | :--- |
| `BP_` | Blueprint Class | 普通场景物体、角色、拾取物、据点、投射物 | `BP_Pawn_Dicebody`、`BP_CapturePoint`、`BP_PointPickup` |
| `BP_GM_` | GameMode Blueprint | 对局规则裁判（仅服务器存在） | `BP_GM_Duel1v1` |
| `BP_GS_` | GameState Blueprint | 全场共享对局状态（剩余时间、据点归属、当前回合） | `BP_GS_Duel1v1` |
| `BP_PC_` | PlayerController Blueprint | 玩家控制器（输入分发、UI 开关） | `BP_PC_DuelPlayer` |
| `BP_PS_` | PlayerState Blueprint | 玩家当局公开/同步数据（命数、点数、已装模块同步） | `BP_PS_DuelPlayer` |
| `ABP_` | Animation Blueprint | 角色/手臂动画蓝图 | `ABP_Dicebody_FirstPerson`、`ABP_Dicebody_ThirdPerson` |
| `WBP_` | Widget Blueprint | UMG 界面控件 | `WBP_HUD_BodyDurability`、`WBP_Shop_CraftPanel` |
| `IA_` | Input Action | UE5 增强输入动作 | `IA_Move`、`IA_Look`、`IA_Jump`、`IA_Slide` |
| `IMC_` | Input Mapping Context | UE5 增强输入按键映射上下文 | `IMC_DefaultPawn`、`IMC_CraftMenu` |
| `L_` | Level (.umap) | 关卡地图文件 | `L_Greybox_Arena01`、`L_MainMenu` |

---

## 4. 美术、材质、动画与音效前缀

| 前缀 | 资产类型 | 常用后缀约定 | 命名示例 |
| :--- | :--- | :--- | :--- |
| `SM_` | Static Mesh | 静态网格体（建筑、掩体、高台、道具） | `SM_Arena_HighPlatform_01`、`SM_Dice_Prop` |
| `SK_` | Skeletal Mesh | 带骨骼网格体（角色身体、机械义肢、枪械） | `SK_Dicebody_Base`、`SK_Pistol_Starter` |
| `PHYS_` | Physics Asset | 角色受击物理与**身体部位碰撞盒**配置 | `PHYS_Dicebody_Hitboxes` |
| `M_` | Material | 母材质（尽量少而精） | `M_Master_Opaque`、`M_UI_DurabilityBar` |
| `MI_` | Material Instance | 材质实例（日常调参数用它，别到处复制母材质） | `MI_Limb_DamagedState`、`MI_CaptureZone_TeamA` |
| `MF_` | Material Function | 材质函数 | `MF_HitFlash` |
| `T_` | Texture | `_D` 基础色 / `_N` 法线 / `_ORM` 粗糙金属AO打包图 / `_UI` 界面图标 | `T_Pistol_D`、`T_Pistol_N`、`T_Icon_ModuleJump_UI` |
| `A_` | AnimSequence | 单段骨骼动画 | `A_FP_Walk`、`A_FP_Slide_Loop` |
| `AM_` | AnimMontage | 动画蒙太奇（攀爬翻越、换弹、部位被打坏受击反馈） | `AM_Action_Vault`、`AM_Hit_LegBreak` |
| `BS_` | Blend Space | 混合空间（移动八方向混合） | `BS_TP_Locomotion` |
| `NS_` | Niagara System | UE5 Niagara 粒子系统 | `NS_Module_DestroySpark`、`NS_Point_PickupGlow` |
| `S_` / `MS_` | SoundWave / MetaSound | 原始音频文件用 `S_`，UE5 MetaSound 程序化音效用 `MS_` | `S_Footstep_Concrete_01`、`MS_Weapon_PistolFire` |

---

## 5. C++ 代码与 GameplayTag 约定（程序速查）

### C++ 类与变量前缀（遵循 Unreal Header Tool 强制规范）

- **`A`**：继承自 `AActor` 的类 → `ADicebodyCharacter`、`ACapturePointActor`
- **`U`**：继承自 `UObject` / `UActorComponent` 的类 → `UBodyPartSlotComponent`、`UDicebodyAbility`
- **`F`**：结构体（`USTRUCT` 或普通 C++ struct） → `FModuleCraftRecipeRow`、`FLimbDurabilityEntry`
- **`E`**：枚举（`UENUM`） → `EBodyPartType`、`EModuleTier`
- **`I`**：接口类 → `IDamageableBodyPartInterface`
- **`b`**：布尔变量 → `bIsModuleDisabled`、`bCanCraftInCombat`

> 代码排版不用手动数空格：仓库根目录已经配好了 `.clang-format` 和 `.editorconfig`（Allman 换行、Tab 缩进宽度 4、不乱动 `.generated.h` 顺序），IDE 保存自动格式化即可。

### Gameplay Tags 命名层级建议

GAS 里全靠 Tag 解耦状态，名字统一用英文点号分层，按「大类.子类.具体含义」来起，别混用大小写风格：

```text
Ability.Move.Sprint          # 能力标识：跑步
Ability.Move.Jump            # 能力标识：跳跃
Ability.Move.Climb           # 能力标识：攀爬
Ability.Move.Slide           # 能力标识：滑铲
BodySlot.Head                # 身体挂载部位：头
BodySlot.Torso               # 身体挂载部位：躯干
BodySlot.Arm.Left            # 身体挂载部位：左臂
BodySlot.Leg                 # 身体挂载部位：腿部
State.Module.Broken          # 状态：模块耐久归零失效
Event.Combat.LimbHit         # 游戏内事件：命中具体身体部位
```
