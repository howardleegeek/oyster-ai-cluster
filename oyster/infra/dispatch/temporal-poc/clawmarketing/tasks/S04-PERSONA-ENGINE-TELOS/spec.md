## 目标
重写 PersonaEngine.generate_reply() 方法，使用 TELOS 构建 system prompt

## 具体改动
1. 修改 PersonaEngine.generate_reply() 接受 brand_telos 参数
2. 实现 _build_system_prompt(telos) 方法，构建品牌人格 prompt
3. 在 generate_reply 的 prompt 中加入 brand_telos 信息:
   - mission
   - voice (tone, personality, taboos)
   - current goals
4. 使用 LLMRouter 生成真实回复

## 验收标准
- [ ] generate_reply() 不再返回空字符串或 placeholder
- [ ] prompt 包含 brand mission, voice, goals
- [ ] black backend/agents/persona_engine.py 检查通过

## 不要做
- 不动其他文件