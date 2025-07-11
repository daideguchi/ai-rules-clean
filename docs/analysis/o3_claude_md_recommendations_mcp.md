# o3 Recommendations for CLAUDE.md Optimization (via MCP)

**1. Core CLAUDE.md Bootloader Contents (20-30 lines):**

The core `CLAUDE.md` file should be a minimal bootloader that initializes the system and imports essential modules. It should contain:

- **Version Information and Metadata:**
  - Specify the version, date, and any critical metadata.
- **Global Settings:**
  - Define global constants and configurations required for all modules.
- **Critical Instructions:**
  - Include any mandatory actions that must be performed before proceeding.
- **@import Statements:**
  - Import the next layer of modules (Essential layer).

*Example Core `CLAUDE.md` Structure:*

```markdown
# CLAUDE.md Core Bootloader

<!-- Version Information -->
Version: 1.0
Last Updated: YYYY-MM-DD

<!-- Global Settings -->
SET GLOBAL_MODE = "OPERATIONAL"
SET LANGUAGE = "EN"

<!-- Critical Instructions -->
**IMPORTANT:** YOU MUST read and follow all operational guidelines before proceeding.

<!-- Import Essential Modules -->
@import "essential_settings.md"
@import "essential_functions.md"
```

**2. Organizing the @import Hierarchy:**

Create a modular structure that follows the 4-layer architecture:

- **Layer 1: Core**
  - `CLAUDE.md` (bootloader)
    - Contains minimal code and imports Essential modules.
  
- **Layer 2: Essential**
  - `essential_settings.md`
    - Core configurations and settings.
  - `essential_functions.md`
    - Fundamental functions required across the system.
  - Imports Specific modules as necessary.

- **Layer 3: Specific**
  - `network_config.md`
    - Network-specific settings.
  - `user_management.md`
    - User roles and permissions.
  - `security_policies.md`
    - Security-related configurations.
  - Imports Reference modules if needed.

- **Layer 4: Reference**
  - `operational_guidelines.md`
    - Detailed operational procedures.
  - `command_reference.md`
    - List of all commands and their descriptions.
  - `troubleshooting.md`
    - Common issues and solutions.

*Import Hierarchy Flow:*

```plaintext
CLAUDE.md
│
├── @import "essential_settings.md"
│       ├── @import "network_config.md"
│       └── @import "user_management.md"
│
├── @import "essential_functions.md"
│       ├── @import "security_policies.md"
│       └── @import "operational_guidelines.md"
│               └── @import "command_reference.md"
│
```

**3. Critical Emphasis Placement (IMPORTANT/YOU MUST):**

- **Placement:**
  - At the beginning of each module where critical actions are required.
  - Before any code that has significant operational impact.

- **Formatting Guidelines:**
  - Use bold and uppercase for "IMPORTANT" and "YOU MUST".
  - Provide a brief but clear directive.

*Examples:*

```markdown
**IMPORTANT:** YOU MUST initialize the network settings before connecting devices.

**YOU MUST NOT** share your security credentials with unauthorized personnel.

**IMPORTANT:** Read `operational_guidelines.md` before performing system updates.
```

- **Consistency:**
  - Ensure the wording and formatting are consistent throughout all modules.
  - Use these statements sparingly to maintain their impact.

**4. Implementation Strategy for Migration:**

**Step 1: Analyze and Categorize Existing Content**

- **Review the 648-line `CLAUDE.md`:**
  - Break down the content into logical sections.
  - Categorize each section into Core, Essential, Specific, or Reference layers.
- **Create an Outline:**
  - Draft an outline mapping existing content to the new modular files.

**Step 2: Extract Core Bootloader Content**

- **Identify Core Elements:**
  - Select the most critical 20-30 lines needed to start the system.
  - Include version info, global settings, and essential imports.
- **Create the Core `CLAUDE.md` File:**
  - Implement the minimal bootloader as per the structure outlined above.

**Step 3: Create Essential Modules**

- **Essential Settings (`essential_settings.md`):**
  - Move global configurations and settings here.
- **Essential Functions (`essential_functions.md`):**
  - Include fundamental functions required by the system.
- **Add Critical Emphasis Statements:**
  - Place "IMPORTANT/YOU MUST" statements at the top of these modules where necessary.

**Step 4: Develop Specific Modules**

- **Create Modules for Specific Features:**
  - For example, `network_config.md`, `user_management.md`, `security_policies.md`.
- **Modularize Code:**
  - Ensure each module contains related functions and settings.
- **Import Dependencies:**
  - Use `@import` statements to include Reference modules if needed.

**Step 5: Assemble Reference Modules**

- **Operational Guidelines (`operational_guidelines.md`):**
  - Place detailed procedures and best practices here.
- **Command Reference (`command_reference.md`):**
  - Document all available commands and their usage.
- **Troubleshooting (`troubleshooting.md`):**
  - Provide solutions for common issues.

**Step 6: Update @import Statements**

- **Ensure Correct Hierarchy:**
  - Verify that all modules are imported in the correct order.
- **Resolve Dependencies:**
  - Check for any missing imports or circular dependencies.

**Step 7: Testing**

- **Module Testing:**
  - Test each module individually to ensure it functions correctly.
- **Integration Testing:**
  - Test the complete system by loading the Core `CLAUDE.md` file.
- **Validation:**
  - Confirm that all functionalities work as intended after modularization.

**Step 8: Deployment**

- **Backup Original File:**
  - Securely store the original `CLAUDE.md` before making changes.
- **Replace with Modular Structure:**
  - Deploy the new Core `CLAUDE.md` and place all modules in their designated locations.
- **Monitor System Performance:**
  - Observe the system for any errors or issues post-migration.

**Step 9: Documentation and Communication**

- **Update Documentation:**
  - Document the new modular structure and any changes in procedures.
- **Inform Stakeholders:**
  - Notify all relevant team members about the changes.
- **Provide Training:**
  - Offer guidance or training sessions if necessary.

**Additional Tips:**

- **Use Version Control:**
  - Implement a version control system (e.g., Git) to track changes throughout the migration process.
- **Adhere to Best Practices:**
  - Follow the Japanese concept of "operational device" by making operational instructions clear and accessible.
- **Maintain Readability:**
  - Keep modules concise and focused on single responsibilities.
- **Consistent Naming Conventions:**
  - Use clear, descriptive names for all modules to enhance maintainability.

---

By following these recommendations, you will achieve a modular, maintainable, and efficient `CLAUDE.md` structure that aligns with best practices and the desired 4-layer architecture.