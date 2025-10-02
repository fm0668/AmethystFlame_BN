#!/usr/bin/env python3
"""
AmethystFlame 统一策略启动器
支持根据配置文件启动不同的网格策略：
- 双向网格策略 (AmethystFlame_BN_Bidirectional.py)
- 做多网格策略 (AmethystFlame_BN_Long.py)
- 做空网格策略 (AmethystFlame_BN_Short.py)
"""

import json
import os
import sys
import asyncio
import logging
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/strategy_launcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('StrategyLauncher')

class StrategyLauncher:
    """统一策略启动器"""
    
    def __init__(self, config_file: str = "strategy_config.json"):
        self.config_file = config_file
        self.config = {}
        self.processes = {}
        self.running = True
        
        # 策略文件映射
        self.strategy_files = {
            "bidirectional": "AmethystFlame_BN_Bidirectional.py",
            "long": "AmethystFlame_BN_Long.py", 
            "short": "AmethystFlame_BN_Short.py"
        }
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self) -> bool:
        """加载策略配置"""
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"配置文件不存在: {self.config_file}")
                return False
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            logger.info(f"成功加载配置文件: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return False
    
    def validate_config(self) -> bool:
        """验证配置文件"""
        required_keys = ["enabled_strategies", "strategy_settings"]
        
        for key in required_keys:
            if key not in self.config:
                logger.error(f"配置文件缺少必需字段: {key}")
                return False
        
        # 验证启用的策略
        enabled = self.config["enabled_strategies"]
        for strategy in enabled:
            if strategy not in self.strategy_files:
                logger.error(f"未知的策略类型: {strategy}")
                return False
                
            strategy_file = self.strategy_files[strategy]
            if not os.path.exists(strategy_file):
                logger.error(f"策略文件不存在: {strategy_file}")
                return False
        
        return True
    
    def start_strategy(self, strategy_name: str) -> bool:
        """启动单个策略"""
        try:
            strategy_file = self.strategy_files[strategy_name]
            
            # 获取策略特定设置
            strategy_settings = self.config["strategy_settings"].get(strategy_name, {})
            
            # 构建启动命令
            cmd = [sys.executable, strategy_file]
            
            # 设置环境变量（如果有的话）
            env = os.environ.copy()
            if "env_vars" in strategy_settings:
                env.update(strategy_settings["env_vars"])
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=os.getcwd()
            )
            
            self.processes[strategy_name] = {
                "process": process,
                "start_time": time.time(),
                "restart_count": 0
            }
            
            logger.info(f"成功启动策略: {strategy_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"启动策略失败 {strategy_name}: {e}")
            return False
    
    def stop_strategy(self, strategy_name: str) -> bool:
        """停止单个策略"""
        try:
            if strategy_name not in self.processes:
                logger.warning(f"策略未运行: {strategy_name}")
                return True
            
            process_info = self.processes[strategy_name]
            process = process_info["process"]
            
            if process.poll() is None:  # 进程仍在运行
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"策略 {strategy_name} 未能正常结束，强制终止")
                    process.kill()
                    process.wait()
            
            del self.processes[strategy_name]
            logger.info(f"成功停止策略: {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"停止策略失败 {strategy_name}: {e}")
            return False
    
    def monitor_strategies(self):
        """监控策略运行状态"""
        while self.running:
            try:
                for strategy_name, process_info in list(self.processes.items()):
                    process = process_info["process"]
                    
                    # 检查进程状态
                    if process.poll() is not None:
                        # 进程已结束
                        exit_code = process.returncode
                        logger.warning(f"策略 {strategy_name} 意外退出 (退出码: {exit_code})")
                        
                        # 检查是否需要重启
                        strategy_settings = self.config["strategy_settings"].get(strategy_name, {})
                        auto_restart = strategy_settings.get("auto_restart", True)
                        max_restarts = strategy_settings.get("max_restarts", 5)
                        
                        if auto_restart and process_info["restart_count"] < max_restarts:
                            logger.info(f"正在重启策略: {strategy_name}")
                            del self.processes[strategy_name]
                            
                            if self.start_strategy(strategy_name):
                                self.processes[strategy_name]["restart_count"] = process_info["restart_count"] + 1
                        else:
                            logger.error(f"策略 {strategy_name} 达到最大重启次数或禁用自动重启")
                            del self.processes[strategy_name]
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                logger.error(f"监控策略时发生错误: {e}")
                time.sleep(5)
    
    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，正在关闭所有策略...")
        self.running = False
        self.stop_all_strategies()
        sys.exit(0)
    
    def stop_all_strategies(self):
        """停止所有策略"""
        logger.info("正在停止所有策略...")
        for strategy_name in list(self.processes.keys()):
            self.stop_strategy(strategy_name)
    
    def start_enabled_strategies(self):
        """启动所有启用的策略"""
        enabled_strategies = self.config["enabled_strategies"]
        
        logger.info(f"准备启动策略: {enabled_strategies}")
        
        for strategy in enabled_strategies:
            if self.start_strategy(strategy):
                logger.info(f"策略 {strategy} 启动成功")
            else:
                logger.error(f"策略 {strategy} 启动失败")
    
    def run(self):
        """主运行函数"""
        logger.info("AmethystFlame 统一策略启动器启动")
        
        # 加载和验证配置
        if not self.load_config():
            logger.error("配置加载失败，退出")
            return False
        
        if not self.validate_config():
            logger.error("配置验证失败，退出")
            return False
        
        # 确保日志目录存在
        os.makedirs("log", exist_ok=True)
        
        # 启动启用的策略
        self.start_enabled_strategies()
        
        if not self.processes:
            logger.warning("没有策略成功启动")
            return False
        
        # 开始监控
        logger.info("开始监控策略运行状态...")
        self.monitor_strategies()
        
        return True

def main():
    """主函数"""
    launcher = StrategyLauncher()
    try:
        launcher.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在退出...")
        launcher.stop_all_strategies()
    except Exception as e:
        logger.error(f"启动器运行时发生错误: {e}")
        launcher.stop_all_strategies()

if __name__ == "__main__":
    main()