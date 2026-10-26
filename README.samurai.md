# Realme X2 Pro / samurai 用户态适配

从 [samurai/README.md](samurai/README.md) 开始。用户态 APKBUILD、补丁、服务脚本和设备配置的正式归属是本仓库的 `samurai-userspace` 分支。

仓库边界：

- 用户态：[`hmhmdcy/pmaports`](https://github.com/hmhmdcy/pmaports/tree/samurai-userspace)，保存 APKBUILD、补丁、OpenRC/udev/桌面配置和服务脚本。
- 内核态：[`hmhmdcy/linux`](https://github.com/hmhmdcy/linux/tree/samurai-ipe-variable-pd10-441)，保存 Linux 驱动、DTS 和后续相机分支。
- 快照与证据：[`hmhmdcy/edk2-realme-x2-pro`](https://github.com/hmhmdcy/edk2-realme-x2-pro)，保存 EDK2、发布索引、历史源码快照和验证记录，不替代上述两个正式源码仓库。

这是从 postmarketOS/Nura 的 GitLab pmaports 导入的个人适配分支；不是官方已合入的设备支持，也不是完整 rootfs 二进制备份。上游完整历史保留，基线为 `862c5af2ca9a48f43e934d9ea55fee0dd47a67f2`；`main` 保留该基线，设备改动位于设备分支。GitHub 没有 GitLab 项目的原生 fork 关系。

`samurai-userspace` 的前六个提交把工具链、相机、Turnip、radio/GNSS、平台/服务和文档按主题整理；后续提交继续加入 r33/r28 相机配置、52 个 libcamera 补丁、GeoClue/PipeWire 修复、传感器/桌面/USB 增量。不要把这个分支误读为固定只有六个提交。当前稳定候选为 libcamera `99990.7.2-r33`、camera config/stack `0.1.0-r28`、platform `5-r3`、desktop `3-r1`、GNSS `2-r1`、GeoClue `2.8.2-r1`、PipeWire `1.6.9-r3`；`r34/r29` 仅为未安装的离线候选。

长期维护：[跟随上游与补丁纯度](samurai/MAINTENANCE.md)。

入口：[最后实机状态](samurai/STATUS.md)、[源码与输入锁](samurai/sources.json)、[最后部署包清单](samurai/observed-packages-248.json)、[复现测试记录](samurai/REPRODUCIBILITY.md)。

本轮发布补充了公开源码检查和离线重放；r33/r28 的实机安装与精确回退证据来自既有 481/484/491 事务。发布动作没有刷写、重启或新增硬件验收，内核实验供电/OF 机制的正式化仍是纯净维护版的阻塞项。
