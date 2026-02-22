## 目标
Create email signup form for WorldGlasses landing page, connect to Listmonk list, welcome email template

## 约束
- React component: EmailSignup.tsx
- POST to Listmonk API
- List name: worldglasses-subscribers
- Double opt-in enabled
- Welcome email: product vision + waitlist info
- Source tag: landing_page

## 验收标准
- [ ] EmailSignup.tsx component created
- [ ] Form validates email
- [ ] Success confirmation displayed
- [ ] Subscriber added to Listmonk
- [ ] Welcome email sent
- [ ] Error handling works

## 不要做
- No developer API signup
- No pre-order system
- No device compatibility check