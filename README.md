<div align="left">
    <img src="https://github.com/user-attachments/assets/fb628d69-c0d2-4a34-8c3f-c9437871f132" style="height: 370px;">
</div>

This repository contains the data analysis scripts, charts, and final paper from my bachelor's thesis conducted at the University of Gothenburg. In this study, we explore and compare three approaches to evaluating student productivity in software development teams:

- <ins>**Baidu framework**</ins> – a metric-driven model focusing on quantitative data such as commits, lines of code, and code reviews.
- <ins>**SPACE framework**</ins> – a more holistic approach that incorporates factors like satisfaction, communication, task completion, and activity.
- <ins>**Self-perceived productivity**</ins> – collected through surveys and ratings provided by team members themselves.

The goal of this study was to analyze potential correlations and disparities between external productivity measurements and students' own perceptions of their contributions. Our findings aim to shed light on the alignment (or lack) between objective metrics and subjective experience within educational team-based development environments.

### Repository Structure
- `scripts/` # All Python scripts for data cleaning, scoring (Baidu/SPACE), and processing
- `charts-and-data/` # Visualizations and figures used in the thesis
- `thesis.pdf` # Final submitted thesis paper
- `README.md` # Current file

### Disclaimer
These analysis scripts were developed specifically for repositories exported from GitLab, which is the default version control system used in the course this thesis is based on. They rely on the structure and file format provided by a valid GitLab export, for example:
- `issues.ndjson`
- `merge_requests.ndjson`
- `project_members.ndjson`

Hence are not compatible with repositories from other platforms or with manually created data unless it follows the exact same schema.

---

### Data Analysis
To run the analysis scripts, ensure you have Python, Git, and Git Bash installed, along with the following Python packages:
- `pandas`, `numpy`, `scikit-learn`, `openpyxl`, `beautifulsoup4`, `gitstats`

1. Unzip the exported .tar.gz GitLab project file and navigate to the inner directory
   `<unzipped>/tree/project/`
2. Ensure the following files are present:
   - `issues.ndjson`
   - `merge_requests.ndjson`
   - `project_members.ndjson`
3. Place `extractData.py` and `createTable.py` inside that `tree/project` directory.
4. Open a terminal in the current directory and run `extractData.py` followed by `createTable.py` using `python <script>.py`

Running `extractData.py` will parse and clean the exported GitLab files, mapping author_ids to usernames using the data in project_members.ndjson, as well as dropping unneeded metadata such as 'lock_version' or 'merge_params'.

It will generate three CSV files: 
- `all_comments.csv` - which includes all comments and GitLab activity
- `cleaned_issues.csv` - which contains metadata for issues including authorship and edit history
- `cleaned_merge_requests.csv` - with equivalent information for merge requests.

Once these files are created, running `createTable.py` will analyze and compile all GitLab activity per contributor, including the number of system actions (such as status changes and assignments), comments written, issues assigned, and merge requests assigned. Creating the `contributions_table.xlsx`.

5. Navigate back to the root of the extracted GitLab export where the `project.bundle` file is located. Open a terminal here and run: `git clone project.bundle`
6. This will create a cloned project folder containing the full repository. Navigate into that folder, right-click inside the directory and select 'Git Bash Here' (found under 'More options' in Windows). In Git Bash, run: `gitstats . gitstats_output`
7. Place the `createStats.py` script inside the generated `gitstats_output` folder. Open a terminal in that directory and run: `python createStats.py`

This will produce the `gitstats_table.xlsx` file, which extracts and compiles only the LOC metrics per author while removing unnecessary sections such as author of the month and commits by domain.

---

### Table Aggregation

Once `contributions_table.xlsx` and `gitstats_table.xlsx`are generated, manually merge them into a single table before running the ranking scripts. Match each author_username to the corresponding Author in the gitstats table and copy over the Commits (%), + lines, and - lines columns into the contributions table. Add them beside the existing columns and ensure names are properly aligned. Save the final result as `final_table.xlsx`, which will be used as input for the ranking computations.

Your `final_table.xlsx` should look similar to:

![image](https://github.com/user-attachments/assets/a5f6c158-8e89-44d9-bf6e-b92fb28365a3)

---

### Baidu Framework Ranking

For Baidu scoring, place `rankBaidu.py` in the same directory as `final_table.xlsx` and run it using: `python rankBaidu.py`

This will print the rankings of all contributors, along with the normalized metrics used to compute the final score: `norm_commits`, `norm_lines`, `norm_reviews`, and the resulting `final_score`.

![baidu](https://github.com/user-attachments/assets/0c444735-b3a6-436f-b33d-a2550e840128)

### SPACE Framework Ranking

For the SPACE framework, since our study included a survey asking each contributor to rate their self-perceived productivity and satisfaction on a 1–5 scale (with 5 being the highest), the script requires these inputs. To replicate this, you should ask each contributor to provide their 1–5 ratings before running the script. Place `rankSpace.py` in the same directory as `final_table.xlsx` and run: `python rankSpace.py`

You will be prompted to enter the productivity and satisfaction scores for each listed contributor. The script will then output their rankings, along with their computed scores for task completion (task_completion), performance (P_score), activity (A_score), collaboration (C_score), and the final_score.

![image](https://github.com/user-attachments/assets/828ab4ba-7eb1-41e6-b1b8-1e4d8566bd90)

--- 

### Summary
The steps above outline how we completed the data analysis and scoring for each of the 6 student groups that participated in the study. For a full explanation of the formulas, weights, and normalization methods used in both the Baidu and SPACE frameworks, please refer to the Data Analysis section of our methodology in the thesis paper.

We also combined the results from all groups into a single table to identify how the most productive contributors rated themselves. This table, along with our survey questionnaire and the responses, can be found in the `charts-and-data/` folder, alongside other visualizations.

--- 

### Acknowledgement

We would like to express our gratitude to Cristy Martinez Montes for her guidance, support, and patience throughout the project. We are also thankful to the students who participated in our study for their time and input.

Authors
- Sam Hardingham - [LinkedIn](https://www.linkedin.com/in/SamHardingham)
- Daniel van den Heuvel - [LinkedIn](https://www.linkedin.com/in/danielvdh24/)
- Kai Rowley - [LinkedIn](https://www.linkedin.com/in/kai-rowley-7074b3257/)
- Cristy Martinez Montes - [LinkedIn](https://www.linkedin.com/in/cristina-martinez-montes/)
