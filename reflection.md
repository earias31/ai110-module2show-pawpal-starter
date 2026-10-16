# PawPal+ Project Reflection

## 1. System Design

The user should be able to schedual tasks, input pet information, and deny suggested tasks.

**a. Initial design**

- Briefly describe your initial UML design.
- I included the Owner Class, Pet Class, and daily schedual. The owner stores
things like name and availible times. Daily scheudual has tasks a person can
mark as compleete and deny any tasks. The pet class stores the name and what 
it needs, etc.

**b. Design changes**

Added an optional pet association to each care task so the schedule can see which pet needs the care while still allowing household-wide tasks. Also added daily availability to `DailySchedule`, since time can vary day by day.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The scheduler considers tasks in time order and
keeps the earlier task when two timed tasks overlap, skipping the later one.
That means an earlier low-priority task can take precedence over a later
high-priority task, and the plan is not guaranteed to maximize the number of
tasks or total priority. It makes sure everything is done but it does make it fully optimal.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
