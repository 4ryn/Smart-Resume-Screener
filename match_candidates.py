import sqlite3
import ollama
from config import OLLAMA_MODEL, DB_PATH
import numpy as np
import json
from typing import Dict, List, Tuple

def extract_skills_from_cv(cv_text):
    """Extract skills and experience using LLM with JSON output."""
    prompt = f"""You are an expert CV analyzer. Analyze this CV and extract information.

CV TEXT:
{cv_text}

You MUST respond with ONLY a valid JSON object in this exact format (no other text):
{{
  "technical_skills": ["Python", "SQL", "Machine Learning"],
  "soft_skills": ["Leadership", "Communication"],
  "domain_skills": ["Data Science", "Finance"],
  "experience_years": 5,
  "keywords": ["Python", "Data Analysis", "ML", "SQL", "ETL"]
}}

Rules:
- Include 5-15 technical skills
- Include 3-8 soft skills
- Include 2-5 domain/industry skills
- Experience in years as a number
- Include 10-20 important keywords from CV
- Return ONLY the JSON, no extra text

Extract the information now:"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL, 
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 800}
        )
        llm_output = response["message"]["content"].strip()
        
        # Try to extract JSON if LLM adds extra text
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            llm_output = llm_output[json_start:json_end]
        
        return llm_output
    except Exception as e:
        print(f"❌ LLM error extracting CV: {e}")
        return '{}'

def parse_cv_extraction(llm_response):
    """Parse LLM JSON response into structured format."""
    info = {
        "skills": [],
        "experience_years": 0,
        "keywords": [],
        "raw_text": llm_response
    }
    
    try:
        # Try to parse as JSON first
        data = json.loads(llm_response)
        
        # Extract all skills
        technical = data.get("technical_skills", [])
        soft = data.get("soft_skills", [])
        domain = data.get("domain_skills", [])
        
        # Combine all skills
        all_skills = []
        if isinstance(technical, list):
            all_skills.extend(technical)
        if isinstance(soft, list):
            all_skills.extend(soft)
        if isinstance(domain, list):
            all_skills.extend(domain)
        
        # Clean and deduplicate skills
        seen = set()
        for skill in all_skills:
            if isinstance(skill, str):
                skill = skill.strip()
                skill_lower = skill.lower()
                if skill and skill_lower not in seen and skill_lower not in ['none', 'n/a', 'not specified']:
                    seen.add(skill_lower)
                    info["skills"].append(skill)
        
        # Extract experience years
        exp = data.get("experience_years", 0)
        if isinstance(exp, (int, float)):
            info["experience_years"] = float(exp)
        elif isinstance(exp, str):
            try:
                info["experience_years"] = float(exp)
            except:
                info["experience_years"] = 0
        
        # Extract keywords
        keywords = data.get("keywords", [])
        if isinstance(keywords, list):
            seen_kw = set()
            for kw in keywords:
                if isinstance(kw, str):
                    kw = kw.strip()
                    kw_lower = kw.lower()
                    if kw and kw_lower not in seen_kw and kw_lower not in ['none', 'n/a', 'not specified']:
                        seen_kw.add(kw_lower)
                        info["keywords"].append(kw)
        
        print(f"    ✓ JSON parsed: {len(info['skills'])} skills, {info['experience_years']} years, {len(info['keywords'])} keywords")
        return info
        
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse failed, using LLM fallback: {e}")
        # Fallback: Use LLM to extract from the response
        return parse_cv_with_llm_fallback(llm_response)

def parse_cv_with_llm_fallback(llm_response):
    """Use LLM to parse its own response if JSON fails."""
    prompt = f"""The following is a response that should contain CV information. Extract the data and return ONLY a valid JSON:

RESPONSE:
{llm_response}

Return ONLY this JSON structure:
{{
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "keywords": ["keyword1", "keyword2"]
}}"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 500}
        )
        fallback_output = response["message"]["content"].strip()
        
        # Extract JSON
        json_start = fallback_output.find('{')
        json_end = fallback_output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            fallback_output = fallback_output[json_start:json_end]
        
        data = json.loads(fallback_output)
        
        info = {
            "skills": data.get("skills", []),
            "experience_years": float(data.get("experience_years", 0)),
            "keywords": data.get("keywords", []),
            "raw_text": llm_response
        }
        
        print(f"    ✓ Fallback parsed: {len(info['skills'])} skills, {info['experience_years']} years")
        return info
        
    except Exception as e:
        print(f"    ❌ Fallback failed: {e}")
        return {
            "skills": [],
            "experience_years": 0,
            "keywords": [],
            "raw_text": llm_response
        }

def extract_jd_requirements(jd_summary):
    """Extract requirements from job description using LLM with JSON output."""
    prompt = f"""You are an expert job requirement analyzer. Analyze this job description and extract requirements.

JOB DESCRIPTION:
{jd_summary}

You MUST respond with ONLY a valid JSON object in this exact format (no other text):
{{
  "required_skills": ["Python", "SQL", "Communication"],
  "preferred_skills": ["Machine Learning", "Cloud"],
  "min_experience": 3,
  "keywords": ["Python", "Data", "Analysis", "SQL", "Team"]
}}

Rules:
- required_skills: Must-have skills (5-10 items)
- preferred_skills: Nice-to-have skills (3-8 items)
- min_experience: Minimum years as a number (default 0)
- keywords: 10-20 important terms from job description
- Return ONLY the JSON, no extra text

Extract the requirements now:"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 800}
        )
        llm_output = response["message"]["content"].strip()
        
        # Extract JSON if LLM adds extra text
        json_start = llm_output.find('{')
        json_end = llm_output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            llm_output = llm_output[json_start:json_end]
        
        return llm_output
    except Exception as e:
        print(f"❌ LLM error extracting JD: {e}")
        return '{}'

def parse_jd_extraction(llm_response):
    """Parse JD JSON response into structured format."""
    info = {
        "required_skills": [],
        "preferred_skills": [],
        "min_experience": 0,
        "keywords": [],
        "raw_text": llm_response
    }
    
    try:
        # Parse JSON
        data = json.loads(llm_response)
        
        # Extract required skills
        required = data.get("required_skills", [])
        if isinstance(required, list):
            seen = set()
            for skill in required:
                if isinstance(skill, str):
                    skill = skill.strip()
                    skill_lower = skill.lower()
                    if skill and skill_lower not in seen and skill_lower not in ['none', 'n/a', 'not specified']:
                        seen.add(skill_lower)
                        info["required_skills"].append(skill)
        
        # Extract preferred skills
        preferred = data.get("preferred_skills", [])
        if isinstance(preferred, list):
            seen = set()
            for skill in preferred:
                if isinstance(skill, str):
                    skill = skill.strip()
                    skill_lower = skill.lower()
                    if skill and skill_lower not in seen and skill_lower not in ['none', 'n/a', 'not specified']:
                        seen.add(skill_lower)
                        info["preferred_skills"].append(skill)
        
        # Extract minimum experience
        exp = data.get("min_experience", 0)
        if isinstance(exp, (int, float)):
            info["min_experience"] = float(exp)
        elif isinstance(exp, str):
            try:
                info["min_experience"] = float(exp)
            except:
                info["min_experience"] = 0
        
        # Extract keywords
        keywords = data.get("keywords", [])
        if isinstance(keywords, list):
            seen_kw = set()
            for kw in keywords:
                if isinstance(kw, str):
                    kw = kw.strip()
                    kw_lower = kw.lower()
                    if kw and kw_lower not in seen_kw and kw_lower not in ['none', 'n/a', 'not specified']:
                        seen_kw.add(kw_lower)
                        info["keywords"].append(kw)
        
        return info
        
    except json.JSONDecodeError:
        print(f"    ⚠️  JD JSON parse failed, using LLM fallback")
        return parse_jd_with_llm_fallback(llm_response)

def parse_jd_with_llm_fallback(llm_response):
    """Use LLM to parse JD response if JSON fails."""
    prompt = f"""The following is a response about job requirements. Extract the data and return ONLY valid JSON:

RESPONSE:
{llm_response}

Return ONLY this JSON structure:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill3"],
  "min_experience": 0,
  "keywords": ["keyword1", "keyword2"]
}}"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 500}
        )
        fallback_output = response["message"]["content"].strip()
        
        # Extract JSON
        json_start = fallback_output.find('{')
        json_end = fallback_output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            fallback_output = fallback_output[json_start:json_end]
        
        data = json.loads(fallback_output)
        
        return {
            "required_skills": data.get("required_skills", []),
            "preferred_skills": data.get("preferred_skills", []),
            "min_experience": float(data.get("min_experience", 0)),
            "keywords": data.get("keywords", []),
            "raw_text": llm_response
        }
        
    except Exception as e:
        print(f"    ❌ JD fallback failed: {e}")
        return {
            "required_skills": [],
            "preferred_skills": [],
            "min_experience": 0,
            "keywords": [],
            "raw_text": llm_response
        }

def get_embedding(text):
    """Safely get embedding from Ollama with retry logic."""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            # Limit text length for embedding
            text_limited = text[:3000] if len(text) > 3000 else text
            result = ollama.embeddings(model=OLLAMA_MODEL, prompt=text_limited)
            embedding = np.array(result["embedding"])
            if embedding.size > 0:
                return embedding
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"⚠️  Embedding failed: {e}")
                return np.zeros(4096)
    return np.zeros(4096)

def cosine_similarity(a, b):
    """Computes cosine similarity between two numpy vectors with safety checks."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = np.dot(a, b) / (norm_a * norm_b)
    return float(np.clip(similarity, -1.0, 1.0))

def compute_keyword_overlap(cv_keywords, jd_keywords):
    """Compute keyword overlap score using Jaccard similarity."""
    if not cv_keywords or not jd_keywords:
        return 0.0
    
    cv_set = set(k.lower().strip() for k in cv_keywords)
    jd_set = set(k.lower().strip() for k in jd_keywords)
    
    intersection = cv_set.intersection(jd_set)
    union = cv_set.union(jd_set)
    
    if not union:
        return 0.0
    
    jaccard = len(intersection) / len(union)
    
    # Also compute coverage (how many JD keywords are in CV)
    if jd_set:
        coverage = len(intersection) / len(jd_set)
        # Weighted: 60% coverage, 40% jaccard
        return (coverage * 0.6) + (jaccard * 0.4)
    
    return jaccard

def compute_skill_match(cv_skills, required_skills, preferred_skills):
    """Compute skill match scores with fuzzy matching using LLM."""
    if not cv_skills:
        return 0.0, 0.0
    
    # Required skills match
    required_match = 0.0
    if required_skills:
        required_match = compute_skill_similarity_with_llm(cv_skills, required_skills)
    
    # Preferred skills match
    preferred_match = 0.0
    if preferred_skills:
        preferred_match = compute_skill_similarity_with_llm(cv_skills, preferred_skills)
    
    return required_match, preferred_match

def compute_skill_similarity_with_llm(cv_skills, required_skills):
    """Use LLM to intelligently match skills."""
    prompt = f"""You are a skills matching expert. Compare the candidate's skills with required skills.

CANDIDATE SKILLS:
{', '.join(cv_skills[:20])}

REQUIRED SKILLS:
{', '.join(required_skills)}

For each required skill, determine if the candidate has it or an equivalent skill.
Consider:
- Exact matches (Python = Python)
- Variations (Python Programming = Python)
- Related skills (PyTorch could match Machine Learning)
- Synonyms (JavaScript = JS)

Return ONLY a JSON with the match score:
{{
  "matches": 5,
  "total_required": 10,
  "match_percentage": 50.0
}}

The match_percentage should be: (matches / total_required) * 100"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2, "num_predict": 200}
        )
        
        output = response["message"]["content"].strip()
        
        # Extract JSON
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            output = output[json_start:json_end]
        
        data = json.loads(output)
        match_pct = data.get("match_percentage", 0)
        
        return min(match_pct / 100.0, 1.0)
        
    except Exception as e:
        # Fallback to simple matching
        cv_skills_lower = [s.lower().strip() for s in cv_skills]
        required_lower = [s.lower().strip() for s in required_skills]
        
        matches = 0
        for req_skill in required_lower:
            for cv_skill in cv_skills_lower:
                if req_skill == cv_skill or req_skill in cv_skill or cv_skill in req_skill:
                    matches += 1
                    break
        
        return min(matches / len(required_skills), 1.0) if required_skills else 0.0

def compute_experience_match(cv_exp, required_exp):
    """Compute experience match score."""
    if required_exp == 0:
        return 1.0
    
    if cv_exp >= required_exp:
        # Perfect match if meets requirement
        if cv_exp > required_exp * 3:
            return 0.85  # Slight penalty if very overqualified
        return 1.0
    else:
        # Graduated penalty
        ratio = cv_exp / required_exp
        if ratio >= 0.75:
            return 0.8
        elif ratio >= 0.5:
            return 0.5
        else:
            return max(0.2, ratio)

def compute_match_score(jd_summary, cv_summary, cv_text="", jd_text=""):
    """Enhanced matching with multiple scoring factors."""
    
    # Parse extracted information
    cv_info = parse_cv_extraction(cv_summary)
    jd_info = parse_jd_extraction(jd_summary)
    
    # Use original texts if available
    text_for_cv = cv_text if cv_text else cv_info["raw_text"]
    text_for_jd = jd_text if jd_text else jd_info["raw_text"]
    
    # 1. Semantic Similarity (20% weight)
    emb_cv = get_embedding(text_for_cv)
    emb_jd = get_embedding(text_for_jd)
    semantic_score = cosine_similarity(emb_cv, emb_jd)
    
    # 2. Keyword Overlap (20% weight)
    keyword_score = compute_keyword_overlap(cv_info["keywords"], jd_info["keywords"])
    
    # 3. Skills Match (50% weight) - most important
    required_match, preferred_match = compute_skill_match(
        cv_info["skills"],
        jd_info["required_skills"],
        jd_info["preferred_skills"]
    )
    skills_score = (required_match * 0.85) + (preferred_match * 0.15)
    
    # 4. Experience Match (10% weight)
    experience_score = compute_experience_match(
        cv_info["experience_years"],
        jd_info["min_experience"]
    )
    
    # Weighted final score
    final_score = (
        semantic_score * 0.20 +
        keyword_score * 0.20 +
        skills_score * 0.50 +
        experience_score * 0.10
    )
    
    final_percentage = round(final_score * 100, 2)
    
    breakdown = {
        "semantic": round(semantic_score * 100, 2),
        "keywords": round(keyword_score * 100, 2),
        "skills": round(skills_score * 100, 2),
        "required_skills": round(required_match * 100, 2),
        "preferred_skills": round(preferred_match * 100, 2),
        "experience": round(experience_score * 100, 2)
    }
    
    return final_percentage, breakdown

def process_candidate_matching():
    """Enhanced matching with multi-factor scoring and LLM-based parsing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, cv_text FROM candidates WHERE match_score IS NULL")
    candidates = cursor.fetchall()

    cursor.execute("SELECT id, jd_summary FROM jobs WHERE jd_summary IS NOT NULL")
    jobs = cursor.fetchall()

    if not candidates:
        print("ℹ️  No new candidates to process.")
        conn.close()
        return
    
    if not jobs:
        print("⚠️  No job descriptions available.")
        conn.close()
        return

    print(f"\n{'='*70}")
    print(f"🔍 ENHANCED MATCHING SYSTEM v3.0 (LLM-Based Parsing)")
    print(f"{'='*70}")
    print(f"📋 Candidates: {len(candidates)} | 💼 Jobs: {len(jobs)}")
    print(f"{'='*70}\n")

    # Pre-process job descriptions
    print("🔄 Analyzing job requirements...\n")
    job_requirements = {}
    for job_id, jd_summary in jobs:
        jd_extracted = extract_jd_requirements(jd_summary)
        jd_info = parse_jd_extraction(jd_extracted)
        job_requirements[job_id] = {
            "summary": jd_summary,
            "extracted": jd_extracted,
            "parsed": jd_info
        }
        print(f"  ✓ Job {job_id}: {len(jd_info['required_skills'])} required, "
              f"{len(jd_info['preferred_skills'])} preferred, {len(jd_info['keywords'])} keywords")
    
    print(f"\n{'='*70}\n")

    # Process each candidate
    for idx, (candidate_id, cv_text) in enumerate(candidates, 1):
        print(f"👤 Candidate {candidate_id} ({idx}/{len(candidates)})")
        print(f"{'-'*70}")
        
        print("  📊 Extracting profile...")
        cv_summary = extract_skills_from_cv(cv_text)
        cv_info = parse_cv_extraction(cv_summary)
        
        print(f"  ✓ Skills: {len(cv_info['skills'])}", end="")
        if cv_info['skills'][:3]:
            print(f" ({', '.join(cv_info['skills'][:3])}...)")
        else:
            print()
        print(f"  ✓ Experience: {cv_info['experience_years']} years")
        print(f"  ✓ Keywords: {len(cv_info['keywords'])}", end="")
        if cv_info['keywords'][:3]:
            print(f" ({', '.join(cv_info['keywords'][:3])}...)")
        else:
            print()

        best_score = 0
        best_job_id = None
        best_breakdown = None

        print(f"\n  🎯 Matching against {len(jobs)} positions:\n")
        for job_id, jd_summary in jobs:
            jd_extracted = job_requirements[job_id]["extracted"]
            
            score, breakdown = compute_match_score(
                jd_extracted, 
                cv_summary,
                cv_text,
                jd_summary
            )
            
            print(f"    Job {job_id}: {score}% match")
            print(f"      ├─ Skills: {breakdown['skills']}% (Req: {breakdown['required_skills']}%, Pref: {breakdown['preferred_skills']}%)")
            print(f"      ├─ Keywords: {breakdown['keywords']}%")
            print(f"      ├─ Semantic: {breakdown['semantic']}%")
            print(f"      └─ Experience: {breakdown['experience']}%")

            if score > best_score:
                best_score = score
                best_job_id = job_id
                best_breakdown = breakdown

        try:
            cursor.execute(
                "UPDATE candidates SET match_score = ?, matched_job_id = ? WHERE id = ?",
                (best_score, best_job_id, candidate_id)
            )
            
            print(f"\n  ✅ BEST MATCH: Job {best_job_id} with {best_score}% compatibility")
            print(f"     Skills={best_breakdown['skills']}% | Keywords={best_breakdown['keywords']}% | "
                  f"Semantic={best_breakdown['semantic']}% | Exp={best_breakdown['experience']}%")
            
        except Exception as e:
            print(f"  ❌ Database error: {e}")
        
        print(f"{'-'*70}\n")

    conn.commit()
    conn.close()
    
    print(f"{'='*70}")
    print(f"🎉 MATCHING COMPLETE - {len(candidates)} candidates processed")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    process_candidate_matching()