# 最后已验证的手机状态与新构建候选

基准：2026-10-17 的248只读 Linux 备份；全机功能验收沿用240，GNSS新增记录到247。用户随后计划自行刷Android，本页不能证明此刻物理手机运行哪个系统。249只做PC侧打包与复现，没有新刷写或新硬件验收。

| 部分 | 最后实测与限制 | 保存位置 |
| --- | --- | --- |
| 启动/屏幕 | EDK2 boot235 + Image183；白屏/花屏修复含UEFI与内核；Phosh启动约20.62秒 | EDK2164、内核153–165；用户态greetd顺序 |
| 触摸/USB | 既有原生桌面触摸和NCM/SSH通路；新镜像需新密钥/身份 | 内核及samurai-platform |
| GPU | 147内核GLES对齐；149 Turnip A640 VM_BIND 64KiB修复通过185个像素回读；240 Snapshot默认Vulkan仍GPU fault/device lost | 内核 + mesa-vulkan-freedreno-samurai；不能标为全部修好 |
| 音频 | 已有UCM/路由、扬声器/耳麦/采集修复；具体测试边界见166–184 | 内核 + samurai-platform |
| Wi-Fi/BT | Wi-Fi/chrony运行；同机DMS地址、RAM NV服务；BT已扫描/既有连接有观察，未新增配对/连接验收 | radio-tools/platform/openrc；固件为私人输入 |
| 传感器 | A.11 SLPI、wise_light兼容；accel/gyro/mag与SensorProxy出数；精度、动作/亮暗响应、旋转仍未完整验收；SLPI同boot重启生命周期仍未解决 | samurai-libssc/hexagonrpcd/ssc/openrc |
| 相机 | IMX471、IMX319与CAMSS/PMIC，libcamera r15/config r10；Snapshot仅该应用CPU路径两轮运行和清理通过 | 内核 + libcamera/config + desktop |
| 相机待办 | 未完成实屏画面/颜色验收；buffer回收告警仍在；其它后摄未适配，S5K3M5候选未部署 | 239–240原始记录 |
| 蜂窝 | 无SIM，未验语音/数据；MM状态−1/reason2/power1 | MM与radio配置；不是业务通过 |
| GNSS | 零CNR、无fix；1240份日志/2586个原始C/No全0；MEMSHARE等试验未证明根因；Android定位基线未知 | 241–247记录 + MM/gnss-assist；保持未解决 |

历史记录入口：[硬件状态](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/linux-port/docs/HARDWARE-STATUS.md)、[240](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel240)、[247](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel247)、[248](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel248)。

## 249候选与历史部署的明确差别

历史958包清单在 `observed-packages-248.json`。重建配方是新候选：libcamera r18/config r13使用同一功能补丁、默认新IPA密钥，下游改动合为6个最终功能补丁，移除实验追踪并修正配方校验顺序；Turnip有专用r2包；MM完整native重建为r4（含库），历史MM r1沿用r0库；服务文件改为有归属的包；私人固件来源改成统一路径；USB身份改为本安装生成。不得把候选APK的SHA或包版本当作历史实机SHA/版本。

读取现有只读备份时，扫描了958包元数据、所有 `/etc` 与 `/usr` 的包文件SHA1及未归属文件，发现140项与数据库校验和不同、6124项未归属文件。数量包含账户/生成缓存、旧模块树、手工重打包后的数据库差异，不等于140个硬件补丁。运行代码/服务/配置的相关项已整理到配方，私人账户/网络、旧诊断trace和构建缓存不导入新镜像。

## 维护纯度的尚未完成项

当前默认分支仍是复现用的 samurai-bringup，并未发布已验收的纯净维护内核。
它为保持最后部署配置，仍记录 IMX319 的 experimental_p_imx319_power 选项；
该配置依赖235/237 lab PMIC provider，不能当作已经完成的标准regulator驱动。
正式化和功能回归之前，不把它包装成“纯净修复”，也不通过直接删除使既有功能悄悄回退。
