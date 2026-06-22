"""
resume_parser.py
Extracts structured data from PDF / DOCX / TXT resumes.
Priority: Gemini API (if GEMINI_API_KEY is set) → heuristic parser.
"""

import os
import re
import json
import urllib.request
import urllib.error


# ─────────────────────────────────────────────
#  File-text extraction helpers
# ─────────────────────────────────────────────

def get_pdf_text(filepath: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        return "\n".join(pages)
    except Exception as e:
        print(f"[resume_parser] PDF read error: {e}")
        return ""


def get_docx_text(filepath: str) -> str:
    try:
        import docx
        doc = docx.Document(filepath)
        parts = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if text:
                        parts.append(text)
        return "\n".join(parts)
    except Exception as e:
        print(f"[resume_parser] DOCX read error: {e}")
        return ""


def get_file_text(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return get_pdf_text(filepath)
    elif ext in (".docx", ".doc"):
        return get_docx_text(filepath)
    else:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"[resume_parser] text read error: {e}")
            return ""


# ─────────────────────────────────────────────
#  Section detection helpers
# ─────────────────────────────────────────────

# Map canonical section names → possible header variants
SECTION_HEADERS = {
    "personal":     ["objective", "summary", "profile", "about me", "career objective", "about", "introduction"],
    "skills":       ["skills", "technical skills", "core competencies", "key skills", "competencies",
                     "expertise", "technologies", "tech stack", "tools & technologies",
                     "skills & tools", "skills and technologies", "programming languages",
                     "other skills", "soft skills", "hard skills", "tools"],
    "experience":   ["experience", "work experience", "professional experience", "employment history",
                     "work history", "employment", "internship", "internships", "roles",
                     "career history"],
    "projects":     ["projects", "key projects", "personal projects", "academic projects",
                     "project details", "project work", "notable projects"],
    "education":    ["education", "educational background", "academic background",
                     "academic profile", "qualifications", "academic qualifications",
                     "scholastic achievements", "academics", "educational qualifications"],
    "certifications": ["certifications", "certificates", "courses", "training", "licenses",
                       "awards", "achievements", "accomplishments"],
    "activities":   ["extra-curricular", "extracurricular", "activities", "co-curricular",
                     "volunteer", "volunteer experience", "leadership", "interests", "hobbies"],
}

def _is_section_header(line: str, kinds: list) -> str | None:
    """Return canonical section name if line matches a section header, else None."""
    clean = line.lower().strip().rstrip(":")
    for kind in kinds:
        for hdr in SECTION_HEADERS.get(kind, []):
            if clean == hdr or clean == hdr + "s":
                return kind
    return None


def _split_into_sections(lines: list) -> dict:
    """
    Walk through lines and group them into named sections.
    Returns dict: {section_name: [lines]}.
    Unmatched lines at the top go into 'header'.
    """
    ALL_KINDS = list(SECTION_HEADERS.keys())
    sections = {"header": []}
    current_key = "header"

    for line in lines:
        matched = _is_section_header(line, ALL_KINDS)
        if matched:
            if matched not in sections:
                sections[matched] = []
            current_key = matched
        else:
            sections.setdefault(current_key, []).append(line)

    return sections


# ─────────────────────────────────────────────
#  Individual extraction functions
# ─────────────────────────────────────────────

def _extract_email(text: str) -> str:
    found = re.findall(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", text)
    return found[0] if found else ""


def _extract_phone(text: str) -> str:
    # Match 10-digit Indian numbers or international formats
    found = re.findall(
        r"(?:\+?91[\s\-]?)?(?:\+?1[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4,5}|\b\d{10}\b",
        text
    )
    # filter out years (4-digit numbers that are years)
    filtered = [p for p in found if not re.fullmatch(r"(19|20)\d{2}", p.replace(" ", "").replace("-", ""))]
    return filtered[0].strip() if filtered else ""


def _extract_name(header_lines: list, default_name: str) -> str:
    if default_name.strip():
        return default_name.strip()
    NOISE = {"resume", "cv", "curriculum vitae", "curriculum", "page", "contact",
             "email", "phone", "mobile", "profile", "objective", "skills",
             "experience", "education", "projects", "technical", "summary", "about"}
    for line in header_lines[:8]:
        clean = line.strip("•-*·| \t")
        if not clean or "@" in clean or len(clean) > 60:
            continue
        lower = clean.lower()
        if any(n in lower for n in NOISE):
            continue
        if re.search(r"\d", clean):
            continue
        words = clean.split()
        if 1 < len(words) <= 5:
            return clean
    return "Applicant"


def _extract_location(header_lines: list, all_text: str) -> str:
    LOCATION_PREFIXES = re.compile(
        r"(?i)^(address|location|city|lives in|resident of|residing at)\s*[:\-]?\s*"
    )
    for line in header_lines:
        m = LOCATION_PREFIXES.match(line)
        if m:
            return line[m.end():].strip()
    # Try to detect city/state mentions in the header area
    INDIAN_CITIES = [
        "delhi", "new delhi", "noida", "ghaziabad", "gurgaon", "gurugram",
        "meerut", "mumbai", "bangalore", "bengaluru", "hyderabad", "pune",
        "kolkata", "lucknow", "agra", "jaipur", "surat", "ahmedabad",
        "bhopal", "indore", "patna", "chandigarh", "dehradun", "uttarakhand",
        "uttar pradesh", "maharashtra", "rajasthan", "karnataka"
    ]
    for line in header_lines[:15]:
        if "@" in line or len(line) > 80:
            continue
        lower = line.lower()
        if any(city in lower for city in INDIAN_CITIES):
            return line.strip("•-*· \t")
    return ""


def _extract_summary(sections: dict) -> str:
    summary_lines = sections.get("personal", [])
    if summary_lines:
        # Filter out lines that are just contact info
        meaningful = [l for l in summary_lines if len(l) > 20 and "@" not in l and "http" not in l.lower()]
        if meaningful:
            return " ".join(meaningful[:4])
    # fall back to first long sentences in header
    header = sections.get("header", [])
    meaningful = [l for l in header if len(l) > 30 and "@" not in l and not re.fullmatch(r"[\d\s\+\-\(\)]+", l)]
    return " ".join(meaningful[:3])


def _extract_skills(sections: dict, full_text: str) -> list:
    """
    Collect skills ONLY from the skills section lines.
    If none found, fall back to scanning the full text but only for
    a curated list of verifiable technical / professional skills.
    """
    skill_lines = sections.get("skills", [])
    # Merge any additional certifications/tools sections that might carry skills
    for extra in ("certifications", "activities"):
        skill_lines = skill_lines + sections.get(extra, [])

    skills = []
    seen = set()

    def _add(s: str):
        s = s.strip("•-*·| \t ").strip()
        if s and len(s) >= 2 and len(s) <= 60:
            key = s.lower()
            if key not in seen:
                seen.add(key)
                skills.append(s)

    CATEGORY_PREFIXES = re.compile(
        r"(?i)^(technical|languages|frameworks|tools|databases|backend|frontend|"
        r"soft skills|hard skills|other|platforms|testing|devops|cloud|os|"
        r"programming)\s*[:\-]\s*"
    )

    for line in skill_lines:
        # Strip category label prefixes
        line = CATEGORY_PREFIXES.sub("", line).strip()
        # Split by common delimiters
        parts = re.split(r"[,|•\*;\t]+", line)
        for part in parts:
            p = part.strip("•-*·| \t ")
            if p:
                # Ignore very long strings (likely sentences)
                if len(p) > 55:
                    continue
                _add(p)

    # If we got a good skills list from the section, return it
    if len(skills) >= 3:
        return skills

    # ── Fallback: scan full text for a STRICT whitelist ──
    # Only add a skill if found explicitly in skills section lines OR very clearly in text
    TECHNICAL_SKILLS = [
        # Languages
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C",
        "Kotlin", "Swift", "Go", "Rust", "PHP", "Ruby", "Scala", "R",
        "MATLAB", "Dart", "Perl", "Shell", "Bash",
        # Web
        "HTML", "CSS", "React", "Angular", "Vue", "Next.js", "Node.js",
        "Express", "Django", "Flask", "FastAPI", "Spring Boot",
        "Bootstrap", "Tailwind", "jQuery", "REST API", "GraphQL",
        # Data / ML
        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
        "Machine Learning", "Deep Learning", "Data Analysis", "NLP",
        "Computer Vision", "Power BI", "Tableau",
        # DB
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Firebase",
        "Oracle", "SQL Server", "Cassandra",
        # DevOps / Cloud
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Linux",
        "Git", "GitHub", "GitLab", "CI/CD", "Jenkins",
        # Tools
        "Figma", "Photoshop", "Illustrator", "MS Office", "Excel",
        "AutoCAD", "Android Studio", "VS Code", "IntelliJ",
        # Professional / Soft
        "Teaching", "Communication", "Leadership", "Management",
        "Public Speaking", "Research", "Teamwork", "Problem Solving",
        "Event Planning", "Social Work", "Fundraising", "Counseling",
        "Coordination", "Community Organizing", "First Aid",
        "Translation", "Tutoring", "Content Writing", "Copywriting",
        "Digital Marketing", "SEO", "Graphic Design",
    ]

    text_lower = full_text.lower()
    for skill in TECHNICAL_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            _add(skill)

    return skills


def _parse_experience_section(lines: list) -> list:
    """Parse a list of experience/project lines into structured entries."""
    entries = []
    current = None

    # Patterns that hint at a new job/project entry
    YEAR_PAT = re.compile(r"\b(19|20)\d{2}\b")
    DATE_PAT = re.compile(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s,]*"
        r"(?:19|20)?\d{2,4}\b",
        re.IGNORECASE
    )
    DURATION_PAT = re.compile(
        r"\b(\d+)\s*(year|month|yr|mo)s?\b|\b(19|20)\d{2}\s*[-–—to]+\s*(?:(19|20)\d{2}|present|current|now)\b",
        re.IGNORECASE
    )

    ROLE_KEYWORDS = {
        "manager", "developer", "teacher", "engineer", "designer",
        "coordinator", "volunteer", "intern", "associate", "consultant",
        "officer", "executive", "lead", "analyst", "creator", "member",
        "founder", "head", "director", "researcher", "trainer", "instructor",
        "specialist", "supervisor", "assistant", "professor", "lecturer",
    }
    PROJECT_KEYWORDS = {
        "system", "app", "website", "platform", "model", "application",
        "game", "bot", "detector", "analyzer", "portal", "tool", "dashboard",
        "project", "module", "service", "api",
    }

    def _looks_like_title(line: str) -> bool:
        low = line.lower()
        if YEAR_PAT.search(line) or DATE_PAT.search(line) or DURATION_PAT.search(line):
            return True
        words = low.split()
        if any(kw in low for kw in ROLE_KEYWORDS) and len(line) < 120:
            return True
        if any(kw in low for kw in PROJECT_KEYWORDS) and len(line) < 120:
            return True
        return False

    def _flush():
        if current:
            entries.append(current)

    for line in lines:
        stripped = line.strip("•-*· \t").strip()
        if not stripped:
            continue

        yr_m = YEAR_PAT.search(line)
        dur_m = DURATION_PAT.search(line)

        if _looks_like_title(stripped):
            _flush()
            current = {
                "role": stripped if len(stripped) < 120 else stripped[:120],
                "company": "",
                "duration": dur_m.group(0) if dur_m else (yr_m.group(0) if yr_m else ""),
                "description": "",
            }
        elif current:
            # Possibly company name (short line after role with no description yet)
            if not current["company"] and len(stripped) < 100 and not stripped.startswith("-"):
                # Only treat as company if it looks like a name and not a sentence
                if len(stripped.split()) <= 8 and not stripped.endswith("."):
                    current["company"] = stripped
                    continue
            # Accumulate as description
            if current["description"]:
                current["description"] += "\n- " + stripped
            else:
                current["description"] = "- " + stripped
        else:
            # No current entry started yet – start a generic one
            current = {
                "role": stripped if len(stripped) < 120 else stripped[:120],
                "company": "",
                "duration": "",
                "description": "",
            }

    _flush()
    return entries


def _parse_education_section(lines: list) -> list:
    entries = []
    current = None

    DEGREE_KEYWORDS = [
        "B.Tech", "M.Tech", "B.Sc", "M.Sc", "B.A", "M.A", "MBA", "Ph.D",
        "B.Com", "M.Com", "B.E", "M.E", "BBA", "BCA", "MCA", "Diploma",
        "Btech", "Mtech", "Graduate", "Post Graduate", "Postgraduate",
        "Class X", "Class XII", "10th", "12th", "Secondary", "Intermediate",
        "Senior Secondary", "Higher Secondary", "Bachelor", "Master", "Doctoral",
    ]
    YEAR_PAT = re.compile(r"\b(19|20)\d{2}\b")
    INST_KEYWORDS = ["university", "college", "institute", "school", "iit", "nit",
                     "iiit", "academy", "polytechnic"]

    def _is_degree_line(line: str) -> bool:
        if any(kw.lower() in line.lower() for kw in DEGREE_KEYWORDS):
            return True
        if any(kw in line.lower() for kw in INST_KEYWORDS) and len(line) < 120:
            return True
        if YEAR_PAT.search(line) and len(line) < 120:
            return True
        return False

    def _flush():
        if current:
            entries.append(current)

    for line in lines:
        stripped = line.strip("•-*· \t").strip()
        if not stripped:
            continue

        yr_m = YEAR_PAT.search(stripped)

        if _is_degree_line(stripped):
            _flush()
            current = {
                "degree": stripped if len(stripped) < 120 else stripped[:120],
                "institution": "",
                "year": yr_m.group(0) if yr_m else "",
                "details": "",
            }
        elif current:
            if not current["institution"] and len(stripped) < 120:
                current["institution"] = stripped
            else:
                current["details"] = (current["details"] + " " + stripped).strip()
        else:
            current = {
                "degree": stripped if len(stripped) < 120 else stripped[:120],
                "institution": "",
                "year": yr_m.group(0) if yr_m else "",
                "details": "",
            }

    _flush()
    return entries


# ─────────────────────────────────────────────
#  Main heuristic extractor
# ─────────────────────────────────────────────

def extract_heuristics(text: str, default_name: str = "") -> dict:
    raw_lines = [l.strip() for l in text.split("\n") if l.strip()]
    sections = _split_into_sections(raw_lines)

    header_lines = sections.get("header", []) + sections.get("personal", [])

    name     = _extract_name(header_lines, default_name)
    email    = _extract_email(text)
    phone    = _extract_phone(text)
    location = _extract_location(header_lines, text)
    summary  = _extract_summary(sections)

    skills    = _extract_skills(sections, text)

    exp_lines  = sections.get("experience", []) + sections.get("projects", [])
    professional = _parse_experience_section(exp_lines)

    edu_lines = sections.get("education", [])
    education = _parse_education_section(edu_lines)

    return {
        "personal": {
            "name":     name,
            "email":    email,
            "phone":    phone,
            "location": location,
            "summary":  summary,
        },
        "professional": professional,
        "education":    education,
        "skills":       skills,
    }


# ─────────────────────────────────────────────
#  Gemini API fallback
# ─────────────────────────────────────────────

def analyze_with_gemini(text: str, api_key: str) -> dict | None:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-1.5-flash:generateContent?key={api_key}"
    )
    prompt = (
        "You are an expert resume parser. Extract structured information from the resume below. "
        "Reply ONLY with a single valid JSON object – no markdown, no code fences, no extra text.\n"
        "The JSON must have these exact keys:\n"
        "  personal:     { name, email, phone, location, summary }\n"
        "  professional: [ { role, company, duration, description } ]\n"
        "  education:    [ { degree, institution, year, details } ]\n"
        "  skills:       [ string ]   ← ONLY skills explicitly mentioned in the resume\n\n"
        f"Resume:\n{text[:8000]}"
    )

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            raw = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw)
    except Exception as e:
        print(f"[resume_parser] Gemini API error: {e}")
        return None


# ─────────────────────────────────────────────
#  Public entry point
# ─────────────────────────────────────────────

def parse_resume(filepath: str, default_name: str = "") -> dict:
    text = get_file_text(filepath)
    if not text.strip():
        return {
            "personal":     {"name": default_name, "email": "", "phone": "", "location": "",
                             "summary": "No readable text found in the uploaded file."},
            "professional": [],
            "education":    [],
            "skills":       [],
        }

    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        result = analyze_with_gemini(text, api_key)
        if result:
            return result

    return extract_heuristics(text, default_name)
