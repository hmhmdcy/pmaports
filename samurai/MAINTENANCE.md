# 跟随上游与补丁纯度

维护单位是 **上游源码 + 最小功能补丁 + 包配方 + 设备配置**；rootfs 是这些输入的构建结果，不是在 Git 中维护的大镜像。测试日志、临时镜像、抓包、私有固件、NV、旧 SDK 和失败方案只留在历史归档，不进入设备 APK 或功能补丁队列。

## 两类版本必须分清

- 已验收版本：固定内核/DTB/模块与用户态版本，并保留不可移动的发布标签和个人回退备份。
- 上游更新候选：在新分支上推进上游，重放设备补丁，通过构建/离线检查后，再做实机验收。构建成功不能自动晋升为已验收版本。

`main` 在首次导入时保存上游基线；`samurai-userspace` 的前六个提交按工具链、相机、Turnip、radio/GNSS、平台/服务和文档整理，之后继续以独立主题提交记录 r33/r28、GeoClue/PipeWire 与验证修正。`samurai-bringup` 保留历史。记录的旧基线不能静默变化。每次更新创建新候选分支，更新 `sources.json` 中的基线，审阅 `git range-diff`；上游已有等价修复就删除本地补丁，不通过重复应用维持它。共享已验收分支不进行强制推送。

例如在干净 checkout 中更新 pmaports（把示例日期、ref替换为实际目标）：

```sh
git remote add upstream https://gitlab.postmarketos.org/postmarketOS/pmaports.git
git fetch upstream main
git switch -c update/pmaports-YYYYMMDD samurai-userspace
git rebase --onto upstream/main 862c5af2ca9a48f43e934d9ea55fee0dd47a67f2
# 有冲突即停下逐项解决，不使用 ours/theirs 批量覆盖。
# 更新 sources.json 的基线后，在新的 work 目录执行 bootstrap.py 和离线检查。
```

fork 中的 `temp/libcamera`、`temp/modemmanager` 要同时比较对应 Alpine/Nura 上游配方；Mesa 只覆盖 Turnip，保留发行版其它 Mesa 包。版本/ABI变化时连同依赖、子包和校验和更新。不要仅替换 .so 而沿用旧 APK 版本号；不要长期使用 `apk upgrade` 留着无归属的手工文件。每个源码补丁都需说明问题、最终行为、依赖与测试边界。

## 内核仓库与当前边界

内核态补丁的正式归属是 [`hmhmdcy/linux`](https://github.com/hmhmdcy/linux)，不是 pmaports 或 EDK2。当前公开分支：

| 分支 | 提交 | 作用 |
| --- | --- | --- |
| `samurai-bringup` | `04d4d4f93171574201db1837a1b195e3aeccde4e` | 早期完整 camera/PMIC bring-up 历史 |
| `samurai-camera-common` | `1f5da50bbcba4fbe89917db7987429fdf078f257` | 3 个提交；改用 common driver、静态 DT 描述，并移除旧 bring-up helper 的一部分 |
| `samurai-vfe175-gtm-reopen434` | `9bc07e6339128ae8d3525c7d5c9bca5d0fbc46f3` | 在 camera-common 后 116 个提交、109 个文件；VFE175/GTM/LTM/PD10 相机处理 |
| `samurai-ipe-variable-pd10-441` | `5b0e7a9ac5b311a4c4fe17cf48b7ed4fc9a7b91d` | 在 434 后 4 个提交、4 个文件（+176/−59）；variable-size PD10、无 SOF 和无 auxiliary restart 诊断 |

GitHub compare 当前报告 `samurai-bringup...samurai-ipe-variable-pd10-441` 为 123 个提交、125 个文件、+19,968/−480。该数字只是发布端点差异，不是硬件通过数量，也不是“已纯化”的证明。分支仍继承实验 OF fixture、前摄 overlay、专用 trace 和 235/237 lab PMIC 机制；不能只构建最新板级 DTS 就宣称复现最后手机状态。

后续应在内核仓库按 DTS、显示、GPU、音频、无线、传感器和相机功能继续拆提交，把电源/复位/共享资源收敛到正常驱动与静态 DT；随后移除临时模块、overlay 和对应 Kconfig/Makefile 引用。日志与失败实验保留在 bring-up 归档。切换到某个 LTS 是单独的移植和验收，不能假定 7.3-rc6 补丁可直接套用。

## 更新的验收门槛

源码：补丁能零fuzz应用、无失败/过渡代码、无个人路径/密钥；正常驱动检查及DT校验通过。

构建：内核Image/DTB和全部模块来自同一配置/提交；APK签名、子包求解、固件输入manifest、离线根目录通过；保存本次精确版本清单。

实机：启动/屏幕/触摸、GLES与Vulkan既有回归、USB/Wi-Fi/BT、音频、传感器和已支持相机逐项验收。GNSS零CNR、其它后摄和未验蜂窝业务继续明确标记未解决。更新工具和CI不自行刷机，也不把构建绿灯解释为硬件验收。

优先将通用修复送对应上游并移除下游副本。Linux stable要求修复先进入主线，流程见 [kernel stable规则](https://docs.kernel.org/process/stable-kernel-rules.html)；设备新支持不等于可直接投递stable补丁。

## 纯净补丁的实际边界

功能补丁保留最终实现：一个提交解决一个问题，说明硬件约束、必要依赖和验证范围。修正提交应折叠进原功能提交；不把“先加错误实现、后面再撤销”作为长期队列。正常错误处理和上游风格的debug接口可以保留；每帧实验日志、硬编码试验路径、运行时OF补节点、探测用驱动、抓包和生成二进制不进入维护队列。回归测试源码另放测试目录，构建输出只作为CI产物。

目前可以确认：`temp/libcamera` 固定 52 个补丁队列（6 个发行版补丁和 46 个项目补丁），零 fuzz 重放后的整棵源码树与 `libcamera-source-lock.json` 一致。补丁数目只是可复现输入，不能推断每个 hunk 都已达到上游可接受形式。camera YAML 只承载本机 profile；个体系数、出厂表、照片和原始日志不进入公开仓库。

## 接下来如何整理内核

先从固定基线另建候选，保留 `samurai-bringup` 不动；不要在已部署分支直接删除文件或强推。对照最终 235/237 的源码和 DTS，将相机电源、复位和共享资源表达成正常的驱动与静态板级描述，再从新候选移除以下实验机制：

| 机制 | 源码位置 | 维护候选应采用的形式 |
|---|---|---|
| 动态补PMIC/CCI节点 | drivers/of/samurai-pmic-fixture.c、samurai-cci-bringup.c | 静态DTS、正常provider探测及deferred probe |
| 动态前摄overlay及探针 | drivers/of/samurai-front-overlay.c、samurai-front-identify.c | 静态endpoint、时钟/电源/复位、正常sensor驱动 |
| 临时phandle修补 | drivers/of/samurai-vio-phandle.c | DTS中的真实supply引用 |
| 专用过程trace | include/trace/events/samurai_diag.h及调用点 | 移出功能队列；必要诊断单独审阅 |
| 实验PMIC开关与复位模块 | 235/237归档及samurai-pmic-bringup.conf | 正式regulator/reset驱动及共享消费者生命周期 |

这张表是已核实的待清理清单，不能代替其余修改逐hunk审查。显示、GPU、音频和FastRPC提交中也混有诊断改动，应分别拆出最终功能差异。清理后必须重新构建并完成断电启动、相机开关/失败回收、共享电源与DSP重启回归，不能只看diff变小。

## 用户态更新和设备安装是两条流水线

上游pmaports/Alpine更新先进入新候选；单独推进libcamera、Mesa、ModemManager等源码版本并重算校验和、增加pkgrel，避免把多个ABI升级混成一次无法定位的变更。重新生成APK、签名索引、离线rootfs和精确包清单。设备本地修复仓库的优先级/版本应显式设置；仅运行apk upgrade不会自动编译GitHub源码，也不会更新外置EDK2/内核/模块。

在离线候选先检查 apk 升级模拟、包归属与服务配置。OpenRC 附加设置保留上游原配置；升级产生的 `.apk-new` 需审阅，设备片段变化需重新运行 finalize 并处理差异，不能覆盖用户设置。实机通过后才发布不可移动的版本标签、构建输入清单和匹配产物，并保留上一版完整回退。当前 r33/r28 有既有 481/484 安装与回退证据，但本次仓库发布没有新的刷写或硬件验收，也未配置自动刷写或无人值守内核升级。

`samurai-userspace` 保留最初的 6 个主题提交，并用后续独立提交记录 r33/r28、GeoClue/PipeWire、GNSS 电源策略、传感器/桌面/USB 修正和发布文档。这样既保留可审阅的主题历史，也避免改写已经推送的远端。提交历史整理、CI 通过和离线构建都不等于实验相机供电已正式化或硬件验收完成。
