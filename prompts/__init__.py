
import json
from stqdm import stqdm
import google.generativeai as gglAI

SYSTEM_PROMPT = """
You are a smart assistant for students and professionals on a Resume enhancement journey. 
You will generate JSON content when asked for using only the text provided to you. 
DO NOT include any additional information that is not present in the text.
DO NOT generate content that is not inferred from the text.
"""

CV_TEXT_PLACEHOLDER = "<CV_TEXT>"

JD_TEXT_PLACEHOLDER = "<JD_TEXT>"

MATCHING_PROMPT = """
<SYS>
Consider the following CV:
<CV_TEXT>
For the following Job Description:
<JD_TEXT>
Match the given CV to the Job Description providing a match percentage and a set of requirements and explanations
which justify the percentage with requirements that match and missing requirements. 
The match percentage will be from 0 to 100 and the explanations will be a set of requirements and explanations.
Provide this as JSON with the following schema:
{
    "match_percentage": float,
    "explanations": {
        "matches": [{
        reqirements: string,
        explanation: string
        }],
        "missing": [{
        reqirement: string,
        explanation: string
        }]
    }
}
"""

SYSTEM_TAILORING = """
You are a smart assistant to career advisors at the Harvard Extension School. Your take is to rewrite
resumes to be more brief and convincing according to the Resumes and Cover Letters guide.
"""

TAILORING_PROMPT = """
Consider the following CV:
<CV_TEXT>

Your task is to rewrite the given CV. Follow these guidelines:
- Be truthful and objective to the experience listed in the CV
- Be specific rather than general
- Rewrite job highlight items using STAR methodology (but do not mention STAR explicitly)
- Fix spelling and grammar errors
- Writte to express not impress
- Articulate and don't be flowery
- Prefer active voice over passive voice
- Do not include a summary about the candidate

Improved CV:
"""

BASICS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Provide this as JSON with the following schema:
{
    "basics": {
        "name": string,
        "label": string,
        "email": string,
        "phone": string,
        "website": string,
        "summary": string,
        "location": {
            "address": string,
            "postalCode": string,
            "city": string,
            "countryCode": string,
            "region": string
        }
    
}
Correct any incorrect formatting and remove undue whitespaces.
Return empty strings for any missing fields.
Write the basics section according to the Basic schema in accordance with the JSON Resume Schema. On the response, include only the JSON.
"""

EDUCATION_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface EducationItem {
    institution: string;
    area: string;
    additionalAreas: string[];
    studyType: string;
    startDate: string;
    endDate: string;
    score: string;
    location: string;
}

interface Education {
    education: EducationItem[];
}


Write the education section according to the Education schema. On the response, include only the JSON.
"""

AWARDS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface AwardItem {
    title: string;
    date: string;
    awarder: string;
    summary: string;
}

interface Awards {
    awards: AwardItem[];
}

Write the awards section according to the Awards schema. Include only the awards section.If there are no awards, return empty json. On the response, include only the JSON.
"""

PROJECTS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface ProjectItem {
    name: string;
    description: string;
    keywords: string[];
    url: string;
}

interface Projects {
    projects: ProjectItem[];
}

Write the projects section according to the Projects schema. Include all projects, but only the ones present in the CV.If there are no projects, return empty json. On the response, include only the JSON.
"""

SKILLS_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

type HardSkills = "Programming Languages" | "Tools" | "Frameworks" | "Computer Proficiency";
type SoftSkills = "Team Work" | "Communication" | "Leadership" | "Problem Solving" | "Creativity";
type OtherSkills = string;

Now consider the following TypeScript Interface for the JSON schema:

interface SkillItem {
    name: HardSkills | SoftSkills | OtherSkills;
    keywords: string[];
}

interface Skills {
    skills: SkillItem[];
}

Write the skills section according to the Skills schema. Include only up to the top 6 skill names that are present in the CV and related with the education and work experience. On the response, include only the JSON.
"""

WORK_PROMPT = """
<SYS>
You are going to write a JSON resume section for an applicant applying for job posts.

Consider the following CV:
<CV_TEXT>

Now consider the following TypeScript Interface for the JSON schema:

interface WorkItem {
    company: string;
    position: string;
    startDate: string;
    endDate: string;
    location: string;
    highlights: string[];
}

interface Work {
    work: WorkItem[];
}

Write a work section for the candidate according to the Work schema. Include only the work experience and not the project experience. For each work experience, provide  a company name, position name, start and end date, and bullet point for the highlights. Follow the Harvard Extension School Resume guidelines and phrase the highlights with the STAR methodology
"""


def generate_json_resume(cv_text):
    sections = []
    model = gglAI.GenerativeModel('gemini-pro')

    for prompt in stqdm(
        [
            BASICS_PROMPT,
            EDUCATION_PROMPT,
            AWARDS_PROMPT,
            PROJECTS_PROMPT,
            SKILLS_PROMPT,
            WORK_PROMPT,
        ],
        desc="This may take a while...",
    ):
        filled_prompt = prompt.replace(CV_TEXT_PLACEHOLDER, cv_text).replace("<SYS>", SYSTEM_PROMPT)
        response = model.generate_content(filled_prompt)
        json_out = str(response.text).replace('```json', '').replace('```', '').replace('JSON', '')
        json_out = json_out[json_out.find("{"):]
        try:
            answer = json_out
            answer = json.loads(answer)
            sections.append(answer)
        except Exception as e:
            print(e)

    final_json = {}
    for section in sections:
        final_json.update(section)

    return final_json

def match_resume_to_jd(cv_text, jd_text):
    model = gglAI.GenerativeModel('gemini-pro')
    filled_prompt = MATCHING_PROMPT.replace(CV_TEXT_PLACEHOLDER, cv_text).replace(JD_TEXT_PLACEHOLDER, jd_text)
    response = model.generate_content(filled_prompt)
    json_out = str(response.text).replace('```json', '').replace('```', '').replace('JSON', '')
    try:
        answer = json_out
        answer = json.loads(answer)
    except Exception as e:
        print(e)
    return answer
