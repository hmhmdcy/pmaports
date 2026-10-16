# 跟随上游与补丁纯度

维护单位是 **上游源码 + 最小功能补丁 + 包配方 + 设备配置**；rootfs 是这些输入的构建结果，不是在 Git 中维护的大镜像。测试日志、临时镜像、抓包、私有固件、NV、旧 SDK 和失败方案只留在历史归档，不进入设备 APK 或功能补丁队列。

## 两类版本必须分清

- 已验收版本：固定内核/DTB/模块与用户态版本，并保留不可移动的发布标签和个人回退备份。
- 上游更新候选：在新分支上推进上游，重放设备补丁，通过构建/离线检查后，再做实机验收。构建成功不能自动晋升为已验收版本。

`main` 在首次导入时保存上游基线；`samurai-bringup` 是当前适配候选。记录的旧基线不能静默变化。每次更新创建新候选分支，更新 `sources.json` 中的基线，审阅 `git range-diff`；上游已有等价修复就删除本地补丁，不通过重复应用维持它。共享已验收分支不进行强制推送。

例如在干净 checkout 中更新 pmaports（把示例日期、ref替换为实际目标）：

```sh
git remote add upstream https://gitlab.postmarketos.org/postmarketOS/pmaports.git
git fetch upstream main
git switch -c update/pmaports-YYYYMMDD samurai-bringup
git rebase --onto upstream/main 862c5af2ca9a48f43e934d9ea55fee0dd47a67f2
# 有冲突即停下逐项解决，不使用 ours/theirs 批量覆盖。
# 更新 sources.json 的基线后，在新的 work 目录执行 bootstrap.py 和离线检查。
```

fork 中的 `temp/libcamera`、`temp/modemmanager` 要同时比较对应 Alpine/Nura 上游配方；Mesa 只覆盖 Turnip，保留发行版其它 Mesa 包。版本/ABI变化时连同依赖、子包和校验和更新。不要仅替换 .so 而沿用旧 APK 版本号；不要长期使用 `apk upgrade` 留着无归属的手工文件。每个源码补丁都需说明问题、最终行为、依赖与测试边界。

## 内核当前尚不能直接作为纯净更新队列

公开内核分支最后核对为 `04d4d4f93171574201db1837a1b195e3aeccde4e`，基线是 `a90ee4305`（Linux7.3-rc6）；相对基线120个文件、11020行新增/881行删除。这些数值是源码审查结果，不是硬件通过数量。

其中仍含 `drivers/of/samurai-*-fixture`、front identify/overlay、专用诊断 trace；最后IMX319部署还使用235/237的lab PMIC/运行时资源方案，不能只构建当前fork的板级DTS便宣称复现最后手机相机状态。应先把稳定的电源/资源关系收敛为正常驱动、regulator和静态DTS，再把临时模块及对应Kconfig/Makefile引用从维护队列移除。未完成的后摄与GNSS试验不能混作正式修复。

内核后续采用独立的维护候选分支，按 DTS、显示、GPU、音频、无线、传感器、相机等功能拆提交；日志/实验保留在原bring-up归档。先沿已验证的上游系列推进并测试；切换到某个LTS系列是单独的移植和验收，不能认为7.3-rc6补丁能直接套到旧LTS。**此处明确记录内核清理未完成，不把现有120文件差异冒称已纯化。**

## 更新的验收门槛

源码：补丁能零fuzz应用、无失败/过渡代码、无个人路径/密钥；正常驱动检查及DT校验通过。

构建：内核Image/DTB和全部模块来自同一配置/提交；APK签名、子包求解、固件输入manifest、离线根目录通过；保存本次精确版本清单。

实机：启动/屏幕/触摸、GLES与Vulkan既有回归、USB/Wi-Fi/BT、音频、传感器和已支持相机逐项验收。GNSS零CNR、其它后摄和未验蜂窝业务继续明确标记未解决。更新工具和CI不自行刷机，也不把构建绿灯解释为硬件验收。

优先将通用修复送对应上游并移除下游副本。Linux stable要求修复先进入主线，流程见 [kernel stable规则](https://docs.kernel.org/process/stable-kernel-rules.html)；设备新支持不等于可直接投递stable补丁。

## 纯净补丁的实际边界

功能补丁保留最终实现：一个提交解决一个问题，说明硬件约束、必要依赖和验证范围。修正提交应折叠进原功能提交；不把“先加错误实现、后面再撤销”作为长期队列。正常错误处理和上游风格的debug接口可以保留；每帧实验日志、硬编码试验路径、运行时OF补节点、探测用驱动、抓包和生成二进制不进入维护队列。回归测试源码另放测试目录，构建输出只作为CI产物。

目前可以确认：libcamera已将16个下游过程补丁收敛成6个最终功能补丁，保留原有6个发行版补丁，独立重放后源码一致。不能由此推断其它全部补丁或内核已清理完成。当前原生APK配方仍明确保留历史IMX319供电兼容配置，以便复现最后部署；它与235/237的内核lab实现一起，是纯净维护版本的阻塞项。

## 接下来如何整理内核

先从固定基线另建候选，保留原samurai-bringup不动；不要在已部署分支直接删除文件或强推。对照最终235/237的源码和DTS，将相机电源、复位和共享资源表达成正常的驱动与静态板级描述，然后再移除以下实验机制：

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

在离线候选先检查apk升级模拟、包归属与服务配置。OpenRC附加设置保留上游原配置；升级产生的.apk-new需审阅，设备片段变化需重新运行finalize并处理差异，不能覆盖用户设置。实机通过后才发布不可移动的版本标签、构建输入清单和匹配产物；保留上一版完整回退。当前尚未发布经过新实机验收的249版本，也未配置自动刷写或无人值守内核升级。
