#!/usr/bin/env python3
"""
🔒 Pre-File Security Check Hook
機密ファイル保護とセキュリティ検証
"""

import json
import re
import sys

# 保護対象ファイルパターン
PROTECTED_PATTERNS = [
    r".*\.env$",
    r".*\.key$",
    r".*\.pem$",
    r".*secrets.*",
    r".*password.*",
    r".*\.p12$",
    r".*\.pfx$",
    r"/etc/passwd",
    r"/etc/shadow",
    r".*config.*credential.*",
]

# 機密情報検出パターン
SECRET_PATTERNS = [
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Password detected"),
    (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "API key detected"),
    (r"secret\s*=\s*['\"][^'\"]+['\"]", "Secret detected"),
    (r"token\s*=\s*['\"][^'\"]+['\"]", "Token detected"),
    (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private key detected"),
    (r"ssh-rsa\s+[A-Za-z0-9+/=]+", "SSH public key detected"),
]


def check_file_path_security(file_path: str) -> list[str]:
    """ファイルパスのセキュリティチェック"""
    issues = []

    # 保護ファイルパターンチェック
    for pattern in PROTECTED_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            issues.append(f"🔒 Protected file pattern detected: {file_path}")
            break

    # パストラバーサル検出
    if ".." in file_path:
        issues.append(f"⚠️  Path traversal detected: {file_path}")

    # システムファイル書き込み警告
    system_paths = ["/etc/", "/usr/", "/var/", "/sys/", "/proc/"]
    if any(file_path.startswith(path) for path in system_paths):
        issues.append(f"⚠️  System path modification: {file_path}")

    return issues


def check_content_security(content: str) -> list[str]:
    """ファイル内容のセキュリティチェック"""
    issues = []

    for pattern, message in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"🔒 {message} in file content")

    return issues


def main():
    try:
        # Hookからの入力を取得
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if tool_name not in ["Edit", "Write", "MultiEdit"]:
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "") or tool_input.get("new_string", "")

        if not file_path:
            sys.exit(0)

        # セキュリティチェック実行
        path_issues = check_file_path_security(file_path)
        content_issues = check_content_security(content) if content else []

        all_issues = path_issues + content_issues

        if all_issues:
            # 重大なセキュリティ問題の場合はブロック
            blocking_keywords = ["password", "secret", "key", "token", "private"]
            is_critical = any(
                any(keyword in issue.lower() for keyword in blocking_keywords)
                for issue in all_issues
            )

            if is_critical:
                # ブロック（exit code 2）
                error_msg = "🚨 SECURITY VIOLATION: Critical security issue detected\\n"
                error_msg += "\\n".join([f"  • {issue}" for issue in all_issues])
                error_msg += "\\n\\n💡 Please review and remove sensitive content before proceeding."
                print(error_msg, file=sys.stderr)
                sys.exit(2)
            else:
                # 警告のみ（継続）
                output = {"continue": True, "suppressOutput": False}

                warning_msg = "⚠️  Security Warning:\\n"
                warning_msg += "\\n".join([f"  • {issue}" for issue in all_issues])
                print(warning_msg)
                print(json.dumps(output), file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError as e:
        print(f"❌ Hook Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hook Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
