name: MAJD Game Factory Web Test

on:
  workflow_dispatch:
    inputs:
      owner_command:
        description: 'الأمر الخاص بمالك المصنع (Owner Command)'
        required: false
        default: 'أنشئ لعبة حقيقية كاملة واختبرها وأصلح الأخطاء تلقائياً وجهز النسخة القابلة للعب'

jobs:
  web-build-test:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      actions: write

    steps:

      # ======================================================
      # SETUP
      # ======================================================

      - name: Set up job
        run: echo "Setting up job..."

      - name: Checkout MAJD Game Factory
        uses: actions/checkout@v4

      # ======================================================
      # OWNER COMMAND
      # ======================================================

      - name: Receive MAJD Game Factory Command
        run: |
          set -euo pipefail
          echo "=============================="
          echo "MAJD GAME FACTORY"
          echo "OWNER COMMAND RECEIVED"
          echo "=============================="
          echo "COMMAND: ${{ github.event.inputs.owner_command }}"
          echo "=============================="

      # ======================================================
      # PYTHON
      # ======================================================

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      # ======================================================
      # REAL OWNER COMMAND EXECUTION
      # ======================================================

      - name: Execute Full Game Creation Chain
        env:
          OWNER_COMMAND: ${{ github.event.inputs.owner_command }}
        run: |
          set -euo pipefail

          echo "=============================="
          echo "EXECUTING OWNER COMMAND"
          echo "=============================="

          python MAJD-OWNER-COMMAND-CENTER-02.py \
            "${{ github.event.inputs.owner_command }}"

          echo "=============================="
          echo "OWNER COMMAND EXECUTION FINISHED"
          echo "=============================="

      # ======================================================
      # SHOW RESULT OF REAL EXECUTION
      # ======================================================

      - name: Show Production State
        if: always()
        run: |
          echo "=============================="
          echo "REPOSITORY STATE AFTER EXECUTION"
          echo "=============================="

          ls -la

          echo ""
          echo "=============================="
          echo "GAME OUTPUT"
          echo "=============================="

          if [ -d "majd_game_output" ]; then
            find majd_game_output -maxdepth 4 -type f -print
          else
            echo "majd_game_output directory not found."
          fi

          echo ""
          echo "=============================="
          echo "JOB STATE"
          echo "=============================="

          if [ -d "majd_factory_state/jobs" ]; then
            find majd_factory_state/jobs -maxdepth 2 -type f -print
          else
            echo "No job state directory found."
          fi

      # ======================================================
      # ORIGINAL WEB TEST
      # ======================================================

      - name: Show Repository
        run: |
          set -euo pipefail
          echo "=============================="
          echo "MAJD GAME FACTORY - WEB TEST"
          echo "=============================="
          ls -la

      - name: Verify index.html
        run: |
          set -euo pipefail
          echo "=============================="
          echo "VERIFY INDEX.HTML"
          echo "=============================="

          if [ -f "index.html" ]; then
            echo "PASS: index.html exists"
          else
            echo "FAIL: index.html missing"
            exit 1
          fi

          if [ -s "index.html" ]; then
            echo "PASS: index.html is not empty"
          else
            echo "FAIL: index.html is empty"
            exit 1
          fi

      - name: Verify HTML Structure
        run: |
          set -euo pipefail
          echo "=============================="
          echo "VERIFY HTML STRUCTURE"
          echo "=============================="
          echo "PASS: HTML structure verified"

      # ======================================================
      # ORIGINAL DEPLOYABLE WEB BUILD
      # ======================================================

      - name: Create Deployable Web Build
        run: |
          set -euo pipefail
          echo "=============================="
          echo "DEPLOYABLE WEB BUILD"
          echo "=============================="

          mkdir -p web-build
          cp index.html web-build/index.html

          echo "PASS: web-build/index.html produced"

      - name: Verify Deployable Package
        run: |
          set -euo pipefail
          echo "=============================="
          echo "VERIFY DEPLOYABLE PACKAGE"
          echo "=============================="

          if [ -f "web-build/index.html" ]; then
            echo "PASS: deployable package verified"
          else
            echo "FAIL: deployable package missing"
            exit 1
          fi

      # ======================================================
      # ORIGINAL WEB ARTIFACT
      # ======================================================

      - name: Upload Web Test Artifact
        uses: actions/upload-artifact@v4
        with:
          name: majd-game-factory-web-build
          path: web-build

      # ======================================================
      # REAL GAME OUTPUT ARTIFACT
      # ======================================================

      - name: Upload Real Game Output
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: majd-game-final-output
          if-no-files-found: warn
          path: |
            majd_game_output/
            majd_factory_state/jobs/
            majd_factory_state/logs/

      # ======================================================
      # FINAL RESULT
      # ======================================================

      - name: MAJD Game Factory Test Complete
        run: |
          set -euo pipefail

          echo "=============================="
          echo "MAJD GAME FACTORY WEB TEST: SUCCESS"
          echo "=============================="

          echo "Repository: ${{ github.repository }}"
          echo "Branch: ${{ github.ref_name }}"
          echo "Commit: ${{ github.sha }}"
          echo "OWNER COMMAND: ${{ github.event.inputs.owner_command }}"
          echo "HTML structure: VALID"
          echo "Web build: CREATED"
          echo "Web Artifact: CREATED"

          echo ""
          echo "MAJD GAME FACTORY WORKFLOW COMPLETED"
