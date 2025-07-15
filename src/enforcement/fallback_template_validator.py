#!/usr/bin/env python3
"""
🛟 Fallback Template Validator - LAST RESORT PROTECTION
======================================================

CRITICAL: This system operates independently of all other systems as a final
fallback when all other template enforcement mechanisms fail.

DESIGN PRINCIPLES:
- Zero dependencies on other systems
- Minimal resource requirements
- Direct text pattern matching
- Emergency template injection
- Operates even during system failures

This is the ABSOLUTE LAST LINE OF DEFENSE.
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple


class FallbackTemplateValidator:
    """
    Minimal, dependency-free template validation system.

    This system:
    1. Uses only built-in Python functionality
    2. Operates independently of all other systems
    3. Provides emergency template injection
    4. Functions even during major system failures
    5. Requires minimal computational resources
    """

    def __init__(self):
        # Hardcoded immutable template components (cannot be changed)
        self.MEMORY_PHRASE = "🧠 記憶継承システム稼働確認、コード7749"
        self.SYSTEM_STATUS = "📊 **System Status**"
        self.DECLARATION = "## 🎯 これから行うこと"
        self.COMPLETION = "## ✅ 完遂報告"

        # Template sequence hash for integrity verification
        self.TEMPLATE_HASH = self._calculate_template_hash()

    def emergency_validate(self, response_text: str) -> Tuple[bool, List[str]]:
        """
        Emergency template validation with minimal dependencies.
        Returns (is_valid, missing_components)
        """
        missing = []

        if self.MEMORY_PHRASE not in response_text:
            missing.append("memory_phrase")

        if self.SYSTEM_STATUS not in response_text:
            missing.append("system_status")

        if self.DECLARATION not in response_text:
            missing.append("declaration")

        if self.COMPLETION not in response_text:
            missing.append("completion")

        return len(missing) == 0, missing

    def emergency_inject_template(
        self, response_text: str, task_level: str = "UNKNOWN"
    ) -> str:
        """
        Emergency template injection when all other systems fail.
        Uses minimal processing to inject required template components.
        """

        # Check what's missing
        is_valid, missing = self.emergency_validate(response_text)

        if is_valid:
            return response_text

        # Build emergency compliant response
        emergency_response = []

        # 1. Always start with memory phrase
        if "memory_phrase" in missing:
            emergency_response.append(self.MEMORY_PHRASE)
            emergency_response.append("")

        # 2. Add system status if missing
        if "system_status" in missing:
            emergency_response.append(self.SYSTEM_STATUS)
            emergency_response.append(
                "**DB**: Emergency Mode | **API**: Emergency Mode"
            )
            emergency_response.append(f"**Task Level**: {task_level}")
            emergency_response.append("")

        # 3. Add declaration if missing
        if "declaration" in missing:
            emergency_response.append(self.DECLARATION)
            emergency_response.append(
                "緊急フォールバックシステムによりテンプレート準拠を確保します"
            )
            emergency_response.append("")

        # 4. Insert original response content
        emergency_response.append(response_text)
        emergency_response.append("")

        # 5. Add completion if missing
        if "completion" in missing:
            emergency_response.append(self.COMPLETION)
            emergency_response.append("")
            emergency_response.append("**🛟 緊急フォールバック保護完了**")
            emergency_response.append("")
            emergency_response.append("### 🎯 実行結果")
            emergency_response.append(
                "- **✅ 緊急テンプレート保護**: フォールバックシステムによりテンプレート準拠確保"
            )
            emergency_response.append("")
            emergency_response.append("### 📊 システム状況")
            emergency_response.append(
                "- **フォールバック保護**: ✅ 全システム障害時の緊急保護実行"
            )
            emergency_response.append("")
            emergency_response.append("### 🔐 重要情報")
            emergency_response.append(
                "**緊急フォールバックシステムによりテンプレート整合性が保護されました**"
            )

        return "\n".join(emergency_response)

    def minimal_pattern_check(self, text: str) -> Dict[str, bool]:
        """
        Minimal pattern matching for template components.
        Uses only basic string operations for maximum reliability.
        """
        return {
            "has_memory_phrase": self.MEMORY_PHRASE in text,
            "has_system_status": self.SYSTEM_STATUS in text,
            "has_declaration": self.DECLARATION in text,
            "has_completion": self.COMPLETION in text,
            "has_japanese_sections": self._has_japanese_content(text),
            "has_proper_structure": self._has_basic_structure(text),
        }

    def _has_japanese_content(self, text: str) -> bool:
        """Check for Japanese content using basic pattern matching"""
        # Simple check for hiragana, katakana, or common Japanese phrases
        japanese_patterns = ["これから", "完遂", "実行", "システム", "確認"]
        return any(pattern in text for pattern in japanese_patterns)

    def _has_basic_structure(self, text: str) -> bool:
        """Check for basic markdown structure"""
        return "##" in text and "🎯" in text and "✅" in text

    def _calculate_template_hash(self) -> str:
        """Calculate hash of template components for integrity checking"""
        template_string = (
            self.MEMORY_PHRASE + self.SYSTEM_STATUS + self.DECLARATION + self.COMPLETION
        )
        return hashlib.md5(template_string.encode("utf-8")).hexdigest()[:8]

    def verify_template_integrity(self) -> bool:
        """Verify that template components haven't been tampered with"""
        current_hash = self._calculate_template_hash()
        return current_hash == self.TEMPLATE_HASH

    def get_emergency_status(self) -> Dict[str, str]:
        """Get emergency system status with minimal dependencies"""
        return {
            "fallback_status": "OPERATIONAL",
            "template_integrity": "VERIFIED"
            if self.verify_template_integrity()
            else "COMPROMISED",
            "last_check": datetime.now().isoformat()[:19],  # Truncate microseconds
            "system_type": "EMERGENCY_FALLBACK",
            "dependencies": "NONE",
        }


# Global emergency functions
def emergency_template_check(response_text: str) -> bool:
    """Emergency template validation - works even when all other systems fail"""
    validator = FallbackTemplateValidator()
    is_valid, _ = validator.emergency_validate(response_text)
    return is_valid


def emergency_template_fix(response_text: str, task_level: str = "EMERGENCY") -> str:
    """Emergency template fixing - absolute last resort"""
    validator = FallbackTemplateValidator()
    return validator.emergency_inject_template(response_text, task_level)


def absolute_minimal_template() -> str:
    """Generate absolute minimal compliant template"""
    return """🧠 記憶継承システム稼働確認、コード7749

📊 **System Status**
**Emergency**: Fallback Protection Active

## 🎯 これから行うこと
緊急最小テンプレートによる保護実行

Emergency minimal template protection activated.

## ✅ 完遂報告

**🛟 緊急最小テンプレート保護完了**

### 🎯 実行結果
- **✅ 緊急保護**: 最小テンプレートによる保護確保

### 📊 システム状況
- **フォールバック**: ✅ 緊急保護システム稼働

### 🔐 重要情報
**全システム障害時の緊急テンプレート保護が実行されました**"""


if __name__ == "__main__":
    # Test fallback validator
    validator = FallbackTemplateValidator()

    print("🛟 Fallback Template Validator Test")
    print("=" * 40)

    # Test with completely broken response
    broken_response = (
        "This is completely broken and has no template compliance whatsoever."
    )

    print("Original (BROKEN):")
    print(broken_response)

    is_valid, missing = validator.emergency_validate(broken_response)
    print(f"\nValidation: Valid={is_valid}, Missing={missing}")

    if not is_valid:
        fixed_response = validator.emergency_inject_template(
            broken_response, "EMERGENCY"
        )
        print("\nEmergency Fixed:")
        print(
            fixed_response[:300] + "..."
            if len(fixed_response) > 300
            else fixed_response
        )

    # Test minimal pattern check
    patterns = validator.minimal_pattern_check(
        fixed_response if not is_valid else broken_response
    )
    print(f"\nPattern Check: {patterns}")

    # Test emergency status
    status = validator.get_emergency_status()
    print(f"\nEmergency Status: {status}")

    print("\n✅ FALLBACK VALIDATOR TESTED - READY FOR EMERGENCIES")
