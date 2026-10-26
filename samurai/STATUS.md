# 最后已验证状态与当前发布候选

文档核对：2026-10-26。硬件基线沿用 2026-10-17 的 248 只读备份、240 全机验收和 2026-10-24 的 484 相机包事务；用户随后继续使用手机做其它工作，本页不能证明此刻物理手机运行哪个系统。本次只做仓库整理、源码检查和离线重放，没有刷写、重启或新增硬件验收。

| 部分 | 最后实测与限制 | 保存位置 |
| --- | --- | --- |
| 启动/屏幕 | EDK2 boot235 + Image183；白屏/花屏修复含 UEFI 与内核；Phosh 启动约 20.62 秒 | EDK2 164、内核 153–165；用户态 greetd 顺序 |
| 触摸/USB | 既有原生桌面触摸和 NCM/SSH 通路；新镜像需新密钥/身份；本轮把 gadget `MaxPower` 提高到 500 并要求重新绑定后再启用 | 内核 + samurai-platform |
| GPU | 147 内核 GLES 对齐；149 Turnip A640 VM_BIND 64 KiB 修复通过 185 个像素回读；240 Snapshot 默认 Vulkan 仍有 GPU fault/device lost | 内核 + mesa-vulkan-freedreno-samurai；不能标为全部修好 |
| 音频 | 已有 UCM/路由、扬声器/耳麦/采集修复；本轮增加 PulseAudio Bluetooth 依赖并继续保留既有路由 | 内核 + samurai-platform |
| Wi-Fi/BT | Wi-Fi/chrony 运行；同机 DMS 地址、RAM NV 服务；BT 已扫描/既有连接有观察，未新增配对/连接验收 | radio-tools/platform/openrc；固件为私人输入 |
| 传感器 | A.11 SLPI、wise_light 兼容；accel/gyro/mag 与 SensorProxy 出数；本轮移除旧 PMIC lab modprobe，加入 SensorProxy 加速度方向 udev 规则；精度、动作/亮暗响应、旋转仍未完整验收 | samurai-libssc/hexagonrpcd/ssc/openrc/platform |
| 相机 | 481/484 已原生安装 libcamera r33/config r28，精确回退到 r32/r27 后再次升级到 r33/r28；两次 forward 共 14 个默认路径用例通过 | 内核相机分支 + libcamera/config + desktop |
| 相机待办 | r34/r29 七包仅离线签名和模拟求解，禁止写成当前版本；实屏色彩、共享 Manager 重开/long-run、编码录像/HDR、多摄同步及第五摄仍未闭环 | 490/491 记录；r33/r28 为当前稳定候选 |
| 蜂窝 | 无 SIM，未验语音/数据；MM 状态 −1/reason2/power1 | MM 与 radio 配置；不是业务通过 |
| GNSS | 零 CNR、无 fix；1240 份日志/2586 个原始 C/No 全 0；GeoClue 生命周期和 no-SIM 电源策略已有更新，但 MEMSHARE 等试验未证明根因 | GeoClue、MM、gnss-assist；保持未解决 |

历史记录入口：[硬件状态](https://github.com/hmhmdcy/realme-x2-pro-edk2/blob/master/Platform/Realme/sm8150/linux-port/docs/HARDWARE-STATUS.md)、[240](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel240)、[247](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel247)、[248](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel248)、[481](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel481)、[484](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel484)、[491](https://github.com/hmhmdcy/realme-x2-pro-edk2/tree/master/Platform/Realme/sm8150/reference/kernel491)。

## 当前用户态候选

该分支的正式源码归属是 [`hmhmdcy/realme-x2-pro-pmaports`](https://github.com/hmhmdcy/realme-x2-pro-pmaports/tree/samurai-userspace)；内核源码归属是 [`hmhmdcy/realme-x2-pro-linux`](https://github.com/hmhmdcy/realme-x2-pro-linux/tree/samurai-ipe-variable-pd10-441)。EDK2 只保存快照、历史和证据，不是内核或 APKBUILD 的最终仓库。

当前仓库固定：

- libcamera / IPA / tools / GStreamer / V4L2：`99990.7.2-r33`
- samurai-camera-config / samurai-camera-stack：`0.1.0-r28`
- samurai-platform：`5-r3`；samurai-desktop：`3-r1`；samurai-gnss-assist：`2-r1`
- GeoClue：`2.8.2-r1`；PipeWire：`1.6.9-r3`（含 `gst-plugin-pipewire` 子包）
- ModemManager / libmm-glib：`1.25.95_git20261005-r4`；Mesa Turnip：`26.2.4-r2`

libcamera 队列共 52 个补丁，零 fuzz 重放后的源码树 SHA256 为 `ae7785b15bc1c9d7434e0804961a0a6713f737beade9668630b8541680587307`。r33/r28 的历史实机事务、精确回退和最终保留见 484 独立审计；本轮只重新验证源码和配方，没有再次安装。

## 与历史 249 候选的差别

历史 958 包清单在 `observed-packages-248.json`。早期 249 候选使用 libcamera r18/config r13、12 个相机补丁；当前候选已更新为 r33/r28、52 个补丁、GeoClue/PipeWire 修复和正常传感器 udev 规则。不得把当前 APK 的 SHA 或包版本当作 248 历史实机版本，也不得把 r34/r29 的离线候选当成已部署版本。

本轮公开验证确认：16 个配方、149 个本地 SHA512、168 个源码文件、1 个工具补丁、52 个 libcamera 补丁和 GNSS 14 个电源策略场景通过；这些检查没有连接手机。现有 r33/r28 硬件证据见 484，当前分支的完整 rootfs 重建和新硬件验收尚未在本轮执行。详见[复现记录](REPRODUCIBILITY.md)。

## 尚未完成的维护纯度

内核侧已有更清晰的相机分支，但从 `samurai-bringup` 到最新 `samurai-ipe-variable-pd10-441` 的累计差异仍很大，包含实验 OF fixture、前摄 overlay、专用 trace 和 lab PMIC 历史。分支推送和源码可构建不等于这些机制已转成上游可接受的标准驱动。必须先收敛电源/复位/共享资源、拆分诊断改动并完成断电/相机开关/DSP 重启回归，才能发布纯净维护内核。
