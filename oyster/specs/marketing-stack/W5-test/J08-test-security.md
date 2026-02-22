---
task_id: J08-test-security
project: marketing-stack
priority: 5
estimated_minutes: 25
depends_on: []
modifies: ["oyster/tests/e2e/test_security_audit.py"]
executor: glm
---
## 目标
Security audit: verify API keys in ~/.oyster-keys/, Docker containers on internal network, no public ports except reverse proxy, rate limiting on external APIs

## 约束
- Check 1: Scan codebase for hardcoded API keys
- Check 2: Verify Docker network config (no host mode)
- Check 3: Port scan localhost, verify only proxy exposed
- Check 4: Test rate limiting on external API calls
- Generate security report

## 验收标准
- [ ] test_security_audit.py created
- [ ] No hardcoded API keys found
- [ ] All Docker containers on internal network
- [ ] Only reverse proxy ports exposed
- [ ] Rate limiting verified on 5+ external APIs
- [ ] pytest test_security_audit.py passes
- [ ] Security report generated

## 不要做
- No penetration testing
- No credential rotation
- No network changes
