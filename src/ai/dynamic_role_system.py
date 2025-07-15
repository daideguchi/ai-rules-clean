#!/usr/bin/env python3
"""
Dynamic Role System - AI組織の動的役職生成・調整システム
Based on o3 and Gemini strategic guidance for production-grade AI orchestration
"""

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class RoleType(Enum):
    CORE = "core"  # Essential roles (PRESIDENT, COORDINATOR)
    SPECIALIZED = "specialized"  # Domain-specific roles
    TEMPORARY = "temporary"  # Task-specific temporary roles
    ADAPTIVE = "adaptive"  # Auto-generated from requirements


class RoleStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    RETIRED = "retired"


@dataclass
class RoleCapability:
    """Role capability contract definition"""

    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    success_criteria: List[str]
    dependencies: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class RoleDefinition:
    """Complete role definition with capabilities and metadata"""

    id: str
    name: str
    display_name: str
    role_type: RoleType
    capabilities: List[RoleCapability]
    responsibilities: List[str]
    authority_level: int  # 1-10
    decision_scope: List[str]
    collaboration_requirements: List[str]
    specialization: str
    required_skills: List[str]
    status: RoleStatus = RoleStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    performance_score: float = 0.0
    task_history: List[str] = field(default_factory=list)


@dataclass
class TaskRequest:
    """Task request for role assignment"""

    id: str
    title: str
    description: str
    requirements: List[str]
    complexity: str  # low, medium, high, critical
    estimated_effort: str  # hours, days, weeks
    priority: str  # low, medium, high, urgent
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class DynamicRoleSystem:
    """
    Dynamic Role Generation & Coordination System
    Implements o3/Gemini strategic guidance for adaptive AI organization
    """

    def __init__(self, project_path: str = "/Users/dd/Desktop/1_dev/coding-rule2"):
        self.project_path = Path(project_path)
        self.roles_registry: Dict[str, RoleDefinition] = {}
        self.active_assignments: Dict[str, str] = {}  # task_id -> role_id
        self.coordination_graph: Dict[
            str, Set[str]
        ] = {}  # role_id -> {collaborating_role_ids}
        self.logger = self._setup_logging()

        # Initialize core roles
        self._initialize_core_roles()

        # Load existing roles
        self._load_roles_registry()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for role system"""
        logger = logging.getLogger("DynamicRoleSystem")
        logger.setLevel(logging.INFO)

        log_dir = self.project_path / "runtime" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(log_dir / "dynamic_role_system.log")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        return logger

    def _initialize_core_roles(self):
        """Initialize essential core roles"""

        # PRESIDENT role
        president_capabilities = [
            RoleCapability(
                name="strategic_decision_making",
                description="Make high-level strategic decisions for project direction",
                inputs=[
                    "project_status",
                    "stakeholder_requirements",
                    "risk_assessment",
                ],
                outputs=["strategic_plan", "resource_allocation", "priority_decisions"],
                success_criteria=[
                    "alignment_with_goals",
                    "stakeholder_satisfaction",
                    "risk_mitigation",
                ],
            ),
            RoleCapability(
                name="crisis_management",
                description="Handle critical issues and emergency situations",
                inputs=["crisis_report", "system_status", "team_availability"],
                outputs=[
                    "crisis_response_plan",
                    "emergency_actions",
                    "communication_plan",
                ],
                success_criteria=[
                    "crisis_resolution_time",
                    "minimal_impact",
                    "team_coordination",
                ],
            ),
        ]

        president_role = RoleDefinition(
            id="president",
            name="PRESIDENT",
            display_name="プレジデント",
            role_type=RoleType.CORE,
            capabilities=president_capabilities,
            responsibilities=[
                "Strategic decision making",
                "Overall system supervision",
                "Crisis management and emergency response",
                "Final quality assurance",
            ],
            authority_level=10,
            decision_scope=["strategic_decisions", "crisis_response", "final_approval"],
            collaboration_requirements=[
                "Information aggregation from all roles",
                "o3・Gemini consultation",
            ],
            specialization="strategic_leadership",
            required_skills=["leadership", "decision_making"],
        )

        # COORDINATOR role
        coordinator_capabilities = [
            RoleCapability(
                name="task_coordination",
                description="Coordinate tasks and resources across roles",
                inputs=["task_queue", "role_availability", "project_timeline"],
                outputs=["task_assignments", "coordination_plan", "progress_reports"],
                success_criteria=[
                    "task_completion_rate",
                    "resource_efficiency",
                    "timeline_adherence",
                ],
            )
        ]

        coordinator_role = RoleDefinition(
            id="coordinator",
            name="COORDINATOR",
            display_name="コーディネーター",
            role_type=RoleType.CORE,
            capabilities=coordinator_capabilities,
            responsibilities=[
                "Inter-role coordination",
                "Task allocation optimization",
                "Communication facilitation",
                "Progress monitoring",
            ],
            authority_level=8,
            decision_scope=["task_coordination", "resource_allocation"],
            collaboration_requirements=[
                "Regular contact with all roles",
                "PRESIDENT support",
            ],
            specialization="coordination",
            required_skills=["coordination", "communication"],
        )

        self.roles_registry["president"] = president_role
        self.roles_registry["coordinator"] = coordinator_role

        self.logger.info("Core roles initialized: PRESIDENT, COORDINATOR")

    def generate_role_from_requirements(
        self, task_request: TaskRequest
    ) -> Optional[RoleDefinition]:
        """
        Generate specialized role based on task requirements
        Implements o3's "Role Synthesizer" concept
        """
        try:
            # Analyze task requirements to determine needed specialization
            specialization = self._analyze_specialization_needs(task_request)

            # Check if suitable role already exists
            existing_role = self._find_suitable_existing_role(
                task_request, specialization
            )
            if existing_role:
                return existing_role

            # Generate new specialized role
            role_id = f"specialist_{specialization}_{uuid.uuid4().hex[:8]}"

            capabilities = self._generate_capabilities_for_specialization(
                specialization, task_request
            )

            new_role = RoleDefinition(
                id=role_id,
                name=f"{specialization.upper()}_SPECIALIST",
                display_name=f"{specialization}スペシャリスト",
                role_type=RoleType.SPECIALIZED,
                capabilities=capabilities,
                responsibilities=self._generate_responsibilities(
                    specialization, task_request
                ),
                authority_level=self._determine_authority_level(task_request),
                decision_scope=[f"{specialization}_decisions"],
                collaboration_requirements=[
                    "COORDINATOR coordination",
                    "PRESIDENT reporting",
                ],
                specialization=specialization,
                required_skills=self._extract_required_skills(task_request),
            )

            # Register new role
            self.roles_registry[role_id] = new_role
            self.logger.info(
                f"Generated new specialized role: {new_role.name} for {specialization}"
            )

            return new_role

        except Exception as e:
            self.logger.error(f"Role generation failed: {e}")
            return None

    def _analyze_specialization_needs(self, task_request: TaskRequest) -> str:
        """Analyze task to determine required specialization"""
        description_lower = task_request.description.lower()
        requirements_text = " ".join(task_request.requirements).lower()
        combined_text = f"{description_lower} {requirements_text}"

        # Domain specialization mapping
        specializations = {
            "database": ["database", "sql", "schema", "migration", "query"],
            "frontend": ["ui", "css", "html", "react", "vue", "frontend"],
            "backend": ["api", "server", "backend", "microservice", "endpoint"],
            "security": ["security", "auth", "encryption", "vulnerability", "audit"],
            "testing": ["test", "testing", "qa", "validation", "verification"],
            "devops": ["deploy", "ci/cd", "infrastructure", "docker", "kubernetes"],
            "data": ["data", "analytics", "pipeline", "etl", "visualization"],
            "mobile": ["mobile", "ios", "android", "app", "native"],
            "performance": ["performance", "optimization", "scaling", "profiling"],
            "documentation": ["documentation", "docs", "readme", "specification"],
        }

        for specialization, keywords in specializations.items():
            if any(keyword in combined_text for keyword in keywords):
                return specialization

        # Default to general development
        return "development"

    def _find_suitable_existing_role(
        self, task_request: TaskRequest, specialization: str
    ) -> Optional[RoleDefinition]:
        """Find existing role that can handle the task"""
        for role in self.roles_registry.values():
            if (
                role.specialization == specialization
                and role.status == RoleStatus.ACTIVE
                and role.role_type in [RoleType.SPECIALIZED, RoleType.ADAPTIVE]
            ):
                return role
        return None

    def _generate_capabilities_for_specialization(
        self, specialization: str, task_request: TaskRequest
    ) -> List[RoleCapability]:
        """Generate capabilities based on specialization"""

        capability_templates = {
            "database": RoleCapability(
                name="database_management",
                description="Design, implement and maintain database systems",
                inputs=[
                    "schema_requirements",
                    "data_models",
                    "performance_requirements",
                ],
                outputs=[
                    "database_schema",
                    "migration_scripts",
                    "performance_optimizations",
                ],
                success_criteria=[
                    "schema_consistency",
                    "query_performance",
                    "data_integrity",
                ],
            ),
            "frontend": RoleCapability(
                name="frontend_development",
                description="Build user interfaces and frontend applications",
                inputs=["ui_requirements", "design_specifications", "user_stories"],
                outputs=["ui_components", "frontend_code", "user_experience"],
                success_criteria=[
                    "ui_responsiveness",
                    "user_satisfaction",
                    "accessibility_compliance",
                ],
            ),
            "security": RoleCapability(
                name="security_implementation",
                description="Implement security measures and conduct audits",
                inputs=[
                    "security_requirements",
                    "threat_models",
                    "compliance_standards",
                ],
                outputs=[
                    "security_implementations",
                    "audit_reports",
                    "vulnerability_fixes",
                ],
                success_criteria=[
                    "security_compliance",
                    "vulnerability_reduction",
                    "audit_pass_rate",
                ],
            ),
        }

        if specialization in capability_templates:
            return [capability_templates[specialization]]

        # Default capability for unknown specializations
        return [
            RoleCapability(
                name=f"{specialization}_expertise",
                description=f"Provide {specialization} domain expertise",
                inputs=["requirements", "specifications", "context"],
                outputs=["solutions", "implementations", "recommendations"],
                success_criteria=[
                    "requirement_fulfillment",
                    "quality_standards",
                    "completion_time",
                ],
            )
        ]

    def _generate_responsibilities(
        self, specialization: str, task_request: TaskRequest
    ) -> List[str]:
        """Generate responsibilities based on specialization"""
        base_responsibilities = [
            f"{specialization.title()} implementation and design",
            f"{specialization.title()} best practices enforcement",
            f"Quality assurance for {specialization} deliverables",
            "Collaboration with other specialists",
        ]

        # Add task-specific responsibilities
        if task_request.complexity == "critical":
            base_responsibilities.append("Critical issue resolution")

        return base_responsibilities

    def _determine_authority_level(self, task_request: TaskRequest) -> int:
        """Determine authority level based on task characteristics"""
        base_level = 5

        if task_request.complexity == "critical":
            base_level += 2
        elif task_request.complexity == "high":
            base_level += 1

        if task_request.priority == "urgent":
            base_level += 1

        return min(base_level, 9)  # Max 9, PRESIDENT is 10

    def _extract_required_skills(self, task_request: TaskRequest) -> List[str]:
        """Extract required skills from task requirements"""
        skills = []

        # Extract from requirements
        for req in task_request.requirements:
            req_lower = req.lower()
            if "programming" in req_lower or "coding" in req_lower:
                skills.append("programming")
            if "design" in req_lower:
                skills.append("design")
            if "analysis" in req_lower:
                skills.append("analysis")
            if "testing" in req_lower:
                skills.append("testing")

        return skills if skills else ["general_expertise"]

    async def assign_task_to_role(
        self, task_request: TaskRequest
    ) -> Tuple[Optional[RoleDefinition], str]:
        """
        Assign task to most suitable role
        Implements role assignment mechanism
        """
        try:
            # 1. Try to find existing suitable role
            suitable_role = None
            for role in self.roles_registry.values():
                if self._is_role_suitable_for_task(role, task_request):
                    suitable_role = role
                    break

            # 2. Generate new role if no suitable one exists
            if not suitable_role:
                suitable_role = self.generate_role_from_requirements(task_request)

            if not suitable_role:
                return None, "Failed to find or generate suitable role"

            # 3. Check role availability
            if not self._is_role_available(suitable_role):
                return None, f"Role {suitable_role.name} is not available"

            # 4. Make assignment
            self.active_assignments[task_request.id] = suitable_role.id
            suitable_role.task_history.append(task_request.id)

            # 5. Set up coordination if needed
            await self._setup_task_coordination(suitable_role, task_request)

            self.logger.info(
                f"Task {task_request.id} assigned to role {suitable_role.name}"
            )

            return suitable_role, "Assignment successful"

        except Exception as e:
            self.logger.error(f"Task assignment failed: {e}")
            return None, f"Assignment failed: {e}"

    def _is_role_suitable_for_task(
        self, role: RoleDefinition, task_request: TaskRequest
    ) -> bool:
        """Check if role is suitable for the task"""
        if role.status != RoleStatus.ACTIVE:
            return False

        # Check specialization match
        task_specialization = self._analyze_specialization_needs(task_request)
        if role.specialization == task_specialization:
            return True

        # Check capability match
        for capability in role.capabilities:
            if any(
                keyword in capability.description.lower()
                for keyword in task_request.description.lower().split()
            ):
                return True

        return False

    def _is_role_available(self, role: RoleDefinition) -> bool:
        """Check if role is available for new tasks"""
        # Simple availability check - can be enhanced with workload management
        current_tasks = sum(
            1
            for task_id, role_id in self.active_assignments.items()
            if role_id == role.id
        )
        max_concurrent_tasks = 3 if role.role_type == RoleType.CORE else 1

        return current_tasks < max_concurrent_tasks

    async def _setup_task_coordination(
        self, assigned_role: RoleDefinition, task_request: TaskRequest
    ):
        """Set up coordination between roles for complex tasks"""
        # Determine required collaboration
        collaboration_needed = []

        if task_request.complexity in ["high", "critical"]:
            collaboration_needed.append("president")  # PRESIDENT oversight

        if assigned_role.role_type != RoleType.CORE:
            collaboration_needed.append("coordinator")  # COORDINATOR facilitation

        # Update coordination graph
        if assigned_role.id not in self.coordination_graph:
            self.coordination_graph[assigned_role.id] = set()

        for collaborator_id in collaboration_needed:
            if collaborator_id in self.roles_registry:
                self.coordination_graph[assigned_role.id].add(collaborator_id)

                # Bidirectional coordination
                if collaborator_id not in self.coordination_graph:
                    self.coordination_graph[collaborator_id] = set()
                self.coordination_graph[collaborator_id].add(assigned_role.id)

        self.logger.info(
            f"Coordination setup for {assigned_role.name}: {collaboration_needed}"
        )

    def get_role_performance_metrics(self, role_id: str) -> Dict[str, Any]:
        """Get performance metrics for a role"""
        if role_id not in self.roles_registry:
            return {}

        role = self.roles_registry[role_id]

        # Calculate basic metrics
        total_tasks = len(role.task_history)
        active_tasks = sum(
            1
            for task_id, assigned_role_id in self.active_assignments.items()
            if assigned_role_id == role_id
        )

        return {
            "role_id": role_id,
            "role_name": role.name,
            "total_tasks_completed": total_tasks,
            "active_tasks": active_tasks,
            "performance_score": role.performance_score,
            "authority_level": role.authority_level,
            "specialization": role.specialization,
            "status": role.status.value,
            "collaboration_count": len(self.coordination_graph.get(role_id, set())),
        }

    def _save_roles_registry(self):
        """Save roles registry to file"""
        try:
            registry_dir = self.project_path / "src" / "memory" / "core"
            registry_dir.mkdir(parents=True, exist_ok=True)

            registry_data = {
                "roles": {
                    role_id: asdict(role)
                    for role_id, role in self.roles_registry.items()
                },
                "active_assignments": self.active_assignments,
                "coordination_graph": {
                    k: list(v) for k, v in self.coordination_graph.items()
                },
                "last_updated": datetime.now().isoformat(),
            }

            with open(registry_dir / "dynamic_roles_registry.json", "w") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)

            self.logger.info(
                f"Roles registry saved with {len(self.roles_registry)} roles"
            )

        except Exception as e:
            self.logger.error(f"Failed to save roles registry: {e}")

    def _load_roles_registry(self):
        """Load roles registry from file"""
        try:
            registry_path = (
                self.project_path
                / "src"
                / "memory"
                / "core"
                / "dynamic_roles_registry.json"
            )

            if not registry_path.exists():
                self.logger.info("No existing roles registry found, starting fresh")
                return

            with open(registry_path) as f:
                registry_data = json.load(f)

            # Load roles
            for role_id, role_data in registry_data.get("roles", {}).items():
                # Convert enum fields back
                role_data["role_type"] = RoleType(role_data["role_type"])
                role_data["status"] = RoleStatus(role_data["status"])

                # Convert capabilities
                capabilities = []
                for cap_data in role_data.get("capabilities", []):
                    capabilities.append(RoleCapability(**cap_data))
                role_data["capabilities"] = capabilities

                self.roles_registry[role_id] = RoleDefinition(**role_data)

            # Load assignments and coordination
            self.active_assignments = registry_data.get("active_assignments", {})
            coordination_data = registry_data.get("coordination_graph", {})
            self.coordination_graph = {k: set(v) for k, v in coordination_data.items()}

            self.logger.info(
                f"Loaded roles registry with {len(self.roles_registry)} roles"
            )

        except Exception as e:
            self.logger.error(f"Failed to load roles registry: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "total_roles": len(self.roles_registry),
            "active_roles": sum(
                1
                for role in self.roles_registry.values()
                if role.status == RoleStatus.ACTIVE
            ),
            "active_assignments": len(self.active_assignments),
            "coordination_links": sum(
                len(links) for links in self.coordination_graph.values()
            ),
            "role_types": {
                role_type.value: sum(
                    1
                    for role in self.roles_registry.values()
                    if role.role_type == role_type
                )
                for role_type in RoleType
            },
        }


# Test and demonstration
async def demo_dynamic_role_system():
    """Demonstrate dynamic role system capabilities"""
    print("=== Dynamic Role System Demo ===")

    system = DynamicRoleSystem()

    # Create sample task requests
    tasks = [
        TaskRequest(
            id="task_001",
            title="Database Schema Design",
            description="Design database schema for user management system with PostgreSQL",
            requirements=[
                "PostgreSQL expertise",
                "Schema design",
                "Performance optimization",
            ],
            complexity="high",
            estimated_effort="3 days",
            priority="high",
        ),
        TaskRequest(
            id="task_002",
            title="Frontend UI Components",
            description="Create responsive UI components for user dashboard using React",
            requirements=["React development", "CSS styling", "Responsive design"],
            complexity="medium",
            estimated_effort="2 days",
            priority="medium",
        ),
        TaskRequest(
            id="task_003",
            title="Security Audit",
            description="Conduct comprehensive security audit of authentication system",
            requirements=[
                "Security expertise",
                "Authentication systems",
                "Vulnerability assessment",
            ],
            complexity="critical",
            estimated_effort="1 week",
            priority="urgent",
        ),
    ]

    # Process each task
    for task in tasks:
        print(f"\n--- Processing Task: {task.title} ---")
        assigned_role, message = await system.assign_task_to_role(task)

        if assigned_role:
            print(f"✅ Assigned to: {assigned_role.name}")
            print(f"   Specialization: {assigned_role.specialization}")
            print(f"   Authority Level: {assigned_role.authority_level}")
        else:
            print(f"❌ Assignment failed: {message}")

    # Show system status
    print("\n--- System Status ---")
    status = system.get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    # Show individual role metrics
    print("\n--- Role Performance Metrics ---")
    for role_id in system.roles_registry.keys():
        metrics = system.get_role_performance_metrics(role_id)
        print(
            f"{metrics['role_name']}: {metrics['total_tasks_completed']} tasks, Score: {metrics['performance_score']}"
        )

    # Save registry
    system._save_roles_registry()
    print("\n✅ Roles registry saved")


if __name__ == "__main__":
    asyncio.run(demo_dynamic_role_system())
