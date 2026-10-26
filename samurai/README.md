# Realme X2 Pro rootfs 重建

本仓库是用户态 APKBUILD、补丁、服务和设备配置的正式归属。内核源码在 [`hmhmdcy/linux`](https://github.com/hmhmdcy/linux/tree/samurai-ipe-variable-pd10-441)，EDK2、DTB、历史快照和发布证据在 [`hmhmdcy/edk2-realme-x2-pro`](https://github.com/hmhmdcy/edk2-realme-x2-pro)。先读 [STATUS.md](STATUS.md)，不要把构建成功等同于所有硬件通过。

推荐 `samurai-userspace`：前六个提交按主题整理工具链、相机、Turnip、radio/GNSS、平台和文档，之后继续记录 r33/r28、GeoClue/PipeWire 及验证修正；原 `samurai-bringup` 保留历史。当前候选固定 libcamera `99990.7.2-r33`、config/stack `0.1.0-r28`、platform `5-r3`、desktop `3-r1`、GNSS `2-r1`、GeoClue `2.8.2-r1` 和 PipeWire `1.6.9-r3`。`r34/r29` 没有安装证据，不是稳定发布。**IMX319 的内核实验供电/OF 依赖尚未正式化，整机纯净维护版本未发布。**

## 环境与隔离构建

需要 Linux x86_64 或 ARM64、Python 3.12以上、Git、sudo/挂载权限、约 25 GiB 可用的 ext4 工作空间。WSL2 可以使用，但 work 目录必须在 Linux 文件系统，不能放在 `/mnt/c`、`/mnt/e` 等 NTFS 挂载上。需联网获取 APK 和已锁定的源码。构建期间保持 WSL 实例运行。

```sh
git clone --branch samurai-userspace https://github.com/hmhmdcy/pmaports.git
cd pmaports
python3 samurai/bootstrap.py --work "$HOME/samurai-build" --build --lax --jobs 4
```

脚本从公开镜像取得并验证 pmbootstrap `200f5123615808326ac796f66b02fdc6cebbcbf1`，官方来源仍为 GitLab。随后应用 sources.json 锁定的一个功能补丁：选择 `kernel=none` 时跳过无内核可用的 initramfs 生成；不替换 mkinitfs 程序，也不生成占位内核。它先构建修正过的 crossdirect，再构建 15 个目标软件包及依赖，其中明确包含 GeoClue 和 PipeWire，确保本地 GNSS/相机缓冲补丁实际参与构建。`--lax` 只是在这次全新工作区内复用 chroot；不读取原手机 SDK。省略它可为每个包重建 chroot。失败后修正/更新源码，再使用同一参数加 `--resume`。不要运行 `pmbootstrap pull`，否则会推进上游基线。

配方中的本地补丁有 SHA512，工具补丁有独立 SHA256；外部源码有固定版本/提交及 SHA512。构建会生成自己的 APK 签名密钥和 libcamera IPA 密钥，不需要项目作者的私钥。结果不承诺与历史 APK 逐字节相同。APK 仓库仍是滚动的 edge；[958 包清单](observed-packages-248.json)记录历史版本，但不是永久可用的二进制镜像。

## 生成离线根目录

成功构建后运行以下命令。变量替换为本次实际路径；普通用户运行无需 `--as-root`，直接以 root 运行则保留它。

```sh
python3 "$HOME/samurai-build/pmbootstrap/pmbootstrap.py" --as-root -y -j 4 \
  -c "$HOME/samurai-build/pmbootstrap.cfg" install --no-image --no-recommends
sudo python3 samurai/export-apk-repository.py \
  --root "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" \
  --packages "$HOME/samurai-build/work/packages/edge"
sudo chroot "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" \
  apk --no-network add device-realme-samurai@samurai samurai-camera-stack@samurai \
  libcamera@samurai libcamera-ipa@samurai libcamera-tools@samurai \
  libcamera-gstreamer@samurai libcamera-v4l2@samurai \
  modemmanager@samurai libmm-glib@samurai geoclue@samurai pipewire@samurai \
  gst-plugin-pipewire@samurai mesa-vulkan-freedreno-samurai@samurai
sudo python3 samurai/finalize-rootfs.py \
  --root "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" --user user
```

交互式设置本次安装密码；不要输入要复用的重要密码。自动测试使用临时随机密码，最终锁定该账号且不发布密码。部署前设置个人密码/SSH 公钥，并确认新生成的 SSH 主机密钥。finalize 配置启动依赖、Phosh 和用户级 Snapshot 覆盖；不会打开手机或格式化分区。默认配置自动登录该用户，与最后部署行为一致。

## 专有固件和本机数据

只有公开 GitHub 仓库不能产生这部分数据。必须提供自己的同机型/同手机输入，禁止用外机 NV 或校准代替。输入文件仅复制到离线候选根目录：

```sh
sudo python3 samurai/provision-firmware.py \
  --root /absolute/path/to/candidate-root \
  --firmware /private/own/lib/firmware \
  --slpi-firmware /private/own/A.11-slpi \
  --ssc-source /private/own/sensor-sources \
  --mag-config /private/own/magnetometer-escaped.json \
  --modem-type /private/own/modemType \
  --radio-manifest /private/own/modem-sha256.txt
```

firmware 是完整的本机固件树，包含 ADSP、GPU、Wi-Fi、BT 文件。slpi-firmware 单独提供自己的 A.11 `slpi.mdt` 及完整分片；安装时规范化到 `qcom/sm8150/realme/samurai-slpi-a11/`。sensor-sources 包含 `sdsp/`、`sensors-vendor/config/`、`sensors-vendor/sns_reg_config`、`sensors-persist/registry/`。modemType 预期为 4。磁力计转义修正及固件出处见 [113](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel113) 和 [186–187](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel187)。脚本验证已知配置 SHA；不同固件不能直接跳过检查。

已有本机 Linux 只读备份可提供这些输入；`/etc/samurai-ssc.json` 标识原始来源位置，`/etc/samurai-wifi/modem-sha256.txt` 提供 radio manifest。新候选统一存放在 `/var/lib/samurai/firmware/`，不会依赖历史 `kNNN` 工作目录。也可从自己的合法固件包/只读备份整理输入，但该提取过程及许可需自行确认。

无线电启动时严格核对本机分区名、扇区数和已验证的 256 GB UFS 型号，modem 分区只读，NV 分区只读复制到 RAM。RMTFS 写入只在 RAM COW，TFTP 工作文件在有限额 tmpfs。128 GB 或其他 UFS 型号不在当前验证范围，脚本将拒绝启动；不得简单删除核对条件。

## boot、模块与部署边界

本设备包选择 `kernel=none`、`flash_method=none`。它不产生可独立启动的手机镜像。最后实机是 EDK2 boot235 + Image183，另有已核对的 775 个模块；不是安装一个通用上游内核就能恢复。屏幕修复还依赖 UEFI164 和内核 DSI/DPU153–165，GLES 依赖147内核地址对齐，不能只恢复用户态。

外置启动链的来源与尚未闭环的步骤见 [BOOT-PROVENANCE.md](BOOT-PROVENANCE.md)，回退另见 [240 交接](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/reference/kernel240/HANDOFF.md)。历史 rootfs handoff 的 PARTUUID/F2FS UUID 是私人部署参数，新文件系统必须重新生成绑定，不能复制旧 UUID 或凭 `uname -r` 认定模块匹配。完整逐字节回退仍使用个人248离线备份。

本流程没有刷写命令。产物须先完成离线检查，再经过设备身份、备份和模块匹配核对，才进入单独的部署/实机验收步骤。

## 可单独运行的公开源码检查

以下检查各使用一个新目录；只下载已锁定的公开源码，不连接手机：

```sh
python3 samurai/check-sources.py
python3 samurai/verify-camera-series.py --work "$HOME/samurai-camera-replay"
python3 samurai/test-ram-services.py --work "$HOME/samurai-ram-tests"
```

离线根目录还需执行以下检查；不会启动硬件服务：

```sh
sudo python3 samurai/check-rootfs.py \
  --root "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" \
  --packages "$HOME/samurai-build/work/packages/edge" --user user
sudo chroot "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" apk update
sudo chroot "$HOME/samurai-build/work/chroot_rootfs_realme-samurai" apk upgrade --simulate
```

`check-rootfs --require-maintenance-clean` 会拒绝 rootfs 中仍残留的 lab 供电配置。本轮已移除旧的 `samurai-pmic-bringup.conf`，但内核源码里实验 OF/供电机制是否清理仍需单独审查；rootfs 检查通过不能代替内核纯度检查。

后两项另需主机的 patch 和 C 编译器（支持ASan/UBSan），以及可用的 /dev/shm tmpfs。
RAM/RPC检查保留上游builder已知的进程寿命分配，不把关闭leak检查解释为内存泄漏已修复。
这些是长期回归测试源码；生成的二进制、日志、抓包和SDK不进入Git。

## 软件包更新

export脚本把本次构建的已签名索引、索引内APK和既有公钥信任保存在候选自身，配置带samurai标签的本地仓库；不复制私钥，不自动修改world。官方发行版仓库继续用于普通软件。导出会拒绝同名多版本混杂的索引；发布仓库应只含本候选版本，不直接复制反复试验的包缓存。部署自己的远程修复仓库时用HTTPS发布APK、同一签名索引及公钥，私钥留在构建机。

维护者先构建新的候选并验收，用户再更新修复仓库；GitHub源仓库本身不是apk仓库。对libcamera、libmm-glib、modemmanager和设备包使用对应samurai仓库标签，避免发行版新版本无意替换设备修复。标签限制来源，不永久锁死版本；以后发布该仓库的新版本仍可更新。新的索引和APK必须同时更新，不能仅复制so。

本轮源码、补丁和离线验证结果见 [REPRODUCIBILITY.md](REPRODUCIBILITY.md)。r33/r28 的既有实机安装及精确回退记录在 EDK2 481/484/491 证据中，本次发布没有新的刷写或硬件验收。内核和模块属于外置启动链，不能通过当前设备 APK 自动升级。
