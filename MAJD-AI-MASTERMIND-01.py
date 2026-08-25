    # ========================================================
    # GENERAL OWNER COMMAND - REAL AUTONOMOUS EXECUTION
    # ========================================================

    def _run_general_command(
        self,
        command: str,
        request: Dict[str, Any],
        state: MastermindState
    ) -> Dict[str, Any]:

        lowered = str(
            command or ""
        ).lower()

        repair_keywords = (
            "افحص",
            "فحص",
            "اصلح",
            "أصلح",
            "اصلاح",
            "إصلاح",
            "صحح",
            "تصحيح",
            "اختبر",
            "اختبار",
            "راجع",
            "مشاكل",
            "أخطاء",
            "اخطاء",
            "خطأ",
            "diagnose",
            "repair",
            "fix",
            "check",
            "test",
            "validate",
            "debug",
        )

        wants_repair = any(
            keyword in lowered
            for keyword in repair_keywords
        )

        # ----------------------------------------------------
        # FIRST INSPECTION
        # ----------------------------------------------------

        inspection = self.inspect_factory()

        state.events.append(
            {
                "time": utc_now(),
                "type": "GENERAL_INSPECTION",
                "data": inspection,
            }
        )

        self._save_state(
            state
        )

        self.logger.log(
            "GENERAL_OWNER_INSPECTION",
            inspection
        )

        # إذا كان الأمر ليس أمراً فنياً للفحص/الإصلاح
        if not wants_repair:

            return {
                "success": True,
                "status": "GENERAL_COMMAND_COMPLETED",
                "operation_id": self.operation_id,
                "command": command,
                "request": request,
                "factory": inspection,
                "message": (
                    "Owner command received and factory "
                    "inspection completed."
                ),
            }

        attempts: List[
            Dict[str, Any]
        ] = []

        last_failure: Optional[
            Dict[str, Any]
        ] = None

        # ----------------------------------------------------
        # AUTONOMOUS REPAIR LOOP
        # ----------------------------------------------------

        for attempt in range(
            1,
            self.max_repair_attempts + 1
        ):

            state.attempts = attempt

            state.status = (
                "GENERAL_AUTONOMOUS_REPAIR"
            )

            self._save_state(
                state
            )

            current_inspection = (
                self.inspect_factory()
            )

            python_report = (
                current_inspection.get(
                    "python_compile",
                    {}
                )
            )

            core_files = (
                current_inspection.get(
                    "core_files",
                    {}
                )
            )

            missing_core = []

            for number in (
                "01",
                "02",
                "03",
                "04",
                "06",
            ):

                item = (
                    core_files.get(
                        number,
                        {}
                    )
                )

                if not item.get(
                    "exists",
                    False
                ):

                    missing_core.append(
                        {
                            "number": number,
                            "file": item.get(
                                "file"
                            ),
                        }
                    )

            # ------------------------------------------------
            # SUCCESS CONDITION
            # ------------------------------------------------

            if (
                current_inspection.get(
                    "success"
                )
                and
                python_report.get(
                    "success"
                )
                and
                not missing_core
            ):

                final_verification = (
                    self.inspect_factory()
                )

                final_python = (
                    final_verification.get(
                        "python_compile",
                        {}
                    )
                )

                verified = bool(
                    final_verification.get(
                        "success"
                    )
                    and
                    final_python.get(
                        "success"
                    )
                )

                result = {
                    "success": verified,
                    "status": (
                        "GENERAL_REPAIR_COMPLETED"
                        if verified
                        else
                        "FINAL_VERIFICATION_FAILED"
                    ),
                    "operation_id":
                        self.operation_id,
                    "command":
                        command,
                    "request":
                        request,
                    "attempts":
                        attempts,
                    "factory":
                        final_verification,
                    "message": (
                        "Factory inspection and repair cycle "
                        "completed with final verification."
                    ),
                }

                self.logger.log(
                    "GENERAL_REPAIR_FINAL",
                    result
                )

                return result

            # ------------------------------------------------
            # BUILD FAILURE OBJECT
            # ------------------------------------------------

            if not python_report.get(
                "success",
                True
            ):

                last_failure = {
                    "stage":
                        "PYTHON_COMPILE",

                    "status":
                        "PYTHON_SYNTAX_ERROR",

                    "result":
                        python_report,
                }

            elif missing_core:

                last_failure = {
                    "stage":
                        "CORE_FILES",

                    "status":
                        "CORE_FILE_MISSING",

                    "missing":
                        missing_core,
                }

            else:

                last_failure = {
                    "stage":
                        "FACTORY_INSPECTION",

                    "status":
                        "FACTORY_INSPECTION_FAILED",

                    "result":
                        current_inspection,
                }

            self.logger.log(
                "GENERAL_REPAIR_FAILURE",
                {
                    "attempt":
                        attempt,

                    "failure":
                        last_failure,
                }
            )

            # ------------------------------------------------
            # DIAGNOSE
            # ------------------------------------------------

            diagnosis = (
                self.diagnostics
                .diagnose(
                    last_failure
                )
            )

            # فشل ملفات Python يجب اعتباره قابلاً للإصلاح
            if (
                last_failure.get(
                    "status"
                )
                ==
                "PYTHON_SYNTAX_ERROR"
            ):

                diagnosis = {
                    "type":
                        "PYTHON_SYNTAX_ERROR",

                    "repairable":
                        True,

                    "details":
                        json.dumps(
                            last_failure,
                            ensure_ascii=False,
                            default=str
                        )[-8000:],
                }

            # ------------------------------------------------
            # REPAIR
            # ------------------------------------------------

            repair = (
                self.repair_engine
                .repair(
                    diagnosis,
                    last_failure
                )
            )

            attempt_record = {
                "attempt":
                    attempt,

                "failure":
                    last_failure,

                "diagnosis":
                    diagnosis,

                "repair":
                    repair,
            }

            attempts.append(
                attempt_record
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "GENERAL_REPAIR_ATTEMPT",

                    "data":
                        attempt_record,
                }
            )

            self._save_state(
                state
            )

            self.logger.log(
                "GENERAL_REPAIR_ATTEMPT",
                attempt_record
            )

            # ------------------------------------------------
            # IMPORTANT:
            # PythonChecker وحده لا يصلح Syntax.
            # إذا لم يوجد Local AI فلا ندّعي نجاح الإصلاح.
            # ------------------------------------------------

            if (
                diagnosis.get(
                    "type"
                )
                ==
                "PYTHON_SYNTAX_ERROR"
                and
                not repair.get(
                    "success"
                )
            ):

                if not self.repair_engine.ai.available:

                    return {
                        "success": False,
                        "status":
                            "CODE_REPAIR_ENGINE_UNAVAILABLE",

                        "operation_id":
                            self.operation_id,

                        "command":
                            command,

                        "request":
                            request,

                        "failure":
                            last_failure,

                        "diagnosis":
                            diagnosis,

                        "repair":
                            repair,

                        "attempts":
                            attempts,

                        "message": (
                            "A real Python code error was "
                            "detected, but no configured code "
                            "generation engine is available. "
                            "No fake repair success was returned."
                        ),
                    }

            # ------------------------------------------------
            # RECHECK AFTER REPAIR
            # ------------------------------------------------

            recheck = (
                self.inspect_factory()
            )

            state.events.append(
                {
                    "time":
                        utc_now(),

                    "type":
                        "GENERAL_REPAIR_RECHECK",

                    "data":
                        recheck,
                }
            )

            self._save_state(
                state
            )

            recheck_python = (
                recheck.get(
                    "python_compile",
                    {}
                )
            )

            if (
                recheck.get(
                    "success"
                )
                and
                recheck_python.get(
                    "success"
                )
            ):

                return {
                    "success": True,
                    "status":
                        "GENERAL_REPAIR_COMPLETED",

                    "operation_id":
                        self.operation_id,

                    "command":
                        command,

                    "request":
                        request,

                    "attempt":
                        attempt,

                    "attempts":
                        attempts,

                    "factory":
                        recheck,

                    "message": (
                        "Factory repaired and verified "
                        "successfully."
                    ),
                }

            # إذا الإصلاح لم يغيّر شيئاً فلا نعلن نجاحاً
            if not repair.get(
                "success"
            ):

                last_failure = {
                    "stage":
                        "AUTONOMOUS_REPAIR",

                    "status":
                        repair.get(
                            "status",
                            "AUTONOMOUS_REPAIR_FAILED"
                        ),

                    "repair":
                        repair,

                    "recheck":
                        recheck,
                }

        # ----------------------------------------------------
        # MAX ATTEMPTS
        # ----------------------------------------------------

        final_inspection = (
            self.inspect_factory()
        )

        return {
            "success": False,

            "status":
                "MAX_AUTONOMOUS_REPAIR_ATTEMPTS_REACHED",

            "operation_id":
                self.operation_id,

            "command":
                command,

            "request":
                request,

            "attempts":
                attempts,

            "failure":
                last_failure,

            "factory":
                final_inspection,

            "message": (
                "Autonomous repair attempts were exhausted. "
                "No fake success was returned."
            ),
          }
