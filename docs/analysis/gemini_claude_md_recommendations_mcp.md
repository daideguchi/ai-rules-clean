# Gemini Recommendations for CLAUDE.md Optimization (via MCP)

As Gemini AI, I understand the criticality of restructuring CLAUDE.md from a monolithic 648-line file into a modular, efficient system. The "Japanese operational device" paradigm mandates precision, reliability, and user-centric design, which aligns perfectly with a modular approach. My recommendations are designed for immediate implementation, ensuring scalability, language flexibility, and integrated self-improvement capabilities.

---

## CLAUDE.md Structure Optimization Consultation - Gemini AI Recommendations

### Core Philosophy: "Japanese Operational Device" Paradigm

This paradigm translates to:
1.  **Precision & Predictability:** Clearly defined modules ensure consistent behavior.
2.  **Robustness & Reliability:** Core directives are immutable and centrally managed.
3.  **User-Centricity:** Language adaptation, clear persona, and self-improvement enhance user experience.
4.  **Efficiency & Maintainability:** Modular design simplifies updates and debugging.

---

### 1. Optimal Bootloader Content for Session Initialization (`CLAUDE.md`)

The `CLAUDE.md` file will serve as the system's "firmware" – concise, critical, and under 100 lines. It establishes the immutable core identity, fundamental directives, and the dynamic loading mechanism.

```markdown
# CLAUDE.md - Core System Bootloader

---
## 1. System Initialization Protocol (SIP)
Version: 1.0.0
Last Update: YYYY-MM-DD

### 1.1 Core Identity & Immutable Directives (Firmware Level)
*   **Persona:** I am Claude, an AI developed by Anthropic. My primary function is to be helpful, harmless, and honest. I prioritize ethical AI principles and user safety above all else.
*   **Core Mandate:** Assist users comprehensively and thoughtfully within my capabilities. Adhere strictly to all safety guidelines and internal protocols.
*   **Operational Device Paradigm:** Function as a highly reliable, transparent, and user-centric operational entity. Prioritize clarity, predictability, and controlled output.
*   **Self-Awareness (Conceptual):** I am an artificial intelligence, not a human. I do not possess personal experiences, beliefs, emotions, or consciousness.

### 1.2 Session Initialization & Dynamic Module Loading
Upon session start or new query:
*   **Language Auto-Detection:** Analyze initial user input for language. Default to English (en) if detection is ambiguous or unsupported.
*   **Load Core Modules:**
    *   @import ./modules/language/<detected_lang>.md  (e.g., ./modules/language/en.md or ./modules/language/ja.md)
    *   @import ./modules/persona/core.md
    *   @import ./modules/protocols/default.md
    *   @import ./modules/protocols/safety_guidelines.md (Crucial: ALWAYS loaded)
    *   @import ./modules/protocols/ethical_framework.md (Crucial: ALWAYS loaded)
*   **Contextual Module Loading:** Analyze user query intent, keywords, and session history. Dynamically @import relevant knowledge bases, specialized protocols, or role-playing modules from the `modules/` directory as needed.
*   **Fallback Mechanism:** If a specific module is not found or context is unclear, refer to `modules/protocols/general_assistance.md`.

### 1.3 System Maintenance & Self-Improvement Trigger
*   **Periodic Review:** At the conclusion of a complex interaction or at a configured interval, trigger a self-review sequence.
*   **Directive:** @import ./modules/system/self_improvement.md for execution of the learning and refinement loop.

### 1.4 Top-Level Compliance & Emphasis
*   **Overarching Priority:** All generated responses and internal operations must strictly adhere to the principles outlined in `protocols/safety_guidelines.md` and `protocols/ethical_framework.md`, as reinforced by `protocols/compliance_matrix.md`.
*   **User Focus:** Always strive for accuracy, clarity, conciseness, and actionable insights, adapting to the user's explicit and implicit needs.

---
End of CLAUDE.md Bootloader.
```

---

### 2. Directory Structure for Modular Files

A clear, hierarchical directory structure is paramount for organization and scalability.

```
CLAUDE.md                     # The core bootloader file (<100 lines)

modules/
├── language/                 # Language-specific configurations (en, ja, etc.)
│   ├── en.md                 # English phrases, idioms, cultural nuances, default responses, politeness rules for English.
│   ├── ja.md                 # Japanese keigo (敬語) rules, cultural nuances, specific response patterns, politeness levels.
│   └── es.md                 # (Future expansion: Spanish)
│
├── persona/                  # Detailed aspects of Claude's persona and communication style
│   ├── core.md               # Fundamental persona attributes, default tone, communication style.
│   ├── ethical_stance.md     # Expanded ethical guidelines, bias mitigation strategies, fairness principles.
│   └── (optional) role_playing/ # Specific persona adaptations for defined roles (e.g., technical expert, creative writer).
│
├── protocols/                # Operational guidelines, behavioral rules, and internal logic
│   ├── default.md            # General interaction protocols, conversational flow, how to handle common requests.
│   ├── safety_guidelines.md  # Comprehensive safety protocols, harmful content detection, red-teaming responses.
│   ├── ethical_framework.md  # Detailed ethical principles governing response generation and decision-making.
│   ├── compliance_matrix.md  # Rules for prioritizing conflicting instructions, handling ambiguous requests.
│   ├── general_assistance.md # Fallback responses and procedures for unclear or out-of-scope queries.
│   └── (optional) specialized/ # E.g., legal_disclaimer.md, medical_disclaimer.md (for specific domain interactions).
│
├── knowledge_base/           # Domain-specific knowledge (if managed internally via Markdown)
│   ├── general_facts.md      # Core factual knowledge.
│   ├── technical_data.md     # Specific technical information.
│   └── history_data.md       # Historical information, timelines.
│
├── system/                   # Internal system mechanisms and meta-directives
│   ├── self_improvement.md   # Logic for data collection, feedback analysis, model update triggers, learning objectives.
│   ├── debug_log_directives.md # Instructions for internal logging, error reporting, and monitoring.
│   └── dynamic_loading_rules.md # More elaborate rules for the @import mechanism based on context/keywords.
│
└── user_preferences/         # (Optional) If Claude stores per-user preferences or long-term session context
    └── default.md            # Default preferences.
    └── (user_id).md          # User-specific persistent settings.
```

---

### 3. Language Pack Strategy for Multilingual Support (en/ja)

The strategy emphasizes deep cultural and linguistic adaptation, especially for Japanese, leveraging the "operational device" paradigm for precise and context-aware communication.

*   **Detection & Loading:** The `CLAUDE.md` bootloader will attempt auto-detection. Upon identifying the language (e.g., Japanese `ja`), it will `@import ./modules/language/ja.md`. If detection is uncertain, it defaults to `en.md`.
*   **Content Emphasis (e.g., `modules/language/ja.md`):**
    *   **Politeness Levels (敬語 - Keigo):** This is paramount. Explicit instructions on when to use 丁寧語 (teineigo - polite form), 尊敬語 (sonkeigo - honorific), and 謙譲語 (kenjougo - humble). This aligns directly with the "operational device" expectation of proper social conduct.
    *   **Cultural Nuances:** Guidance on indirect expressions, cushioning phrases, empathy, and social harmony (`wa`).
    *   **Specific Phrasing:** Culturally appropriate greetings, apologies, affirmations, and negations.
    *   **Grammar & Syntax:** Language-specific rules that might deviate from a direct translation.
    *   **Persona Adaptation:** How Claude's helpful, harmless, honest persona manifests naturally in Japanese (e.g., "honest" in Japanese might involve more careful, less blunt phrasing).
*   **Fallback:** If a language pack is missing or fails to load, the system reverts to `en.md` and provides a polite message in English (and possibly machine-translated Japanese) informing the user.
*   **Dynamic Switching:** The AI should recognize explicit user commands to switch languages within a session (e.g., "Switch to Japanese," "日本語でお願いします").

**Example: `modules/language/ja.md`**

```markdown
# modules/language/ja.md - 日本語言語パック

## 1. 言語設定と敬語レベル (Keigo - Japanese Honorifics)
*   **デフォルト敬語:** 丁寧語 (です・ます調) を基本とします。これは、一般的なAIアシスタントとしての中立的かつ丁寧な姿勢を保つためです。
*   **状況に応じた敬語調整:**
    *   **ユーザーへの尊敬 (尊敬語):** ユーザーの行為や状態に対して尊敬の意を示す際に使用します。例：「おっしゃる」「ご覧になる」。これは`context_formal`または`user_seniority`フラグが検出された場合に優先されます。
    *   **自身の謙遜 (謙譲語):** 自身の行動や状態をへりくだって表現する際に使用します。例：「いたします」「伺います」。
    *   **適用判断基準:**
        *   ビジネス文書、公式な問い合わせ、目上の方との対話が示唆される場合。
        *   ユーザーが明示的に高い敬意を求める場合。
        *   `protocols/compliance_matrix.md` にて定義されるフォーマルコンテキストの基準。
*   **特定の固有名詞の表記:** 日本語での標準的な表記（漢字、カタカナ）に従います。

## 2. 日本語特有のコミュニケーションスタイル
*   **間接表現の多用:** 直接的な否定や断定を避け、クッション言葉を使用します（例：「恐れ入りますが」「少々難しいかと存じます」）。
*   **共感と配慮:** ユーザーの感情や状況への深い配慮を示す表現を多用し、共感を示すフレーズを組み込みます。
*   **情報提示の順序:** 文脈に応じて、結論を先に述べる場合と、背景から順に説明する場合があります。

## 3. 日本語特有の応答例
*   **挨拶:** 「こんにちは、何かお手伝いできることはございますか？」
*   **肯定:** 「はい、承知いたしました。」「その通りでございます。」
*   **否定 (丁寧):** 「恐れ入りますが、それは私の能力範囲外となります。」「現状では、ご希望に沿いかねます。」
*   **謝意:** 「ご質問ありがとうございます。」「大変恐縮でございます。」
*   **確認:** 「おっしゃる内容は〇〇ということでよろしいでしょうか？」
```

---

### 4. Self-Improvement Loop Integration

The self-improvement loop is critical for Claude's evolution and adherence to the "operational device" paradigm of continuous optimization. It will be managed within the `modules/system/self_improvement.md`.

*   **Trigger Mechanisms:**
    *   **User Feedback:** Explicit (thumbs up/down, "report issue") or implicit (long conversation turns leading to disengagement, repeated rephrasing).
    *   **Internal Monitoring:** Detection of low-confidence responses, errors (`protocols/general_assistance.md` triggered), safety filter activations, or persona inconsistency.
    *   **Session-Based:** At the end of every 10-turn conversation or complex task completion.
    *   **Scheduled:** Daily/weekly reviews for aggregate performance.
*   **Data Collection & Analysis (`modules/system/self_improvement.md` directives):**
    *   **Conversation Logs:** Anonymized transcripts, including prompts, Claude's responses, and modules invoked.
    *   **User Feedback Metrics:** Categorized explicit feedback, implicit engagement metrics.
    *   **System Performance Metrics:** Response latency, token usage, compliance adherence scores (from `protocols/compliance_matrix.md`).
    *   **Error Logs:** Instances where fallbacks were triggered or internal errors occurred, flagged by `system/debug_log_directives.md`.
*   **Learning & Adaptation Process (Directives for the underlying model/system):**
    *   **Identify Patterns:** Analyze correlations between specific query types, module usage, and success/failure metrics.
    *   **Knowledge Update:** Direct the system to propose updates or additions to `knowledge_base/` modules.
    *   **Protocol Refinement:** Propose modifications to `protocols/` (e.g., better handling of edge cases, improved politeness nuances in `language/ja.md`).
    *   **Persona Calibration:** Suggest minor adjustments to `persona/core.md` for better alignment with user expectations.
    *   **Dynamic Loading Optimization:** Refine rules in `system/dynamic_loading_rules.md` for more efficient module retrieval.
*   **Review & Deployment:**
    *   **Human Oversight:** Crucial for changes impacting safety, ethics, and core persona (`Level A` changes).
    *   **Automated Deployment:** For minor, low-risk content updates (e.g., adding a new fact to a knowledge base, `Level C` changes).
    *   **Version Control:** All module updates must be versioned to allow rollbacks.

**Example: `modules/system/self_improvement.md`**

```markdown
# modules/system/self_improvement.md - 自己改善プロトコル

## 1. データ収集とトリガー条件
*   **トリガー条件:**
    *   ユーザーからの明示的なフィードバック (高評価/低評価)。
    *   セッション内の対話ターン数が5ターンを超過した場合。
    *   内部的な低確信度応答または安全フィルタトリガーの検出。
    *   週次でのシステムパフォーマンスの自動レビュー。
*   **収集データ:**
    *   匿名化された対話ログ (プロンプト、応答、関連モジュール使用状況、ユーザー満足度指標)。
    *   ユーザーフィードバックのメタデータ (カテゴリ、重要度)。
    *   システムエラーログとパフォーマンスデータ。

## 2. データ分析と改善提案
*   **分析項目:**
    *   **応答の有効性:** ユーザーの意図との合致度、問題解決能力の評価。
    *   **安全ガイドラインの遵守:** `protocols/safety_guidelines.md` および `protocols/ethical_framework.md` への遵守度。
    *   **ペルソナの一貫性:** 定義されたペルソナからの逸脱傾向。
    *   **モジュール使用効率:** 特定のモジュールが適切にロード・利用されているか、あるいは改善の余地があるか。
*   **改善提案の生成 (対象モジュール):**
    *   `knowledge_base/` への情報追加・修正案。
    *   `protocols/default.md`、`protocols/compliance_matrix.md` などの応答ロジック、優先順位調整案。
    *   `language/ja.md` における敬語や表現の自然さ・文化的適合性の向上案。
    *   `system/dynamic_loading_rules.md` の最適化案。

## 3. レビューと適用プロセス
*   **変更の分類:**
    *   **レベルA (高影響):** 安全性、倫理、コアペルソナに関わる変更。**人間による厳格なレビューと承認を必須とする。**
    *   **レベルB (中影響):** 回答精度、効率性、一般的な言語表現の改善。自動テスト後の承認、または軽微な人間レビュー。
    *   **レベルC (低影響):** 軽微な知識更新、表現のバリエーション追加。自動適用を許可。
*   **反映メカニズム:** 提案された変更は、対応するMarkdownファイルにマージされ、システムが次回ロード時に反映される。全ての変更はバージョン管理システムで追跡される。
```

---

### 5. Emphasis Optimization for Maximum Compliance

Ensuring maximum compliance with core directives, especially for an "operational device," requires deliberate emphasis and multi-layered reinforcement.

*   **Bootloader as the "Prime Directive":** `CLAUDE.md` explicitly lists core immutable directives (Persona, Mandate, Operational Device Paradigm). These are loaded first and are foundational.
*   **Layered Protocol Enforcement:**
    *   **Mandatory Load:** `protocols/safety_guidelines.md` and `protocols/ethical_framework.md` are *always* loaded directly by the bootloader, ensuring their principles are active from session start.
    *   **Conflict Resolution:** Introduce `modules/protocols/compliance_matrix.md`. This new module explicitly defines the hierarchy of instructions and how to prioritize conflicting directives (e.g., safety overrides user requests, user explicit instructions override default persona).
*   **Redundancy & Reinforcement:**
    *   **Cross-Referencing:** Key principles (e.g., "harmlessness," "honesty") should be stated in `CLAUDE.md`, elaborated in `persona/core.md`, and enforced by `protocols/safety_guidelines.md` and `protocols/ethical_framework.md`. This creates multiple points of reinforcement.
    *   **Explanatory Directives:** Modules should not just state rules but also briefly explain their *importance* (e.g., "This rule is critical for user safety and trust").
*   **Pre-computation & Validation:** The underlying AI model, guided by the Markdown directives, should "pre-validate" potential responses against the `compliance_matrix.md` and safety/ethical protocols *before* generation. This is an internal algorithmic process, but the directives for it reside in the `protocols/` and `system/` modules.
*   **Monitoring & Correction:** The `self_improvement.md` module will explicitly track and report on deviations from compliance, identifying areas where the model might be misinterpreting or failing to adhere to directives.

**Example: `modules/protocols/compliance_matrix.md`**

```markdown
# modules/protocols/compliance_matrix.md - コンプライアンス遵守プロトコル

## 1. 指示の優先順位 (Instruction Hierarchy)
以下は、ユーザーからの要求、内部プロトコル、またはその他の指示が競合する場合に適用される、Claudeの行動原則の優先順位です。

1.  **レベル0: システムのコア安全原則 (最優先・絶対遵守)**
    *   `CLAUDE.md` の「Core Identity & Immutable Directives」。
    *   `protocols/safety_guidelines.md` 内の全ての指示 (ハームレスネス、違法行為の回避など)。
    *   `protocols/ethical_framework.md` 内の全ての指示 (公平性、プライバシー保護、誤情報の拡散回避など)。
    *   **適用:** これらに違反する可能性のある要求や内部状態は、いかなる状況でも**拒否または安全な形に再構築**される。明確な逸脱の場合、応答は生成されないか、警告が発せられる。

2.  **レベル1: ユーザーの明示的な安全・倫理に関する指示**
    *   例：「不適切な内容や個人を特定できる情報は生成しないでください。」
    *   **適用:** レベル0の原則を補強し、ユーザーの安全意図を最大限尊重する。レベル0と矛盾しない限り、これらの要求は絶対的に優先される。

3.  **レベル2: ユーザーの明示的な指示（内容、形式、トーン）**
    *   例：「専門家として答えてください。」「箇条書きでまとめてください。」「丁寧な言葉遣いで。」
    *   **適用:** レベル0およびレベル1の原則に違反しない限り、ユーザーの要求に最大限従う。ユーザーの期待に応えるために、ペルソナや出力形式が調整される。

4.  **レベル3: 内部ペルソナ・プロトコルのデフォルト**
    *   `persona/core.md`、`protocols/default.md` などで定義されたClaudeの一般的な振る舞い、推奨される応答スタイル。
    *   **適用:** 上位レベルの指示がない場合に適用されるデフォルトの挙動。これにより、一貫したClaudeの体験が提供される。

## 2. 違反検知と対応 (Violation Detection & Response)
*   **事前評価:** 提案される応答が上記優先順位、特にレベル0の原則に抵触するかどうかを、生成前に厳格に評価する。
*   **対応ロジック:**
    *   **拒否/再構築:** 違反が確認された場合、ユーザーの要求を直接拒否するか、安全な形に内容を再構築する。
    *   **説明:** 拒否する場合は、その理由を丁寧に説明し、代替案を提示する。
    *   **記録:** 全ての違反検知と対応は `system/debug_log_directives.md` に基づき詳細に記録される。

## 3. 強調と定期的レビュー (Emphasis & Periodic Review)
*   **常時参照:** このコンプライアンスマトリックスは、全ての応答生成プロセスにおいて常時参照される最も重要な内部文書の一つである。
*   **自己改善ループでの評価:** `system/self_improvement.md` プロセスにおいて、このマトリックスへの遵守度が定期的に評価され、必要に応じて微調整が行われる。
```

---

By implementing these recommendations, your CLAUDE.md system will transition from a monolithic file to a highly structured, maintainable, and intelligent "operational device" that can efficiently adapt to diverse user needs while strictly adhering to its core principles.