# Realme X2 Pro / samurai 用户态适配

从 [samurai/README.md](samurai/README.md) 开始。推荐设备分支：samurai-userspace；按6个主题提交最终用户态差异。samurai-bringup保留历史整理过程。

这是从 postmarketOS/Nura 的 GitLab pmaports 导入的个人适配分支；不是官方已合入的设备支持，也不是完整 rootfs 二进制备份。上游完整历史保留，基线为 `862c5af2ca9a48f43e934d9ea55fee0dd47a67f2`；`main` 保留该基线，设备改动位于设备分支。GitHub 没有 GitLab 项目的原生 fork 关系。

长期维护：[跟随上游与补丁纯度](samurai/MAINTENANCE.md)。

入口：[最后实机状态](samurai/STATUS.md)、[源码与输入锁](samurai/sources.json)、[最后部署包清单](samurai/observed-packages-248.json)、[复现测试记录](samurai/REPRODUCIBILITY.md)。

当前属于离线构建候选；内核lab相机供电依赖仍是纯净维护版的阻塞项。没有发布新的实机验收版本。
