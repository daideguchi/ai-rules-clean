# 📊 Performance Monitoring (perf) - 完全解説

## "perf" とは何か

**Performance Monitoring** = 継続的なシステム性能監視

### 3層監視アーキテクチャ

#### 1. アプリケーション層
```
📊 Application Metrics
├── 応答時間 (Latency)
│   ├── p50: 50%のリクエストの応答時間
│   ├── p95: 95%のリクエストの応答時間
│   └── p99: 99%のリクエストの応答時間
├── スループット (Throughput)
│   ├── リクエスト/秒 (RPS)
│   ├── タスク完了率
│   └── 並行処理数
└── エラー率 (Error Rate)
    ├── 4xx エラー率
    ├── 5xx エラー率
    └── タイムアウト率
```

#### 2. システム層
```
🖥️ System Metrics
├── CPU使用率
│   ├── 全体使用率
│   ├── コア別使用率
│   └── アイドル時間
├── メモリ使用量
│   ├── 物理メモリ
│   ├── スワップ使用量
│   └── キャッシュ使用量
├── ディスクI/O
│   ├── 読み取り速度
│   ├── 書き込み速度
│   └── IOPS
└── ネットワーク
    ├── 帯域幅使用率
    ├── 接続数
    └── パケット損失率
```

#### 3. AI特化層
```
🤖 AI-Specific Metrics
├── GPU使用率
│   ├── GPU使用率 (%)
│   ├── VRAMメモリ使用量
│   └── GPU温度
├── 推論性能
│   ├── Token/秒
│   ├── 推論レイテンシ
│   └── バッチ処理効率
├── モデル性能
│   ├── コンテキスト使用率
│   ├── キャッシュヒット率
│   └── 精度ドリフト
└── AI Worker状態
    ├── アクティブWorker数
    ├── 待機中Worker数
    └── エラー状態Worker数
```

## 実装詳細

### 1. メトリクス収集
```python
# monitoring/metrics_collector.py
import time
import psutil
import GPUtil
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    gpu_usage: float
    gpu_memory: float
    active_workers: int
    completed_tasks: int
    error_rate: float

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.task_count = 0
        self.error_count = 0
    
    def collect_system_metrics(self) -> PerformanceMetrics:
        """システムメトリクスを収集"""
        
        # CPU・メモリ
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU (利用可能な場合)
        gpu_usage = 0
        gpu_memory = 0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
                gpu_memory = gpus[0].memoryUtil * 100
        except:
            pass
        
        # AI Worker状態
        active_workers = self.count_active_workers()
        
        # エラー率計算
        error_rate = (self.error_count / max(self.task_count, 1)) * 100
        
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_usage=disk.percent,
            gpu_usage=gpu_usage,
            gpu_memory=gpu_memory,
            active_workers=active_workers,
            completed_tasks=self.task_count,
            error_rate=error_rate
        )
    
    def count_active_workers(self) -> int:
        """アクティブなAI Worker数を取得"""
        # 実際の実装では、AI Organization Systemと連携
        return 8  # 8 AI workers
```

### 2. リアルタイム表示
```python
# monitoring/live_dashboard.py
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import time

class LivePerformanceDashboard:
    def __init__(self):
        self.console = Console()
        self.collector = MetricsCollector()
    
    def create_metrics_table(self, metrics: PerformanceMetrics) -> Table:
        """メトリクステーブル作成"""
        table = Table(title="📊 Performance Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")
        
        # CPU
        cpu_status = "🟢 Normal" if metrics.cpu_percent < 70 else "🟡 Warning" if metrics.cpu_percent < 90 else "🔴 Critical"
        table.add_row("CPU Usage", f"{metrics.cpu_percent:.1f}%", cpu_status)
        
        # Memory
        mem_status = "🟢 Normal" if metrics.memory_percent < 70 else "🟡 Warning" if metrics.memory_percent < 90 else "🔴 Critical"
        table.add_row("Memory Usage", f"{metrics.memory_percent:.1f}%", mem_status)
        
        # GPU
        if metrics.gpu_usage > 0:
            gpu_status = "🟢 Normal" if metrics.gpu_usage < 80 else "🟡 Warning" if metrics.gpu_usage < 95 else "🔴 Critical"
            table.add_row("GPU Usage", f"{metrics.gpu_usage:.1f}%", gpu_status)
            table.add_row("GPU Memory", f"{metrics.gpu_memory:.1f}%", gpu_status)
        
        # AI Workers
        worker_status = "🟢 Active" if metrics.active_workers >= 6 else "🟡 Degraded" if metrics.active_workers >= 4 else "🔴 Critical"
        table.add_row("Active Workers", f"{metrics.active_workers}/8", worker_status)
        
        # Error Rate
        error_status = "🟢 Normal" if metrics.error_rate < 5 else "🟡 Warning" if metrics.error_rate < 15 else "🔴 Critical"
        table.add_row("Error Rate", f"{metrics.error_rate:.1f}%", error_status)
        
        return table
    
    def create_worker_status_panel(self) -> Panel:
        """Worker状態パネル"""
        worker_info = """
🤖 AI Workers Status:
├── 👑 PRESIDENT: ACTIVE (CPU: 45%, Tasks: 12)
├── 🔄 COORDINATOR: PROCESSING (CPU: 38%, Tasks: 8)
├── 📋 ANALYST: ACTIVE (CPU: 52%, Tasks: 15)
├── 🏗️ ARCHITECT: IDLE (CPU: 12%, Tasks: 3)
├── 📊 DATA_ENG: PROCESSING (CPU: 78%, Tasks: 20)
├── 🔒 SECURITY: ACTIVE (CPU: 34%, Tasks: 6)
├── 📈 PM: IDLE (CPU: 8%, Tasks: 2)
└── ⚙️ DEVOPS: ACTIVE (CPU: 41%, Tasks: 10)
        """
        return Panel(worker_info, title="AI Organization Status")
    
    def run_live_dashboard(self):
        """ライブダッシュボード実行"""
        def generate_display():
            while True:
                metrics = self.collector.collect_system_metrics()
                
                # レイアウト作成
                layout = Layout()
                layout.split_column(
                    Layout(name="metrics", size=12),
                    Layout(name="workers")
                )
                
                layout["metrics"].update(self.create_metrics_table(metrics))
                layout["workers"].update(self.create_worker_status_panel())
                
                yield layout
                time.sleep(2)  # 2秒更新
        
        with Live(generate_display(), console=self.console, refresh_per_second=0.5):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
```

### 3. アラート・通知
```python
# monitoring/alerting.py
from dataclasses import dataclass
from enum import Enum
from typing import List, Callable

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    level: AlertLevel
    message: str
    metric_name: str
    current_value: float
    threshold: float
    timestamp: float

class AlertManager:
    def __init__(self):
        self.alert_rules = []
        self.alert_handlers = []
    
    def add_rule(self, metric_name: str, threshold: float, level: AlertLevel, message: str):
        """アラートルール追加"""
        self.alert_rules.append({
            'metric_name': metric_name,
            'threshold': threshold,
            'level': level,
            'message': message
        })
    
    def add_handler(self, handler: Callable[[Alert], None]):
        """アラートハンドラー追加"""
        self.alert_handlers.append(handler)
    
    def check_alerts(self, metrics: PerformanceMetrics):
        """アラートチェック"""
        metric_values = {
            'cpu_percent': metrics.cpu_percent,
            'memory_percent': metrics.memory_percent,
            'gpu_usage': metrics.gpu_usage,
            'error_rate': metrics.error_rate
        }
        
        for rule in self.alert_rules:
            current_value = metric_values.get(rule['metric_name'])
            if current_value and current_value > rule['threshold']:
                alert = Alert(
                    level=rule['level'],
                    message=rule['message'],
                    metric_name=rule['metric_name'],
                    current_value=current_value,
                    threshold=rule['threshold'],
                    timestamp=time.time()
                )
                
                # アラート送信
                for handler in self.alert_handlers:
                    handler(alert)

# アラート設定例
alert_manager = AlertManager()
alert_manager.add_rule('cpu_percent', 80.0, AlertLevel.WARNING, "CPU使用率が高くなっています")
alert_manager.add_rule('cpu_percent', 95.0, AlertLevel.CRITICAL, "CPU使用率が危険レベルです")
alert_manager.add_rule('memory_percent', 85.0, AlertLevel.WARNING, "メモリ使用率が高くなっています")
alert_manager.add_rule('error_rate', 10.0, AlertLevel.CRITICAL, "エラー率が許容範囲を超えています")
```

## 使用方法

### 1. 基本的な監視
```bash
# パフォーマンス監視開始
python3 monitoring/live_dashboard.py

# メトリクス収集のみ
python3 monitoring/metrics_collector.py --collect-only

# アラート設定
python3 monitoring/alerting.py --config alerts.json
```

### 2. 統合ダッシュボード
```bash
# AI Organization + Performance 統合表示
python3 src/ui/ai_org_ui.py --mode dashboard --with-perf

# パフォーマンス専用
python3 src/ui/ai_org_ui.py --mode perf
```

## 結論

**"perf" = 継続的なシステム性能監視**

1. **3層監視**: アプリケーション・システム・AI特化
2. **リアルタイム表示**: 2秒間隔更新
3. **アラート機能**: 閾値ベースの自動通知
4. **統合ダッシュボード**: AI Organization + Performance
5. **24/7運用**: 継続的な監視・改善

**常に動いているシステムパフォーマンス監視です。**