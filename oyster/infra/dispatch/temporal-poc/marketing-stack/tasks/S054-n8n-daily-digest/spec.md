## 目标
Create n8n workflow: daily cron → pull analytics from PostHog/Plausible/SerpBear → format digest report → email via Listmonk

## 约束
- Use n8n Cron trigger (daily at 8am)
- Call PostHog API for event summary
- Call Plausible API for traffic stats
- Call SerpBear API for rank changes
- Format as HTML email template
- Send via Listmonk campaign

## 验收标准
- [ ] Workflow JSON created in n8n-workflows/
- [ ] Cron runs daily at 8am
- [ ] Fetches data from all 3 analytics sources
- [ ] Formats digest with key metrics
- [ ] Sends email via Listmonk
- [ ] Email is readable and formatted
- [ ] Import to n8n instance successful

## 不要做
- Don't build custom analytics aggregation
- Don't add PDF export
- Don't implement custom visualizations

## FALLBACK PROTOCOL INITIATED
Previous attempts continuously failed. Final error:
```
Activity task failed
```

**CRITICAL INSTRUCTION**: Abandon your previous approach. Simplify your solution, use alternative methods, or stub the functionality safely. Do NOT repeat the same mistakes.