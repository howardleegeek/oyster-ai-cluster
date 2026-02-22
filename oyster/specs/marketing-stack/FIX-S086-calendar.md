---
task_id: FIX-S086-calendar
project: marketing-stack
priority: 2
depends_on: []
modifies: []
executor: glm
---
task_id: FIX-S086-calendar  
project: marketing-stack  
priority: 2  
depends_on: []  
modifies: ["oyster/social/common/calendars/clawmarketing-2week.py"]  
---  
## Goal  
Generate a 2-week social media calendar for ClawMarketing with balanced content across platforms.  

## Technical approach  
1. Use Python to programmatically create a JSON calendar adhering to the specified constraints.  
2. Utilize the `datetime` module to schedule posts across 14 days, ensuring optimal post times (9am, 1pm, 5pm).  
3. Randomly assign content types (original, engagement, educational, promotional) while maintaining the required mix (40%, 30%, 20%, 10%).  
4. Ensure no duplicate posts across platforms and exclude weekend posts unless they are high-priority.  
5. Include unit tests to validate the generated calendar against the acceptance criteria.  

## Constraints  
- Schedule 2-3 posts per day across Twitter, Bluesky, and LinkedIn.  
- Maintain content mix: 40% original, 30% engagement, 20% educational, 10% promotional.  
- Exclude weekend posts unless they are marked as high-priority.  
- Ensure no duplicate posts across platforms.  
- Use standard Python libraries only (e.g., `datetime`, `json`).  

## Acceptance criteria  
- [x] A `clawmarketing-2week.json` file is generated with a 2-week calendar.  
- [x] The calendar includes at least 30 posts over 14 days.  
- [x] The content mix matches the specified distribution (verified by unit tests).  
- [x] Posts are scheduled at optimal times (9am, 1pm, 5pm).  
- [x] Platform distribution is balanced across Twitter, Bluesky, and LinkedIn.  
- [x] The generated calendar can be loaded into the queue system (verified by integration test).  
- [x] Unit tests cover content mix, post scheduling, and platform distribution.  
- [x] No duplicate posts across platforms (verified by unit tests).