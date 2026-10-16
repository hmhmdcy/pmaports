# 独立复现核验

2026-10-17：本轮PC离线核验完成。结论：公开源码可重建用户态APK并组装候选rootfs；自备同机私有输入后可完成离线配置和完整性核验。**尚不能仅凭GitHub一键重建最后实机的完整启动链，也不能据此宣称纯净维护内核或硬件重新验收通过。**

## 方法与结果

从GitHub另建新clone，使用bootstrap从公开镜像取得锁定pmbootstrap提交及已公开的kernel=none功能补丁。源码、配方、运行程序均未复制旧私有SDK；私有输入只在固件整理阶段显式读取248的PC只读备份，未连接或刷写手机。第一次安装发现的包归属问题已修正，使用空根目录重新安装；外置内核的工具修正公开后完成账号配置。过程日志和失败产物仅留私人构建目录。

| 检查 | 最终结果与范围 |
|---|---|
| 源完整性 | 14配方、88个本地SHA512、102个生产源码文件、1个工具补丁SHA256通过 |
| libcamera队列 | 原发行版6补丁＋最终下游6补丁；零fuzz重放，21个改动文件锁一致；独立净源码比较1490文件一致 |
| ARM64构建 | 13个目标配方及完整libcamera/MM子包成功；crossdirect另在主机架构构建 |
| ModemManager | 38项测试全部通过；不是蜂窝业务验收 |
| RAM服务回归 | COW、sharedmem边界、当前TFTP tmpfs工作文件、扩展RPC registry四项通过ASan/UBSan；已知上游builder进程寿命分配不做leak验收 |
| 根目录安装 | 882包；finalize重复执行通过；未生成可独立启动的手机镜像 |
| 包与加载检查 | 189个包文件校验、78个ARM64 ELF、服务路径/依赖/用户覆盖；Python GI-QMI加载通过 |
| 命令冒烟 | ModemManager版本、使用设备SSC库的ssccli帮助、GNSS辅助程序帮助均返回0；未开QMI定位会话或启动硬件服务 |
| 同机自备输入 | 301个SSC文件及160个firmware条目的SHA256 manifest逐项通过；备份保持只读 |
| APK更新链 | 34个本候选APK组成的签名仓库验证通过；拒绝同名多版本混杂索引，未复制私钥；自带公钥及samurai来源标签 |
| 升级求解 | 刷新发行版与本地签名索引后apk upgrade --simulate返回0，未求解出替换设备包或其它升级；仅表示本次索引可解 |
| 维护纯度门槛 | --require-maintenance-clean按预期拒绝实验IMX319供电配置；没有把阻塞标为通过 |

libcamera与Turnip此处验证的是编译、补丁与安装完整性；配方未执行硬件单元测试，PC也不能替代摄像头/GPU实机测试。新版发行版包会继续变化，后续更新仍需重新构建和验收。

## 本轮用户态版本

| 包 | 候选版本 |
|---|---|
| device-realme-samurai | 2-r0 |
| device-realme-samurai-kernel-none | 2-r0 |
| samurai-camera-config | 0.1.0-r13 |
| samurai-camera-stack | 0.1.0-r13 |
| libcamera | 99990.7.2-r18 |
| libcamera-ipa | 99990.7.2-r18 |
| libcamera-tools | 99990.7.2-r18 |
| libcamera-gstreamer | 99990.7.2-r18 |
| libcamera-v4l2 | 99990.7.2-r18 |
| mesa-vulkan-freedreno-samurai | 26.2.4-r2 |
| modemmanager | 1.25.95_git20261005-r4 |
| libmm-glib | 1.25.95_git20261005-r4 |
| samurai-libssc | 1-r0 |
| samurai-hexagonrpcd | 1-r0 |
| samurai-radio-tools | 1-r0 |
| samurai-platform | 5-r0 |
| samurai-gnss-assist | 2-r0 |
| samurai-ssc | 1-r0 |
| samurai-openrc | 3-r0 |
| samurai-desktop | 3-r0 |

APK配方最终代码在公开提交6c2540fe4已具备，仓库导出保护在5cd7b3a2d验证；后续samurai-userspace将相同最终差异整理为6个主题提交，原分支与其历史保留。新分支源码检查由GitHub Actions单独运行。新IPA/APK密钥、本轮依赖版本及构建时间不同，不承诺与248历史APK逐字节相同。

## 无法由本轮证明的事项

- 882包是新候选；248备份958包包含其它软件与历史版本，未宣称完整逐包重装成历史镜像。
- 所有上游源码有固定版本/提交与校验和，但Alpine/Nura APK依赖仓库是滚动的；历史清单不是冻结二进制镜像。
- 固件、校准、NV、凭据和分区身份必须自备；公开仓库不提供私人内容。完整逐字节回退仍依赖个人248备份。
- 最后boot235/Image183/237模块的构建和相机lab PMIC/provider尚未合为一个干净、自动可复建的维护内核；参见[启动链来源](BOOT-PROVENANCE.md)与[清理清单](MAINTENANCE.md)。
- GNSS零CNR、Snapshot默认Vulkan故障、相机显示/颜色及其它后摄等限制保持[原状态](STATUS.md)。物理手机当前系统未知，本轮没有刷写或新实机验收。
