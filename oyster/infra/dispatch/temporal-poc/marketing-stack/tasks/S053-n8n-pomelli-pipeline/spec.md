## 目标
Create n8n workflow: Pomelli asset download → store in Directus media library → schedule on Postiz for social posting

## 约束
- Use n8n HTTP Request to download Pomelli asset
- Upload to Directus Files collection
- Create Directus item with metadata
- Call Postiz API to schedule post
- Handle image/video assets

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Downloads asset from Pomelli URL
- [ ] Uploads to Directus media library
- [ ] Creates Directus item with asset reference
- [ ] Schedules on Postiz with asset
- [ ] Handles both images and videos
- [ ] Import to n8n instance successful

## 不要做
- Don't build Pomelli integration (use URLs)
- Don't add content generation
- Don't implement approval workflow yet