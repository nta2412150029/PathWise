PATHWISE — PRODUCT SPECIFICATION
1. Product Overview
PathWise is a data-driven career skill development platform that analyzes a student's current skill profile and target career to identify skill gaps and recommend which skills the student should learn next.
The core question of the product is:
“Given where I am now and where I want to go, what should I learn next?”
PathWise focuses on prioritizing skill development, rather than simply recommending courses or learning resources.
2. Target User
The primary users are university students who:
have a current set of technical and soft skills;
have one or more target career paths;
are uncertain about which skills to develop first;
have limited time for learning.
3. Core Product Flow
PathWise follows a closed-loop user journey:
Skill Profile → Career Goal → Skill Gap Analysis → Skill Prioritization → Next Skill Recommendation → Learning Roadmap → Profile Update
The system compares the user's current skill levels with the skill requirements of the selected career and converts the differences into actionable recommendations.
4. MVP Scope
The MVP will include the following core capabilities:
A. Skill Profile
 Users provide current skill levels using a simple 1–5 scale from Beginner to Expert.
B. Career Selection
 Users select a target career such as Business Analyst, Data Analyst, Marketing Analyst, Financial Analyst, or other predefined career profiles.
C. Skill Gap Analysis
 The system calculates the difference between the user's current level and the required level for the selected career.
D. Career Fit Score
 The system calculates an overall model-based compatibility indicator between the user's current profile and the selected career.
E. Skill Priority & Recommendation
 The system calculates a Skill Priority Score using factors such as skill gap, career importance, market demand, and strategic/prerequisite value, then recommends the next skill to learn.
F. Learning Roadmap
 The system presents a logical progression from the user's current state toward the target career, including prerequisites where relevant.
5. MVP Website Structure
The MVP will contain five main pages:
Dashboard
My Skills
Career Explorer
Skill Gap
Learning Roadmap
These pages represent the core user experience described in the project specification.
6. Data & Python Component
The system will work with structured data covering:
career skill requirements;
user skill levels;
skill importance;
skill prerequisites;
other attributes required by the recommendation model.
Python will be used for data processing, skill-gap analysis, scoring, similarity/recommendation logic, and related analysis rather than using AI only as a conversational interface.
7. Out of Scope for MVP
The following will not be required for the initial MVP:
advanced machine-learning prediction;
student clustering;
a large-scale personalized learning dataset;
complex recommendation models beyond the project's core scoring/recommendation logic;
advanced “What If?” simulation;
detailed time-constrained learning-plan optimization.
These features may be considered only after the core MVP is stable. The project specification explicitly describes the more advanced prediction/clustering components as future extensions and does not require Level 5 prediction for the MVP.
8. Required Project Deliverables
Ngay từ đầu nhóm phải coi 4 thứ dưới đây là bắt buộc và cùng thuộc một project, không phải làm website xong rồi mới nghĩ đến phần còn lại:
1. Website
A working PathWise MVP demonstrating the complete core user journey.
2. GitHub Code
A GitHub repository containing the project's source code and relevant project files.
3. Presentation Slides
Slides explaining the problem, product concept, data, methodology, Python analysis/recommendation logic, website, and results.
4. Presentation Video
A recorded presentation demonstrating the project and explaining its concept, implementation, and results.

