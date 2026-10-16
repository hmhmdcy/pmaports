# 外置启动链的复现边界

这是公开仓库审查得到的事实，不把“有源码归档”写成“一条命令可完整复现”。

最后检查点248使用 EDK2 boot235、Image183 和237核对的模块集（775个ko/789项清单）。
Linux仓库04d4d4f保存的是已整理的主树源码；晚期相机模块还有235/237单独准备和部署的来源。
因此，只克隆Linux分支、执行普通defconfig并make，不能宣称得到最后手机上的全部模块。

## 查找准确来源

- [Linux主树](https://github.com/hmhmdcy/linux/tree/samurai-bringup)：设备驱动/板源。根README是上游通用说明，没有本设备的完整统一构建配方。
- [Linux移植导航](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/linux-port/README.md)：源码、历史配置、启动链文档与会话入口。
- [183记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel183)：Image183的构建和验证背景。
- [235记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel235)：IMX319、PMIC源码、Kconfig/Makefile片段、板源准备及构建脚本。
- [237记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel237)：最后模块安装、清单与验收。
- [240交接](https://github.com/hmhmdcy/edk2-realme-x2-pro/blob/master/Platform/Realme/sm8150/reference/kernel240/HANDOFF.md)：最后相机/用户态部署与回退。
- [248记录](https://github.com/hmhmdcy/edk2-realme-x2-pro/tree/master/Platform/Realme/sm8150/reference/kernel248)：个人完整备份和PC恢复核验；原始镜像与私人身份数据未公开。

历史脚本中有固定的本地工作路径、独立SDK和一次性部署前提，不能直接当作通用安装脚本执行。
本仓库已将用户态部分替换为原生APKBUILD和参数化的离线整理入口；内核晚期相机仍需同样的正式化处理。

## 完整源码复现仍缺少的闭环

1. 收敛235/237的最终相机驱动与供电资源，去掉不再需要的OF fixture/overlay，建立可维护的内核功能队列。
2. 提供与该队列匹配、无私人路径的统一内核配置片段；从同一构建产出Image、DTB和全部模块。
3. 参数化外置initramfs/rootfs绑定与EDK2打包，使用本次安装的F2FS UUID、个人SSH密钥及明确固件输入。
4. 做新镜像的启动和逐项硬件回归，记录精确提交/配置/文件hash，再发布不可变的验收标签。

这些是当前完整复现测试的剩余限制，不能省略成一句“按Linux README编译即可”。
已有个人248完整备份可以承担逐字节回退；公开源码重建生成的新密钥和新镜像不承诺与该备份逐字节一致。
