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
tasks or total priority. It makes sure everything is done but it does make it not fully optimal.

---

## 3. AI Collaboration

**a. How you used AI**

- Brainstorming, problem solving, and explaining.
- The ones asking the ai to explain itself helped me undertsand more of what was going on.

**b. Judgment and verification**

- The first UML was needlessly complicated. I had to edit it a few times
- A lot of the verifying was done double checking the added and deleted files

---

## 4. Testing and Verification

**a. What you tested**

- Just standard uses of the app.
- If the app doesnt work, something has gone wrong. Simulating standard user use is important
to any project

**b. Confidence**

- Moderatly confident.
- Perhaps a lot of gibbarish or numbers past the bit limit.

---

## 5. Reflection

**a. What went well**

- Using the ai felt smooth and familiar.

**b. What you would improve**

- I cant tell exactly, but it feels bare. It feels like a project, which it is, but something
about it makes it seem primative. I would like to improve the app to be more polished, and improve
myself by figuring out what specifically caused this.

**c. Key takeaway**

- Ai is a tool, not the solution. You use a hammer to drive in nails, or a knife to cut food. 
You shouldnt try to use a hammer for a screw, or a knife on not food. Ai can be good and bad,
and it made me even more condifent that the future of coding isnt going to be replaced by ai, but
skilled coders using ai as another tool of theirs they can use.