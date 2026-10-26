# 外置启动链的复现边界

这是公开仓库审查得到的事实，不把“有源码归档”写成“一条命令可完整复现”。

最后检查点 248 使用 EDK2 boot235、Image183 和 237 核对的模块集（775 个 ko/789 项清单）。后续 r33/r28 用户态事务记录在 481/484/491，不改变这个外置内核/模块边界。

内核正式归属是 `hmhmdcy/linux`。`samurai-bringup` 保存早期完整 bring-up 源码 `04d4d4f93171574201db1837a1b195e3aeccde4e`；相机后续依次发布为 `samurai-camera-common`、`samurai-vfe175-gtm-reopen434`、`samurai-ipe-variable-pd10-441`。最新分支仍未把 235/237 的实验 OF/供电机制完全收敛为标准驱动，因此只克隆该分支、执行普通 defconfig 并 make，仍不能宣称得到最后手机上的全部模块。

## 查找准确来源

- [Linux 早期完整 bring-up](https://github.com/hmhmdcy/linux/tree/samurai-bringup)：设备驱动/板源历史基线。
- [Linux 当前相机队列](https://github.com/hmhmdcy/linux/tree/samurai-ipe-variable-pd10-441)：在 common-driver、VFE175/GTM 和 IPE PD10 分支之后的当前端点；仍不是已纯化的统一发布内核。
- [Linux移植导航](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/linux-port/README.md)：源码、历史配置、启动链文档与会话入口。
- [183记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel183)：Image183的构建和验证背景。
- [235记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel235)：IMX319、PMIC源码、Kconfig/Makefile片段、板源准备及构建脚本。
- [237记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel237)：最后模块安装、清单与验收。
- [240交接](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/reference/kernel240/HANDOFF.md)：最后相机/用户态部署与回退。
- [248记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel248)：个人完整备份和PC恢复核验；原始镜像与私人身份数据未公开。

历史脚本中有固定的本地工作路径、独立SDK和一次性部署前提，不能直接当作通用安装脚本执行。
用户态 APKBUILD 和补丁已归入 `hmhmdcy/pmaports`；EDK2 的 `linux-port/packages` 只是公开快照和证据。内核晚期相机仍需同样的正式化处理。

## 完整源码复现仍缺少的闭环

1. 收敛 235/237 的最终相机驱动与供电资源，去掉不再需要的 OF fixture/overlay，在正确的内核仓库建立可维护的功能队列。
2. 提供与该队列匹配、无私人路径的统一内核配置片段；从同一构建产出Image、DTB和全部模块。
3. 参数化外置initramfs/rootfs绑定与EDK2打包，使用本次安装的F2FS UUID、个人SSH密钥及明确固件输入。
4. 做新镜像的启动和逐项硬件回归，记录精确提交/配置/文件hash，再发布不可变的验收标签。

这些是当前完整复现测试的剩余限制，不能省略成一句“按Linux README编译即可”。
已有个人248完整备份可以承担逐字节回退；公开源码重建生成的新密钥和新镜像不承诺与该备份逐字节一致。
