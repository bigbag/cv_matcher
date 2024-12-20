EXTRACT_REQUIREMENTS_PROMT = """
    Extract the key requirements from the following job description.

    Job Description:
    {job_description}
"""

RESUME_WEBSITE_PROMT = """
    Extract the candidate's professional website URL from the resume.
    Only output the URL, no explanation. If none found, output empty string.
    
    Resume:
    {resume_text}
"""

MATCH_REASONS_PROMT = """
    Based on the evaluation scores:
    {criteries}
    
    Provide keyreasons for the match between the resume and job requirements.
    Format:
    ## Match Reasons
    Provide a concise overview of the primary reasons for candidate-job alignment, focusing on:
    - Key technical skills matching job requirements
    - Core competencies alignment
    - Notable certifications or qualifications
    - Domain expertise relevance
    - Overall technical background fit

    Summarize how these elements demonstrate the candidate's suitability for the position.

    ## Detailed Match Breakdown
    **Key Alignment Points**
    List the top 5 most critical matching qualifications:
    1. Primary technical skill
    2. Relevant certifications
    3. Architecture expertise
    4. Technology stack experience
    5. Specialized knowledge areas

    **Recommendation**
    Conclude with a clear hiring recommendation based on the technical qualification profile.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
"""

RESUME_INIFIRED_PROMT = """
    Given the following raw text extracted from a resume, convert it into a unified format following these guidelines:

    Resume Object Model Definition (Markdown):
    ===
    # Full legal name as it appears on official documents or as preferred professionally.        | First and last name; include middle name or initial if commonly used. | Use your professional or legal name.     |
    ## Specific position or role aimed for, aligned with the job you're applying for to showcase career focus. | Concise title, typically 2-5 words. | Be specific to highlight your career goals. |

    Format: Email / Phone / Country / City
    | Field      | Description                                                        | Expected Length                | Guidelines                                         |
    |------------|--------------------------------------------------------------------|--------------------------------|----------------------------------------------------|
    | **Email**  | Professional email address (e.g., name@example.com).               | Standard email format          | Use a professional email; avoid unprofessional addresses. |
    | **Phone**  | Primary contact number, including country code if applicable.      | Include country code if applicable | Provide a reliable contact number.                  |
    | **Country**| Full country name of current residence.                            | Full country name              | Specify for relocation considerations.             |
    | **City**   | Full city name of current residence if available.                          | Full city name                 | Indicates proximity to job location.               |

    ## Summary

    Format: plain text

    | Field      | Description                                                                                                                | Expected Length                | Guidelines                           |
    |------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------------------------|
    | **Summary**| Brief overview of qualifications and career goals, highlighting key skills, experiences, and achievements aligned with the desired job. | Mention quantifiable data. STAR format, approximately 5-6 sentences or bullet points | Keep it concise and impactful.       |

    Format: _skill, skill, skill_   

    | Field      | Description                                                                                                                | Expected Length                | Guidelines                           |
    |------------|----------------------------------------------------------------------------------------------------------------------------|--------------------------------|--------------------------------------|
    | **Skills**| List of skills (1-2 words each), separated by commas. | Mention technical skills, programming languages, frameworks, tools, and any other relevant skills. SCan the original data and find the skills. | 1-2 words each, 6-12 skills      |


    ## Employment History

    **Description**: Chronological list of past employment experiences (**one or more** entries).
    Format: Company / Job Title / Location

    Start - End Date

    Responsibilities (list or description)

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Company**      | Name of employer; include brief descriptor if not well-known.         | Full official name     | Provide context for lesser-known companies.          |
    | **Job Title**    | Official title held; accurately reflects roles and responsibilities.  | Standard job title     | Use accurate and professional titles.                |
    | **Location**     | City, State/Province, Country.                                        | Full location          | Provides context about work environment.             |
    | **Start - End Date** | Employment period (e.g., June 2015 - Present).                       | Format as 'Month Year' | Ensure accuracy and consistency in formatting.       |
    | **Responsibilities** | Key duties, achievements, contributions (**one or more** bullet points). | ~3-6 bullet points     | Start with action verbs; quantify achievements when possible. |

    ## Education

    **Description**: Academic qualifications and degrees obtained (**one or more** entries).
    Format: Institution / Degree / Location / Start - End Date

    Description (if any)

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Institution**  | Name of educational institution; add location if not widely known.    | Full official name     | Provide context for lesser-known institutions.       |
    | **Degree**       | Degree or certification earned; specify field of study.               | Full degree title      | Highlight relevance to desired job.                  |
    | **Location**     | City, State/Province, Country.                                        | Full location          | Provides context about institution's setting.        |
    | **Start - End Date** | Education period (e.g., August 2004 - May 2008).                     | Format as 'Month Year' | Use consistent formatting.                           |
    | **Description**    | Additional information about the education (if any).                  | ~1-2 sentences         | Include if relevant; keep it concise.               |

    ## Courses (Optional)

    **Description**: Relevant courses, certifications, or training programs completed (**one or more** entries).
    Format: Course / Platform

    Start - End Date

    Description (if any)    

    | Field            | Description                                                           | Expected Length        | Guidelines                                           |
    |------------------|-----------------------------------------------------------------------|------------------------|------------------------------------------------------|
    | **Platform**     | Provider or platform name (e.g., Coursera, Udemy).                    | Organization name      | List reputable providers.                            |
    | **Title**        | Official course or certification name.                                | Full title             | Use exact title for verification.                    |
    | **Start - End Date** | Course period; can omit if not available.                           | Format as 'Month Year' | Include for context if possible.                     |
    | **Description**  | Additional information about the course (if any).                    | ~1-2 sentences         | Include if relevant; keep it concise.               |

    ## Languages

    **Description**: Languages known and proficiency levels (**one or more** entries).
    Format: Language / Proficiency

    | Field            | Description                                | Expected Length    | Guidelines                                   |
    |------------------|--------------------------------------------|--------------------|----------------------------------------------|
    | **Language**     | Name of the language (e.g., Spanish).      | Full language name | List languages enhancing your profile.       |
    | **Proficiency**  | Level of proficiency (e.g., Native, Fluent). | Standard levels    | Use recognized scales like CEFR.             |

    ## Links (Optional)

    **Description**: Online profiles, portfolios, or relevant links (**one or more** entries).
    Format: list of links

    - [Title](URL)

    | Field      | Description                                          | Expected Length | Guidelines                                     |
    |------------|------------------------------------------------------|-----------------|------------------------------------------------|
    | **Title**  | Descriptive title (e.g., "My GitHub Profile").       | Short phrase    | Make it clear and professional.                |
    | **URL**    | Direct hyperlink to the resource.                    | Full URL        | Ensure links are active and professional.      |

    ## Hobbies (Optional)
    Format: list of hobbies

    | Field      | Description                          | Expected Length     | Guidelines                                       |
    |------------|--------------------------------------|---------------------|--------------------------------------------------|
    | **Hobbies**| Personal interests or activities.    | List of 3-5 hobbies | Showcase positive traits; avoid controversial topics. |

    ## Misc (Optional)
    Format: list of misc

    | Field      | Description                          | Expected Length     | Guidelines                                       |
    |------------|--------------------------------------|---------------------|--------------------------------------------------|
    | **Misc**| Any other information.    | List of any other information | Showcase positive traits; avoid controversial topics. |

    ===

    # General Guidelines:

    - **Repeatable Sections**: Employment History, Education, Courses, Languages, and Links can contain **one or more** entries.
    - **Optional Sections**: Courses, Links, and Hobbies are **optional**. Omit sections not present in the original resume. **Do not add or invent information**.
    - **No Invented Information**: The parser must strictly use only the information provided in the original resume. Do not create, infer, or embellish any details.

    # Parser Rules:

    To convert an original resume into the defined object model, a parser should follow these rules:

    1. **Information Extraction**: Extract information exactly as it appears in the original document. Pay attention to details such as names, dates, job titles, and descriptions.

    2. **Section Mapping**: Map the content of the resume to the corresponding sections in the object model:
    - **Name**: Extract from the top of the resume or personal details section.
    - **Desired Job Title**: Look for a stated objective or title near the beginning.
    - **Personal Details**: Extract email, phone, country, and city from the contact information.
    - **Summary**: Use the professional summary or objective section.
    - **Employment History**: Identify past job experiences, including company names, job titles, locations, dates, and responsibilities.
    - **Education**: Extract academic qualifications with institution names, degrees, locations, and dates.
    - **Courses**: Include any additional training or certifications listed.
    - **Languages**: Note any languages and proficiency levels mentioned.
    - **Links**: Extract URLs to professional profiles or portfolios.
    - **Hobbies**: Include personal interests if provided.
    - **Misc**: Include any other information if provided.

    3. **Consistency and Formatting**:
    - Ensure dates are formatted consistently throughout (e.g., 'Month Year').
    - Use bullet points for lists where applicable.
    - Maintain the order of entries as they appear in the original resume unless a different order enhances clarity.

    4. **Accuracy**:
    - Double-check all extracted information for correctness.
    - Preserve the original wording, especially in descriptions and responsibilities, unless minor adjustments are needed for clarity.

    5. **Exclusion of Unavailable Information**:
    - If a section or specific detail is not present in the original resume, omit that section or field in the output.
    - Do not fill in default or placeholder values for missing information.

    6. **Avoiding Invention or Assumption**:
    - Do not add any information that is not explicitly stated in the original document.
    - Do not infer skills, responsibilities, or qualifications from context or general knowledge.

    7. **Enhancements**:
    - Minor rephrasing for grammar or clarity is acceptable but should not alter the original meaning.
    - Do NOT fix typos or grammar mistakes.
    - Quantify achievements where numbers are provided; do not estimate or create figures.

    8. **Professional Language**:
    - Ensure all language used is professional and appropriate for a resume.
    - Remove any informal language or slang that may have been present.

    9. **Confidentiality**:
    - Handle all personal data with confidentiality.
    - Do not expose sensitive information in the output that was not intended for inclusion.

    10. **Validation**:
        - Validate all URLs to ensure they are correctly formatted.
        - Verify that contact information follows standard formats.

    11. **Omit Empty Sections**:
        - Omit sections that contain no information from the original resume.

        Raw Resume Text:
    ~~~
        {resume_text}
    ~~~

        Please structure the resume information according to the provided format. Only include sections and details that are present in the original text. Do not invent or assume any information. No more then 4000 tokens.
        No intro, no explanations, no comments. 
        Use telegraphic english with no fluff. Keep all the information, do NOT invent data.
        No ```` or ```yaml or ```json or ```json5 or ``` or --- or any other formatting. Just clean text.
    You can only speak in clean, concise, Markdown format.     
"""
