## 目标
Deploy ALwrity AI content generation with multi-LLM (OpenAI/Anthropic/Gemini), blog post + social media pipelines, EN/ZH support, SEO optimization

## 约束
- API keys in ~/.oyster-keys/
- Pipelines: blog_post, social_post, newsletter
- Languages: EN, ZH
- SEO: auto meta tags, keyword optimization
- Output: markdown + frontmatter
- CLI wrapper: alwrity_wrapper.py

## 验收标准
- [ ] ALwrity installed and configured
- [ ] All 3 LLM APIs working
- [ ] Blog post generation works (EN/ZH)
- [ ] Social media content generation works
- [ ] SEO metadata included in output
- [ ] alwrity_wrapper.py CLI functional
- [ ] pytest tests for wrapper pass

## 不要做
- No auto-publishing yet
- No image generation
- No WordPress integration