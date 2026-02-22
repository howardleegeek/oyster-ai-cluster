---
task_id: S063-main-cli-commands
project: marketing-stack
priority: 3
estimated_minutes: 20
depends_on: [S060-competitor-tracker, S061-ab-testing]
modifies: ["oyster/social/bluesky-poster/bluesky/__main__.py"]
executor: glm
---
## 目标
Add CLI commands to __main__.py: campaign (multi-platform), analytics (cross-platform stats), competitor (report), test (A/B test)

## 约束
- Commands: campaign, analytics, competitor, test
- campaign: trigger content across Twitter/Bluesky/LinkedIn
- analytics: show unified stats from PostHog/Plausible
- competitor: run CompetitorTracker.daily_digest()
- test: create/track/report A/B tests
- Use Click or argparse for CLI

## 验收标准
- [ ] __main__.py updated with 4 new commands
- [ ] python -m bluesky campaign --product <name> works
- [ ] python -m bluesky analytics shows stats
- [ ] python -m bluesky competitor shows report
- [ ] python -m bluesky test create/track/report works
- [ ] Help text clear for each command
- [ ] pytest tests for CLI pass

## 不要做
- No interactive prompts
- No TUI/GUI
- No config file changes
