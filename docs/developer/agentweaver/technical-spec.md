# 🏗️ AgentWeaver - 技術仕様書

## 📋 **システムアーキテクチャ**

### **全体構成**
```
┌─────────────────────────────────────────────────────────────┐
│                    AgentWeaver Platform                    │
├─────────────────────────────────────────────────────────────┤
│  OSS Library (Python)     │    SaaS Platform (Cloud)      │
│  ┌─────────────────────┐   │   ┌─────────────────────────┐  │
│  │ Core Engine         │   │   │ Web Dashboard           │  │
│  │ ├─ Agent Framework  │   │   │ ├─ Workflow Builder     │  │
│  │ ├─ Workflow Engine  │   │   │ ├─ Monitoring Console   │  │
│  │ ├─ Communication    │   │   │ └─ Analytics Dashboard  │  │
│  │ └─ Model Adapters   │   │   │                         │  │
│  └─────────────────────┘   │   └─────────────────────────┘  │
│  ┌─────────────────────┐   │   ┌─────────────────────────┐  │
│  │ Tools & Integrations│   │   │ Execution Runtime       │  │
│  │ ├─ Web Search       │   │   │ ├─ Container Orchestration│ │
│  │ ├─ File I/O         │   │   │ ├─ Queue Management     │  │
│  │ ├─ Database Access  │   │   │ └─ Auto Scaling         │  │
│  │ └─ API Connectors   │   │   │                         │  │
│  └─────────────────────┘   │   └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────▼───────────────┐
                │        Model Backends         │
                │ ┌─────┐ ┌─────┐ ┌─────┐ ┌────┐│
                │ │Claude│ │Gemini│ │ o3  │ │GPT ││
                │ └─────┘ └─────┘ └─────┘ └────┘│
                └───────────────────────────────┘
```

---

## 🔧 **Core OSS Library**

### **1. Agent Framework**

#### **Agent Definition API**
```python
# agent.py
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    CLAUDE = "claude"
    GEMINI = "gemini"
    O3 = "o3"
    GPT = "gpt"
    LLAMA = "llama"

@dataclass
class AgentConfig:
    role: str
    model: ModelType
    tools: List[str] = None
    personality: str = "helpful, professional"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30

class Agent:
    def __init__(self, config: AgentConfig, func: Callable):
        self.config = config
        self.func = func
        self.model_adapter = ModelAdapterFactory.create(config.model)
        self.tools = ToolRegistry.get_tools(config.tools or [])
    
    async def execute(self, input_data: Any, context: Dict = None) -> Any:
        # 1. 入力データの前処理
        processed_input = self._preprocess_input(input_data, context)
        
        # 2. LLM実行
        response = await self.model_adapter.generate(
            prompt=self._build_prompt(processed_input),
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        # 3. ツール実行（必要に応じて）
        if self._needs_tool_execution(response):
            tool_results = await self._execute_tools(response)
            response = await self._integrate_tool_results(response, tool_results)
        
        # 4. 結果の後処理
        return self._postprocess_output(response)

def agent(role: str, model: str, **kwargs):
    """エージェント定義デコレータ"""
    def decorator(func: Callable):
        config = AgentConfig(
            role=role,
            model=ModelType(model),
            **kwargs
        )
        return Agent(config, func)
    return decorator
```

#### **Model Adapter System**
```python
# model_adapters.py
from abc import ABC, abstractmethod

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def get_cost(self, input_tokens: int, output_tokens: int) -> float:
        pass

class ClaudeAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.messages.create(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.content[0].text

class GeminiAdapter(ModelAdapter):
    def __init__(self, api_key: str):
        self.client = genai.GenerativeModel('gemini-pro')
    
    async def generate(self, prompt: str, **kwargs) -> str:
        response = await self.client.generate_content_async(prompt)
        return response.text

class ModelAdapterFactory:
    @staticmethod
    def create(model_type: ModelType) -> ModelAdapter:
        adapters = {
            ModelType.CLAUDE: ClaudeAdapter,
            ModelType.GEMINI: GeminiAdapter,
            ModelType.O3: O3Adapter,
            ModelType.GPT: GPTAdapter,
        }
        return adapters[model_type](api_key=get_api_key(model_type))
```

### **2. Workflow Engine**

#### **Workflow Orchestration**
```python
# workflow.py
from typing import List, Union, Dict, Any
from enum import Enum
import asyncio

class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"

class WorkflowResult:
    def __init__(self):
        self.results: List[Any] = []
        self.execution_time: float = 0
        self.total_cost: float = 0
        self.errors: List[Exception] = []

class AgentWorkflow:
    def __init__(
        self,
        agents: List[Agent],
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        error_handling: str = "retry_3_times",
        max_parallel: int = 5
    ):
        self.agents = agents
        self.mode = mode
        self.error_handling = error_handling
        self.max_parallel = max_parallel
        self.state_manager = WorkflowStateManager()
    
    async def run(
        self,
        input_data: Any,
        context: Dict = None
    ) -> WorkflowResult:
        result = WorkflowResult()
        start_time = time.time()
        
        try:
            if self.mode == ExecutionMode.SEQUENTIAL:
                result.results = await self._run_sequential(input_data, context)
            elif self.mode == ExecutionMode.PARALLEL:
                result.results = await self._run_parallel(input_data, context)
            elif self.mode == ExecutionMode.CONDITIONAL:
                result.results = await self._run_conditional(input_data, context)
                
        except Exception as e:
            result.errors.append(e)
            if self.error_handling.startswith("retry"):
                retries = int(self.error_handling.split("_")[1])
                result = await self._retry_execution(input_data, context, retries)
        
        result.execution_time = time.time() - start_time
        result.total_cost = self._calculate_total_cost()
        
        return result
    
    async def _run_sequential(self, input_data: Any, context: Dict) -> List[Any]:
        results = []
        current_input = input_data
        
        for agent in self.agents:
            agent_result = await agent.execute(current_input, context)
            results.append(agent_result)
            current_input = agent_result  # 前の結果を次の入力に
            
            # 中間状態保存
            await self.state_manager.save_intermediate_state({
                'agent': agent.config.role,
                'input': current_input,
                'result': agent_result
            })
        
        return results
    
    async def _run_parallel(self, input_data: Any, context: Dict) -> List[Any]:
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def execute_with_semaphore(agent):
            async with semaphore:
                return await agent.execute(input_data, context)
        
        tasks = [execute_with_semaphore(agent) for agent in self.agents]
        return await asyncio.gather(*tasks)
```

### **3. Inter-Agent Communication**

#### **Communication Framework**
```python
# communication.py
from typing import Dict, Any, Optional
import asyncio
from dataclasses import dataclass

@dataclass
class Message:
    sender: str
    receiver: str
    content: Any
    timestamp: float
    message_type: str = "general"
    requires_response: bool = False

class CommunicationHub:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_history: List[Message] = []
    
    def register_agent(self, agent: Agent):
        self.agents[agent.config.role] = agent
    
    async def send_message(self, message: Message):
        await self.message_queue.put(message)
        self.message_history.append(message)
    
    async def process_messages(self):
        while True:
            message = await self.message_queue.get()
            
            if message.receiver in self.agents:
                receiver_agent = self.agents[message.receiver]
                
                if message.requires_response:
                    response = await receiver_agent.execute(
                        message.content,
                        context={'sender': message.sender}
                    )
                    
                    response_message = Message(
                        sender=message.receiver,
                        receiver=message.sender,
                        content=response,
                        timestamp=time.time(),
                        message_type="response"
                    )
                    await self.send_message(response_message)

class CoordinatorAgent:
    """エージェント間の調整を行う特別なエージェント"""
    
    def __init__(self, communication_hub: CommunicationHub):
        self.hub = communication_hub
        self.task_queue: List[Dict] = []
    
    async def distribute_task(self, task: Dict, available_agents: List[Agent]):
        # タスクの複雑さと各エージェントの専門性を分析
        task_analysis = await self._analyze_task_complexity(task)
        
        # 最適なエージェントの選択
        selected_agent = self._select_best_agent(task_analysis, available_agents)
        
        # タスク配布
        message = Message(
            sender="coordinator",
            receiver=selected_agent.config.role,
            content=task,
            timestamp=time.time(),
            requires_response=True
        )
        
        await self.hub.send_message(message)
        return selected_agent
    
    def _select_best_agent(self, task_analysis: Dict, agents: List[Agent]) -> Agent:
        # エージェントのスキル適合度を計算
        scores = {}
        for agent in agents:
            score = self._calculate_skill_match(task_analysis, agent)
            scores[agent] = score
        
        return max(scores.keys(), key=lambda x: scores[x])
```

---

## 🌐 **SaaS Platform**

### **4. Web Dashboard (React + TypeScript)**

#### **Frontend Architecture**
```typescript
// types/workflow.ts
export interface AgentConfig {
  role: string;
  model: 'claude' | 'gemini' | 'o3' | 'gpt';
  tools: string[];
  personality: string;
  temperature: number;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  agents: AgentConfig[];
  execution_mode: 'sequential' | 'parallel' | 'conditional';
  created_at: string;
  updated_at: string;
}

export interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  input_data: any;
  results: any[];
  execution_time: number;
  total_cost: number;
  started_at: string;
  completed_at?: string;
}
```

```tsx
// components/WorkflowBuilder.tsx
import React, { useState } from 'react';
import { WorkflowDefinition, AgentConfig } from '../types/workflow';

export const WorkflowBuilder: React.FC = () => {
  const [workflow, setWorkflow] = useState<WorkflowDefinition>({
    id: '',
    name: '',
    description: '',
    agents: [],
    execution_mode: 'sequential',
    created_at: '',
    updated_at: ''
  });

  const addAgent = () => {
    const newAgent: AgentConfig = {
      role: '',
      model: 'claude',
      tools: [],
      personality: 'helpful, professional',
      temperature: 0.7
    };
    setWorkflow(prev => ({
      ...prev,
      agents: [...prev.agents, newAgent]
    }));
  };

  const updateAgent = (index: number, updatedAgent: AgentConfig) => {
    setWorkflow(prev => ({
      ...prev,
      agents: prev.agents.map((agent, i) => 
        i === index ? updatedAgent : agent
      )
    }));
  };

  return (
    <div className="workflow-builder">
      <div className="workflow-header">
        <input
          type="text"
          placeholder="Workflow Name"
          value={workflow.name}
          onChange={(e) => setWorkflow(prev => ({
            ...prev,
            name: e.target.value
          }))}
        />
        <textarea
          placeholder="Description"
          value={workflow.description}
          onChange={(e) => setWorkflow(prev => ({
            ...prev,
            description: e.target.value
          }))}
        />
      </div>
      
      <div className="agents-section">
        <h3>Agents</h3>
        {workflow.agents.map((agent, index) => (
          <AgentConfigCard
            key={index}
            agent={agent}
            onUpdate={(updatedAgent) => updateAgent(index, updatedAgent)}
            onRemove={() => removeAgent(index)}
          />
        ))}
        <button onClick={addAgent} className="add-agent-btn">
          Add Agent
        </button>
      </div>
      
      <div className="execution-settings">
        <label>Execution Mode:</label>
        <select
          value={workflow.execution_mode}
          onChange={(e) => setWorkflow(prev => ({
            ...prev,
            execution_mode: e.target.value as any
          }))}
        >
          <option value="sequential">Sequential</option>
          <option value="parallel">Parallel</option>
          <option value="conditional">Conditional</option>
        </select>
      </div>
    </div>
  );
};
```

### **5. Backend API (FastAPI + Python)**

#### **API Server**
```python
# api/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import List, Dict, Any
import asyncio

app = FastAPI(title="AgentWeaver API", version="1.0.0")
security = HTTPBearer()

@app.post("/workflows/", response_model=WorkflowDefinition)
async def create_workflow(
    workflow: WorkflowDefinitionCreate,
    current_user: User = Depends(get_current_user)
):
    # ワークフロー定義をデータベースに保存
    db_workflow = await WorkflowService.create(workflow, current_user.id)
    return db_workflow

@app.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    # ワークフロー定義を取得
    workflow = await WorkflowService.get(workflow_id, current_user.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # 実行をキューに追加
    execution_id = await ExecutionService.enqueue_execution(
        workflow_id=workflow_id,
        input_data=execution_request.input_data,
        user_id=current_user.id
    )
    
    return {"execution_id": execution_id, "status": "queued"}

@app.get("/executions/{execution_id}")
async def get_execution_status(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    execution = await ExecutionService.get_execution(execution_id, current_user.id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

@app.get("/executions/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    logs = await LoggingService.get_execution_logs(execution_id, current_user.id)
    return {"logs": logs}
```

### **6. Execution Runtime**

#### **Container Orchestration**
```python
# runtime/executor.py
import docker
import asyncio
from typing import Dict, Any

class WorkflowExecutor:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.execution_queue = asyncio.Queue()
        self.running_executions: Dict[str, Any] = {}
    
    async def start_executor(self):
        """実行エンジンの開始"""
        while True:
            execution_request = await self.execution_queue.get()
            asyncio.create_task(self._execute_workflow(execution_request))
    
    async def _execute_workflow(self, execution_request: Dict):
        execution_id = execution_request['execution_id']
        
        try:
            # Dockerコンテナでワークフローを実行
            container = self.docker_client.containers.run(
                image="agentweaver/runtime:latest",
                command=f"python -m agentweaver.runner {execution_id}",
                environment={
                    "EXECUTION_ID": execution_id,
                    "WORKFLOW_CONFIG": execution_request['workflow_config'],
                    "INPUT_DATA": execution_request['input_data']
                },
                detach=True,
                mem_limit="1g",
                cpu_period=100000,
                cpu_quota=50000  # 0.5 CPU
            )
            
            self.running_executions[execution_id] = {
                'container': container,
                'start_time': time.time()
            }
            
            # 実行完了を待機
            exit_code = container.wait()
            logs = container.logs().decode('utf-8')
            
            # 結果をデータベースに保存
            await ExecutionService.update_execution_result(
                execution_id=execution_id,
                exit_code=exit_code['StatusCode'],
                logs=logs
            )
            
        except Exception as e:
            await ExecutionService.mark_execution_failed(execution_id, str(e))
        
        finally:
            # コンテナクリーンアップ
            if execution_id in self.running_executions:
                container = self.running_executions[execution_id]['container']
                container.remove(force=True)
                del self.running_executions[execution_id]
```

---

## 📊 **データベース設計**

### **PostgreSQL Schema**
```sql
-- ユーザー管理
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ワークフロー定義
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ワークフロー実行履歴
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflows(id),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    input_data JSONB,
    results JSONB,
    execution_time INTEGER, -- ミリ秒
    total_cost DECIMAL(10,4),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    error_message TEXT
);

-- 実行ログ
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES workflow_executions(id),
    agent_role VARCHAR(255),
    log_level VARCHAR(50),
    message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 利用統計
CREATE TABLE usage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    metric_type VARCHAR(100), -- 'api_calls', 'execution_time', 'tokens_used'
    value DECIMAL(15,4),
    date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 **セキュリティ設計**

### **認証・認可**
```python
# auth/security.py
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
import bcrypt

class AuthService:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# API Key暗号化
class APIKeyManager:
    @staticmethod
    def encrypt_api_key(api_key: str, user_id: str) -> str:
        cipher = Fernet(derive_key(user_id))
        return cipher.encrypt(api_key.encode()).decode()
    
    @staticmethod
    def decrypt_api_key(encrypted_key: str, user_id: str) -> str:
        cipher = Fernet(derive_key(user_id))
        return cipher.decrypt(encrypted_key.encode()).decode()
```

---

## 📈 **監視・メトリクス**

### **Prometheus Metrics**
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# カウンタ
workflow_executions_total = Counter(
    'agentweaver_workflow_executions_total',
    'Total number of workflow executions',
    ['user_id', 'workflow_id', 'status']
)

# ヒストグラム
workflow_execution_duration = Histogram(
    'agentweaver_workflow_execution_duration_seconds',
    'Workflow execution duration',
    ['workflow_id']
)

# ゲージ
active_executions = Gauge(
    'agentweaver_active_executions',
    'Number of currently running executions'
)

# API使用量
api_calls_total = Counter(
    'agentweaver_api_calls_total',
    'Total API calls',
    ['endpoint', 'method', 'status_code']
)
```

---

**📝 技術仕様書作成完了**  
**🎯 次フェーズ**: 既存システムからの抽象化設計開始