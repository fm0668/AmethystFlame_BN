# AmethystFlame_BN 网格交易策略 VPS部署指南

## 系统要求

- **操作系统**: Ubuntu 22.04 LTS 或 CentOS 8+
- **CPU**: 2核心以上
- **内存**: 2GB RAM 以上
- **存储**: 20GB SSD 以上
- **网络**: 稳定的互联网连接
- **Python**: 3.8+ 版本

## 快速部署

### 1. 系统准备

```bash
# Ubuntu/Debian 系统
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip python3-venv screen htop

# CentOS/RHEL 系统
sudo yum update -y
sudo yum install -y git python3 python3-pip screen htop
```

### 2. 项目部署

```bash
# 克隆项目
cd ~
git clone https://github.com/fm0668/AmethystFlame_BN.git
cd AmethystFlame_BN

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. 配置环境

```bash
# 创建配置文件
vim .env
```

配置内容：
```bash
# Binance API配置
API_KEY=your_binance_api_key_here
API_SECRET=your_binance_secret_key_here
```

**重要配置说明：**
- 交易参数（币种、网格间距、杠杆等）在 `AmethystFlame_BN.py` 文件中配置
- 确保API密钥具有期货交易权限
- 建议使用子账户API，限制权限范围

### 4. 创建日志目录

```bash
# 创建日志目录
mkdir -p ~/AmethystFlame_BN/log
```

### 5. 生产环境部署（systemd服务）

创建系统服务：
```bash
sudo vim /etc/systemd/system/amethyst-flame-bn.service
```

服务配置：
```ini
[Unit]
Description=AmethystFlame BN Grid Trading Strategy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/AmethystFlame_BN
Environment=PATH=/root/AmethystFlame_BN/venv/bin
ExecStart=/root/AmethystFlame_BN/venv/bin/python AmethystFlame_BN.py
Restart=always
RestartSec=10
StandardOutput=append:/root/AmethystFlame_BN/log/systemd.log
StandardError=append:/root/AmethystFlame_BN/log/systemd_error.log

[Install]
WantedBy=multi-user.target
```

**操作步骤：**
1. 复制上述配置内容
2. 在vim编辑器中按 `i` 进入插入模式
3. 粘贴配置内容
4. 按 `Esc` 退出插入模式
5. 输入 `:wq` 保存并退出
6. 按 `Enter` 确认

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable amethyst-flame-bn.service
```

## 常用命令汇总

### 启动脚本
```bash
# 启动网格交易服务
sudo systemctl start amethyst-flame-bn.service

# 查看启动状态
sudo systemctl status amethyst-flame-bn.service

# 查看服务日志（实时）
sudo journalctl -u amethyst-flame-bn.service -f

# 查看最近100行日志
sudo journalctl -u amethyst-flame-bn.service -n 100
```

### 停止脚本
```bash
# 停止网格交易服务
sudo systemctl stop amethyst-flame-bn.service

# 紧急停止（直接终止进程）
pkill -f "python.*AmethystFlame_BN.py"
```

### 重启服务
```bash
# 重启网格交易服务
sudo systemctl restart amethyst-flame-bn.service

# 重新加载配置
sudo systemctl daemon-reload
sudo systemctl restart amethyst-flame-bn.service
```

### 查看日志

```bash
# 查看系统服务日志（实时）
sudo journalctl -u amethyst-flame-bn.service -f

# 查看应用日志（实时）
tail -f ~/AmethystFlame_BN/log/AmethystFlame_BN.log

# 查看系统日志
tail -f ~/AmethystFlame_BN/log/systemd.log

# 查看错误日志
tail -f ~/AmethystFlame_BN/log/systemd_error.log
```

### 更新策略

```bash
# 停止当前运行的服务
sudo systemctl stop amethyst-flame-bn.service

# 进入项目目录
cd ~/AmethystFlame_BN

# 备份当前配置
cp .env .env.backup

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖包
pip install -r requirements.txt

# 恢复配置文件
cp .env.backup .env

# 重启服务
sudo systemctl start amethyst-flame-bn.service
```

### 系统监控
```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看网络连接
netstat -tulpn | grep python

# 查看服务状态
sudo systemctl status amethyst-flame-bn.service
```

## 手动运行和测试

### 测试运行
```bash
# 进入项目目录
cd ~/AmethystFlame_BN
source venv/bin/activate

# 手动运行（测试模式）
python AmethystFlame_BN.py
```

### Screen 会话运行
```bash
# 创建新的screen会话
screen -S amethyst-flame

# 在screen中运行
cd ~/AmethystFlame_BN
source venv/bin/activate
python AmethystFlame_BN.py

# 分离会话（Ctrl+A, 然后按D）
# 重新连接会话
screen -r amethyst-flame

# 查看所有会话
screen -ls
```

## 维护任务

### 日志管理
```bash
# 查看日志文件大小
du -sh ~/AmethystFlame_BN/log/*

# 清理大日志文件（保留最近1000行）
tail -n 1000 ~/AmethystFlame_BN/log/AmethystFlame_BN.log > /tmp/temp.log
mv /tmp/temp.log ~/AmethystFlame_BN/log/AmethystFlame_BN.log

# 删除旧的系统日志
sudo journalctl --vacuum-time=7d
```

### 代码更新
```bash
# 停止服务
sudo systemctl stop amethyst-flame-bn.service

# 备份配置
cd ~/AmethystFlame_BN
cp .env .env.backup

# 更新代码
git stash  # 暂存本地修改
git pull origin main
git stash pop  # 恢复本地修改

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl start amethyst-flame-bn.service
```

### 配置备份
```bash
# 创建配置备份
cd ~/AmethystFlame_BN
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env AmethystFlame_BN.py

# 恢复配置
tar -xzf config_backup_YYYYMMDD.tar.gz
```

## 故障排除

### 常见问题

1. **服务无法启动**
   ```bash
   # 查看详细错误
   sudo journalctl -u amethyst-flame-bn.service --no-pager -n 50
   
   # 检查配置文件
   cat ~/AmethystFlame_BN/.env
   
   # 检查Python环境
   cd ~/AmethystFlame_BN
   source venv/bin/activate
   python -c "import ccxt, websockets; print('Dependencies OK')"
   ```

2. **API连接失败**
   - 检查API密钥是否正确
   - 确认网络连接正常：`ping api.binance.com`
   - 验证API权限设置（需要期货交易权限）
   - 检查IP白名单设置

3. **WebSocket连接问题**
   ```bash
   # 测试网络连接
   telnet fstream.binance.com 443
   
   # 检查防火墙设置
   sudo ufw status
   ```

4. **内存不足**
   ```bash
   # 创建交换文件
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # 永久启用
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

5. **磁盘空间不足**
   ```bash
   # 清理系统缓存
   sudo apt clean
   sudo apt autoremove
   
   # 清理日志
   sudo journalctl --vacuum-size=100M
   ```

### 紧急处理
```bash
# 立即停止所有交易
sudo systemctl stop amethyst-flame-bn.service
pkill -f "python.*AmethystFlame_BN.py"

# 检查是否还有Python进程
ps aux | grep AmethystFlame_BN
```

### 性能优化
```bash
# 调整系统参数
echo 'net.core.rmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 设置进程优先级
sudo systemctl edit amethyst-flame-bn.service
# 添加：
# [Service]
# Nice=-10
```

## 安全建议

### API安全
- 使用子账户API密钥，限制权限范围
- API密钥只开启期货交易权限，禁用提现
- 设置IP白名单，限制访问来源
- 定期轮换API密钥

### 系统安全
- 定期更新系统和依赖包
- 配置防火墙，只开放必要端口
- 使用SSH密钥认证，禁用密码登录
- 定期备份配置和日志

### 风险管理
- 设置合理的仓位和止损限制
- 监控账户余额和持仓状态
- 定期检查交易记录
- 设置资金使用上限

## 监控和告警

### 基础监控脚本
```bash
# 创建监控脚本
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
SERVICE="amethyst-flame-bn.service"
if ! systemctl is-active --quiet $SERVICE; then
    echo "$(date): Service $SERVICE is not running!" >> ~/monitor.log
    # 可以添加邮件或短信告警
fi
EOF

chmod +x ~/monitor.sh

# 添加到crontab（每5分钟检查一次）
echo "*/5 * * * * /root/monitor.sh" | crontab -
```

---

**免责声明**: 本软件仅供学习研究使用，交易有风险，投资需谨慎。使用本软件进行实盘交易的所有风险由用户自行承担。