# 🎯 学生打卡系统

一个简单的网页打卡系统，支持IP限制防止代签行为。

## ✨ 功能特点

- 📱 响应式设计，支持手机和电脑访问
- 🔒 IP地址限制，每台设备只能签到一次
- 📊 实时显示已签到和未签到同学名单
- 📈 出勤率统计
- 💾 数据持久化存储
- 🛡️ 防重复签到

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python app.py
```

### 3. 访问系统

打开浏览器访问：http://localhost:5000

## 📋 使用说明

### 学生端使用

1. 在输入框中输入自己的姓名
2. 点击"打卡签到"按钮
3. 系统会显示签到成功或失败信息

### 注意事项

- 只能输入预设的学生名单中的姓名
- 每个IP地址只能签到一次，防止代签
- 已经签到的同学不能重复签到

### 管理员功能

系统提供以下管理员API（需要添加管理员验证）：

- `POST /api/admin/reset` - 重置所有签到数据
- `GET /api/admin/export` - 导出签到数据

## 🛠️ 技术栈

- **前端**: HTML5, CSS3, JavaScript
- **后端**: Python Flask
- **数据存储**: JSON文件
- **跨域处理**: Flask-CORS

## 📁 文件结构

```
student-checkin-system/
├── index.html              # 主页面文件
├── app.py                  # Flask后端服务器
├── requirements.txt        # Python依赖
├── checkin_data.json       # 签到数据文件（自动生成）
├── ip_records.json         # IP记录文件（自动生成）
└── README.md              # 说明文档
```

## 🔧 配置说明

### 修改学生名单

在 `app.py` 文件中修改 `STUDENT_LIST` 变量：

```python
STUDENT_LIST = [
    '张三', '李四', '王五', # ... 你的学生名单
]
```

### 修改端口

在 `app.py` 文件中修改最后一行的端口号：

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🚨 安全提醒

- 当前版本的管理员功能没有身份验证，生产环境请添加管理员验证
- IP限制可以通过代理绕过，如需更严格的安全措施，请考虑其他验证方式
- 建议定期备份数据文件

## 📞 技术支持

如遇到问题，请检查：

1. Python环境是否正确安装
2. 依赖包是否全部安装成功
3. 端口是否被占用
4. 防火墙是否阻止了访问

## 📄 许可证

MIT License - 可自由使用和修改