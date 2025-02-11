# GitHub520 Hosts 加速工具

一个用于加速访问 GitHub 的小工具，通过更新 hosts 文件来实现。

## 功能特点

- 自动更新 hosts 配置
- 一键刷新 DNS 缓存
- 查看当前 hosts 内容
- 手动编辑 hosts 文件
- 快速打开 hosts 文件目录

## 使用方法

### 直接使用

1. 在 `dist` 目录下找到 `GitHub520加速工具.exe`
2. 双击运行（需要管理员权限）
3. 按照菜单提示进行操作

### 从源码运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 运行程序：

```bash
python update_hosts.py
```

### 打包程序

如果需要重新打包程序：

```bash
python -m PyInstaller github520.spec
```

## 项目文件说明

- `update_hosts.py`: 主程序源代码
- `github520.spec`: PyInstaller 打包配置文件
- `requirements.txt`: 项目依赖列表
- `README.md`: 项目说明文档

## 注意事项

- 运行程序需要管理员权限（因为需要修改 hosts 文件）
- 建议定期更新 hosts 配置
- 更新后需要刷新 DNS 缓存才能生效

## 鸣谢

感谢 [GitHub520](https://github.com/521xueweihan/GitHub520) 项目提供的 hosts 数据源。
