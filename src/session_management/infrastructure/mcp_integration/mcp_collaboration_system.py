"""
MCP Collaboration System
Model Context Protocol統合・AI協業システム
"""

import json
import uuid
import asyncio
import aiohttp
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import threading
import logging
from pathlib import Path


class MCPMessageType(Enum):
    """MCPメッセージ種別"""
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"


class AIModel(Enum):
    """AIモデル種別"""
    CLAUDE = "CLAUDE"
    O3 = "O3"
    GEMINI = "GEMINI"
    GPT4 = "GPT4"


class CollaborationRole(Enum):
    """協業役割"""
    COORDINATOR = "COORDINATOR"     # 調整者（Claude）
    ANALYZER = "ANALYZER"          # 分析者（o3）
    REVIEWER = "REVIEWER"          # レビュー者（Gemini）
    EXECUTOR = "EXECUTOR"          # 実行者（Claude）


class TaskPriority(Enum):
    """タスク優先度"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class MCPMessage:
    """MCPメッセージ"""
    message_id: str
    message_type: MCPMessageType
    sender: AIModel
    recipient: Optional[AIModel]
    content: Dict[str, Any]
    timestamp: datetime
    conversation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender": self.sender.value,
            "recipient": self.recipient.value if self.recipient else None,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "reply_to": self.reply_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """辞書から復元"""
        return cls(
            message_id=data["message_id"],
            message_type=MCPMessageType(data["message_type"]),
            sender=AIModel(data["sender"]),
            recipient=AIModel(data["recipient"]) if data.get("recipient") else None,
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            conversation_id=data.get("conversation_id"),
            reply_to=data.get("reply_to")
        )


@dataclass
class CollaborationTask:
    """協業タスク"""
    task_id: str
    title: str
    description: str
    priority: TaskPriority
    assigned_models: List[AIModel]
    coordinator: AIModel
    created_at: datetime
    deadline: Optional[datetime] = None
    status: str = "PENDING"
    progress: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    conversation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "assigned_models": [model.value for model in self.assigned_models],
            "coordinator": self.coordinator.value,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "status": self.status,
            "progress": self.progress,
            "context": self.context,
            "results": self.results,
            "conversation_id": self.conversation_id
        }


@dataclass
class AIModelEndpoint:
    """AIモデルエンドポイント"""
    model: AIModel
    endpoint_url: str
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（APIキー除外）"""
        return {
            "model": self.model.value,
            "endpoint_url": self.endpoint_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "is_active": self.is_active
        }


class MCPClient:
    """MCPクライアント"""
    
    def __init__(self, model: AIModel, logger: Optional[logging.Logger] = None):
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.endpoints: Dict[AIModel, AIModelEndpoint] = {}
        self.message_handlers: List[Callable[[MCPMessage], None]] = []
        self.conversation_history: Dict[str, List[MCPMessage]] = {}
        self._lock = threading.Lock()
    
    def add_endpoint(self, endpoint: AIModelEndpoint) -> None:
        """エンドポイント追加"""
        self.endpoints[endpoint.model] = endpoint
        self.logger.info(f"Added endpoint for {endpoint.model.value}")
    
    def add_message_handler(self, handler: Callable[[MCPMessage], None]) -> None:
        """メッセージハンドラー追加"""
        self.message_handlers.append(handler)
    
    async def send_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """メッセージ送信"""
        if not message.recipient or message.recipient not in self.endpoints:
            self.logger.error(f"No endpoint for recipient: {message.recipient}")
            return None
        
        endpoint = self.endpoints[message.recipient]
        if not endpoint.is_active:
            self.logger.warning(f"Endpoint inactive: {endpoint.model.value}")
            return None
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # メッセージ送信
            async with self.session.post(
                endpoint.endpoint_url,
                json=message.to_dict(),
                headers=self._build_headers(endpoint),
                timeout=aiohttp.ClientTimeout(total=endpoint.timeout)
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    
                    # レスポンスメッセージ作成
                    response_message = MCPMessage(
                        message_id=str(uuid.uuid4()),
                        message_type=MCPMessageType.RESPONSE,
                        sender=message.recipient,
                        recipient=message.sender,
                        content=response_data,
                        timestamp=datetime.now(),
                        conversation_id=message.conversation_id,
                        reply_to=message.message_id
                    )
                    
                    # 会話履歴に追加
                    self._add_to_conversation_history(message)
                    self._add_to_conversation_history(response_message)
                    
                    self.logger.info(f"Message sent successfully to {message.recipient.value}")
                    return response_message
                else:
                    self.logger.error(f"Failed to send message: HTTP {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout sending message to {message.recipient.value}")
            return None
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None
    
    def _build_headers(self, endpoint: AIModelEndpoint) -> Dict[str, str]:
        """ヘッダー構築"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"MCP-Client/{self.model.value}"
        }
        
        if endpoint.api_key:
            headers["Authorization"] = f"Bearer {endpoint.api_key}"
        
        headers.update(endpoint.headers)
        return headers
    
    def _add_to_conversation_history(self, message: MCPMessage) -> None:
        """会話履歴に追加"""
        if not message.conversation_id:
            return
        
        with self._lock:
            if message.conversation_id not in self.conversation_history:
                self.conversation_history[message.conversation_id] = []
            
            self.conversation_history[message.conversation_id].append(message)
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[MCPMessage]:
        """会話履歴取得"""
        with self._lock:
            history = self.conversation_history.get(conversation_id, [])
            return history[-limit:]
    
    async def close(self) -> None:
        """クライアント終了"""
        if self.session:
            await self.session.close()
            self.session = None


class CollaborationOrchestrator:
    """協業オーケストレーター"""
    
    def __init__(self, mcp_client: MCPClient, logger: Optional[logging.Logger] = None):
        self.mcp_client = mcp_client
        self.logger = logger or logging.getLogger(__name__)
        
        # タスク管理
        self.active_tasks: Dict[str, CollaborationTask] = {}
        self.task_results: Dict[str, Dict[str, Any]] = {}
        
        # 協業パターン
        self.collaboration_patterns = {
            "analysis_review": {
                "roles": [CollaborationRole.ANALYZER, CollaborationRole.REVIEWER],
                "models": [AIModel.O3, AIModel.GEMINI],
                "coordinator": AIModel.CLAUDE
            },
            "code_review": {
                "roles": [CollaborationRole.ANALYZER, CollaborationRole.REVIEWER, CollaborationRole.EXECUTOR],
                "models": [AIModel.O3, AIModel.GEMINI, AIModel.CLAUDE],
                "coordinator": AIModel.CLAUDE
            },
            "problem_solving": {
                "roles": [CollaborationRole.ANALYZER, CollaborationRole.REVIEWER],
                "models": [AIModel.O3, AIModel.GEMINI],
                "coordinator": AIModel.CLAUDE
            }
        }
        
        self._lock = threading.Lock()
    
    def create_collaboration_task(self, title: str, description: str, 
                                pattern: str = "analysis_review",
                                priority: TaskPriority = TaskPriority.MEDIUM,
                                context: Optional[Dict[str, Any]] = None) -> CollaborationTask:
        """協業タスク作成"""
        
        if pattern not in self.collaboration_patterns:
            raise ValueError(f"Unknown collaboration pattern: {pattern}")
        
        pattern_config = self.collaboration_patterns[pattern]
        
        task = CollaborationTask(
            task_id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            assigned_models=pattern_config["models"],
            coordinator=pattern_config["coordinator"],
            created_at=datetime.now(),
            context=context or {},
            conversation_id=str(uuid.uuid4())
        )
        
        with self._lock:
            self.active_tasks[task.task_id] = task
        
        self.logger.info(f"Created collaboration task: {task.title}")
        return task
    
    async def execute_collaboration_task(self, task_id: str) -> Dict[str, Any]:
        """協業タスク実行"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.active_tasks[task_id]
        
        try:
            task.status = "RUNNING"
            
            # 各モデルにタスクを送信
            model_responses = {}
            
            for model in task.assigned_models:
                if model == self.mcp_client.model:
                    continue  # 自分自身には送信しない
                
                # タスクメッセージ作成
                message = MCPMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=MCPMessageType.REQUEST,
                    sender=self.mcp_client.model,
                    recipient=model,
                    content={
                        "task_id": task.task_id,
                        "type": "collaboration_request",
                        "title": task.title,
                        "description": task.description,
                        "context": task.context,
                        "role": self._get_model_role(model, task)
                    },
                    timestamp=datetime.now(),
                    conversation_id=task.conversation_id
                )
                
                # メッセージ送信
                response = await self.mcp_client.send_message(message)
                if response:
                    model_responses[model.value] = response.content
                    task.progress += 1.0 / len(task.assigned_models)
            
            # 結果統合
            integrated_result = self._integrate_model_responses(model_responses, task)
            
            # タスク完了
            task.status = "COMPLETED"
            task.progress = 1.0
            task.results = integrated_result
            
            with self._lock:
                self.task_results[task_id] = integrated_result
            
            self.logger.info(f"Collaboration task completed: {task.title}")
            return integrated_result
            
        except Exception as e:
            task.status = "FAILED"
            task.results = {"error": str(e)}
            self.logger.error(f"Collaboration task failed: {e}")
            raise
    
    def _get_model_role(self, model: AIModel, task: CollaborationTask) -> str:
        """モデルの役割取得"""
        role_mapping = {
            AIModel.O3: CollaborationRole.ANALYZER,
            AIModel.GEMINI: CollaborationRole.REVIEWER,
            AIModel.CLAUDE: CollaborationRole.COORDINATOR
        }
        
        return role_mapping.get(model, CollaborationRole.EXECUTOR).value
    
    def _integrate_model_responses(self, responses: Dict[str, Any], task: CollaborationTask) -> Dict[str, Any]:
        """モデル応答統合"""
        integrated = {
            "task_id": task.task_id,
            "title": task.title,
            "timestamp": datetime.now().isoformat(),
            "model_responses": responses,
            "summary": {},
            "recommendations": [],
            "consensus": {}
        }
        
        # 分析結果の統合
        if AIModel.O3.value in responses:
            o3_response = responses[AIModel.O3.value]
            integrated["summary"]["analysis"] = o3_response.get("analysis", "")
            integrated["recommendations"].extend(o3_response.get("recommendations", []))
        
        # レビュー結果の統合
        if AIModel.GEMINI.value in responses:
            gemini_response = responses[AIModel.GEMINI.value]
            integrated["summary"]["review"] = gemini_response.get("review", "")
            integrated["recommendations"].extend(gemini_response.get("recommendations", []))
        
        # コンセンサス生成
        integrated["consensus"] = self._generate_consensus(responses)
        
        return integrated
    
    def _generate_consensus(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """コンセンサス生成"""
        consensus = {
            "agreement_level": "medium",
            "key_points": [],
            "disagreements": [],
            "final_recommendation": ""
        }
        
        # 簡単なコンセンサス分析（実装は簡略化）
        all_recommendations = []
        for response in responses.values():
            all_recommendations.extend(response.get("recommendations", []))
        
        # 共通の推奨事項を特定
        recommendation_counts = {}
        for rec in all_recommendations:
            recommendation_counts[rec] = recommendation_counts.get(rec, 0) + 1
        
        # 最も支持された推奨事項
        if recommendation_counts:
            consensus["final_recommendation"] = max(recommendation_counts, key=recommendation_counts.get)
            consensus["key_points"] = list(recommendation_counts.keys())
        
        return consensus
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスク状況取得"""
        with self._lock:
            if task_id in self.active_tasks:
                return self.active_tasks[task_id].to_dict()
        return None
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """アクティブタスク一覧"""
        with self._lock:
            return [task.to_dict() for task in self.active_tasks.values()]
    
    def get_task_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスク結果取得"""
        with self._lock:
            return self.task_results.get(task_id)


class MCPCollaborationSystem:
    """MCP協業システム"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # MCP クライアント初期化
        self.mcp_client = MCPClient(AIModel.CLAUDE, self.logger)
        
        # オーケストレーター初期化
        self.orchestrator = CollaborationOrchestrator(self.mcp_client, self.logger)
        
        # エンドポイント設定
        self._setup_endpoints()
        
        # メッセージハンドラー設定
        self.mcp_client.add_message_handler(self._handle_incoming_message)
        
        self.logger.info("MCP Collaboration System initialized")
    
    def _setup_endpoints(self) -> None:
        """エンドポイント設定"""
        endpoints_config = self.config.get("endpoints", {})
        
        for model_name, endpoint_config in endpoints_config.items():
            try:
                model = AIModel(model_name.upper())
                endpoint = AIModelEndpoint(
                    model=model,
                    endpoint_url=endpoint_config["url"],
                    api_key=endpoint_config.get("api_key"),
                    headers=endpoint_config.get("headers", {}),
                    timeout=endpoint_config.get("timeout", 30),
                    max_retries=endpoint_config.get("max_retries", 3),
                    is_active=endpoint_config.get("is_active", True)
                )
                self.mcp_client.add_endpoint(endpoint)
            except (ValueError, KeyError) as e:
                self.logger.error(f"Invalid endpoint configuration for {model_name}: {e}")
    
    def _handle_incoming_message(self, message: MCPMessage) -> None:
        """受信メッセージ処理"""
        self.logger.info(f"Received message from {message.sender.value}: {message.message_type.value}")
        
        if message.message_type == MCPMessageType.REQUEST:
            # リクエスト処理
            content = message.content
            if content.get("type") == "collaboration_request":
                self._handle_collaboration_request(message)
        elif message.message_type == MCPMessageType.RESPONSE:
            # レスポンス処理
            self._handle_collaboration_response(message)
    
    def _handle_collaboration_request(self, message: MCPMessage) -> None:
        """協業リクエスト処理"""
        try:
            content = message.content
            
            # 協業タスクの処理をシミュレート
            response_content = {
                "task_id": content.get("task_id"),
                "status": "completed",
                "analysis": f"Analysis of: {content.get('title')}",
                "recommendations": [
                    "Implement proper error handling",
                    "Add comprehensive tests",
                    "Improve documentation"
                ],
                "confidence": 0.85
            }
            
            # レスポンス送信
            response_message = MCPMessage(
                message_id=str(uuid.uuid4()),
                message_type=MCPMessageType.RESPONSE,
                sender=self.mcp_client.model,
                recipient=message.sender,
                content=response_content,
                timestamp=datetime.now(),
                conversation_id=message.conversation_id,
                reply_to=message.message_id
            )
            
            # 非同期送信をスケジュール
            asyncio.create_task(self.mcp_client.send_message(response_message))
            
        except Exception as e:
            self.logger.error(f"Error handling collaboration request: {e}")
    
    def _handle_collaboration_response(self, message: MCPMessage) -> None:
        """協業レスポンス処理"""
        self.logger.info(f"Collaboration response received from {message.sender.value}")
        # レスポンス処理はオーケストレーターで行われる
    
    async def collaborate_on_task(self, title: str, description: str, 
                                context: Optional[Dict[str, Any]] = None,
                                pattern: str = "analysis_review") -> Dict[str, Any]:
        """タスクで協業"""
        try:
            # 協業タスク作成
            task = self.orchestrator.create_collaboration_task(
                title=title,
                description=description,
                pattern=pattern,
                context=context
            )
            
            # タスク実行
            result = await self.orchestrator.execute_collaboration_task(task.task_id)
            
            return {
                "task_id": task.task_id,
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Collaboration failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_collaboration_status(self) -> Dict[str, Any]:
        """協業状況取得"""
        return {
            "active_tasks": self.orchestrator.get_active_tasks(),
            "endpoints": {
                model.value: endpoint.to_dict() 
                for model, endpoint in self.mcp_client.endpoints.items()
            },
            "conversation_count": len(self.mcp_client.conversation_history),
            "system_status": "active"
        }
    
    async def close(self) -> None:
        """システム終了"""
        await self.mcp_client.close()
        self.logger.info("MCP Collaboration System closed")