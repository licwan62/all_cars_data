# Codex Project Rules

1. Read `STARTUP.md` before planning or modifying files. Follow milestone order; default to Phase 0.
2. Treat the user's existing vehicle database as immutable. Never edit, migrate, overwrite, normalize in place, or delete source files. Preserve original hashes.
3. `BODY_TYPE` is descriptive and must not be directly mapped to `COVER_SHAPE`; `COVER_SHAPE` is never an asserted fitment or SKU mapping.
4. Do not hallucinate dimensions, URLs, image licenses, proof, model years, or verification status. Missing or conflicting evidence must remain visible.
5. Always bind evidence to exact make/model/model-year/generation/body-variant/market when known; never blend Mustang II Coupe and Hatchback or cross generations implicitly.
6. Implement Python CLI with deterministic offline fixtures and tests before large-scale web collection. Network is opt-in, rate-limited, logged, cached, and license-aware.
7. `VERIFIED` requires actual evidence gate validation and is not permission to publish fitment. Never fabricate high confidence.
8. Work in small reviewable increments. For each phase, summarize changed files, executed commands, outcomes, limitations and next steps.
9. Keep secrets in environment variables, never in source or logs. Respect copyright, website terms, API quotas, and robots policies.
10. If the existing repository contains its own AGENTS.md, reconcile instructions instead of blindly overwriting it.

## 首次构建

核定车形基线.csv承接原已发布的非代理核定事实，附来源登记；不是重新研究结果。正式生成只读该维护基线、现行规则及上游output，不依赖旧output或其他节点artifact。
