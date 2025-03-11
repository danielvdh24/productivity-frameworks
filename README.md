<div align="left">
    <img src="https://github.com/user-attachments/assets/c62890fa-5d4b-48d8-a7fa-9ca3516cc112" style="height: 370px;">
</div>

Using SPACE Framework for Small Development Teams
This guide represents our method of applying the SPACE framework to measure productivity in small software teams. It is not an official implementation but a structured approach that aligns closely with SPACE’s core principles and metrics.

While our methodology follows SPACE dimensions, the specific metrics, weighting, and ranking system can be modified to suit different team structures, goals, and project requirements.

### Step 1: Select Measurable Metrics for Student Teams

| **SPACE Dimension**       | **Selected Metrics** | **How to Measure** |
|--------------------------|---------------------------------|-----------------|
| Satisfaction | Self-reported productivity satisfaction | Survey: "On a scale of 1-5, how satisfied are you with your productivity this week?" |
| Performance | Number of successfully completed tasks | Count tasks marked as "Done" in project management tools (e.g., GitHub Issues, Trello) |
| Activity | Number of commits per student | Extract from GitHub/GitLab repository |
| Collaboration | Code review participation | Count number of comments made on merge requests/commits |
| Efficiency | Time spent actively coding | Use GitHub statistics or screen monitoring tools (if available) |

---

### Step 2: Normalize Metrics for Fair Comparison

Each metric needs to be converted to a standardized scale (e.g., 0-100) so that different types of data (survey responses vs. commits) can be compared fairly.  

- **Satisfaction (1-5 scale)** → Convert to percentage (e.g., 5 = 100%, 3 = 60%)  
- **Tasks Completed** → Normalize by the team average (e.g., if avg = 10 tasks, someone completing 12 tasks gets 120%)  
- **Commits** → Normalize by the highest contributor (e.g., if max is 30 commits, a student with 15 gets 50%)  
- **Code Review Comments** → Normalize using a similar relative approach 
- **Coding Time** → Normalize based on average hours spent per team member

**Formula:**  

$$\text{Normalized Score} = \left(\frac{\text{Individual Score}}{\text{Max or Avg Score in Team}}\right) \times 100$$  

---

### Step 3: Weight the Metrics (Optional)

Depending on research priorities, we can assign weights to different SPACE dimensions.  

Example **weighted scoring system**:
- **Satisfaction** → **10%**
- **Performance (Tasks Completed)** → **25%**
- **Activity (Commits)** → **20%**
- **Collaboration (Code Reviews)** → **25%**
- **Efficiency (Coding Time)** → **20%**

**Final score formula:**  

$$\text{Final Productivity Score} = (S \times 0.1) + (P \times 0.25) + (A \times 0.2) + (C \times 0.25) + (E \times 0.2)$$  

Where:
- **S** = Satisfaction Score
- **P** = Performance Score
- **A** = Activity Score
- **C** = Collaboration Score
- **E** = Efficiency Score

---

### Step 4: Rank Team Members Based on Final Score

Once we compute final scores for each student, we can rank them from highest to lowest.  

| **Student** | **Final Productivity Score (%)** | **Rank** |
|------------|-------------------------|------|
| Kai | 87% | 1st |
| Sam | 82% | 2nd |
| Daniel | 79% | 3rd |
