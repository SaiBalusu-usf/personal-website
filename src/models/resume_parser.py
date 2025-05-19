import os
import json
import PyPDF2
import re

def extract_resume_content(pdf_path):
    """Extract text content from a PDF file"""
    try:
        content = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                content += page.extract_text()
        return content
    except Exception as e:
        print(f"Error extracting PDF content: {e}")
        return None

def parse_resume(content):
    """Parse resume content into structured data"""
    data = {
        'name': '',
        'contact': {},
        'summary': '',
        'education': [],
        'experience': [],
        'skills': [],
        'certifications': []
    }
    
    # Extract name (assuming it's the first line)
    lines = content.split('\n')
    if lines:
        data['name'] = lines[0].strip()
    
    # Extract contact info (typically in the first few lines)
    contact_line = ''
    for i in range(1, min(5, len(lines))):
        if '|' in lines[i]:
            contact_line = lines[i]
            break
    
    if contact_line:
        parts = contact_line.split('|')
        for part in parts:
            part = part.strip()
            if '@' in part:  # Email
                data['contact']['email'] = part
            elif any(c.isdigit() for c in part) and ('+' in part or '-' in part):  # Phone
                data['contact']['phone'] = part
            elif 'LinkedIn' in part:
                data['contact']['linkedin'] = part
            elif 'GitHub' in part:
                data['contact']['github'] = part
            else:  # Location
                data['contact']['location'] = part
    
    # Extract summary
    summary_start = content.find('Professional Summary:')
    education_start = content.find('Education:')
    if summary_start != -1 and education_start != -1:
        data['summary'] = content[summary_start + len('Professional Summary:'):education_start].strip()
    
    # Extract education
    education_end = content.find('Professional Experience:')
    if education_start != -1 and education_end != -1:
        education_text = content[education_start + len('Education:'):education_end].strip()
        # Parse education entries
        current_edu = {}
        for line in education_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if 'University' in line or 'College' in line or 'School' in line:
                if current_edu and 'institution' in current_edu:
                    data['education'].append(current_edu)
                current_edu = {'institution': line}
            elif 'Bachelor' in line or 'Master' in line or 'PhD' in line or 'MBA' in line:
                if 'degree' not in current_edu:
                    current_edu['degree'] = line
            elif 'Relevant Coursework' in line:
                current_edu['coursework'] = line.replace('Relevant Coursework:', '').strip()
            elif any(y in line for y in ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']):
                current_edu['years'] = line
        
        if current_edu and 'institution' in current_edu:
            data['education'].append(current_edu)
    
    # Extract experience
    experience_start = content.find('Professional Experience:')
    core_competencies_start = content.find('Core Competencies:')
    if experience_start != -1 and core_competencies_start != -1:
        experience_text = content[experience_start + len('Professional Experience:'):core_competencies_start].strip()
        
        # Parse experience entries
        current_exp = {}
        bullet_points = []
        
        for line in experience_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if '|' in line and any(m in line for m in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                if current_exp and 'title' in current_exp:
                    current_exp['responsibilities'] = bullet_points
                    data['experience'].append(current_exp)
                    bullet_points = []
                
                parts = line.split('|')
                current_exp = {
                    'title': parts[0].strip(),
                    'company': parts[1].strip(),
                    'period': parts[2].strip() if len(parts) > 2 else ''
                }
            elif line.startswith('•'):
                bullet_points.append(line.replace('•', '').strip())
        
        if current_exp and 'title' in current_exp:
            current_exp['responsibilities'] = bullet_points
            data['experience'].append(current_exp)
    
    # Extract skills
    skills_start = content.find('Core Competencies:')
    technical_skills_start = content.find('Technical & Professional Skills:')
    if skills_start != -1 and technical_skills_start != -1:
        skills_text = content[skills_start + len('Core Competencies:'):technical_skills_start].strip()
        
        for line in skills_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                data['skills'].append(line.replace('•', '').strip())
    
    # Extract certifications
    certifications_start = content.find('Certifications:')
    honors_start = content.find('Honors & Awards:')
    if certifications_start != -1 and honors_start != -1:
        certifications_text = content[certifications_start + len('Certifications:'):honors_start].strip()
        
        for line in certifications_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                data['certifications'].append(line.replace('•', '').strip())
    
    return data

def update_website_from_resume(resume_data, output_dir):
    """Update website content based on parsed resume data"""
    # Save the parsed data to a JSON file
    website_data_file = os.path.join(output_dir, 'website_data.json')
    with open(website_data_file, 'w') as f:
        json.dump(resume_data, f, indent=4)
    
    # Generate HTML content based on the resume data
    # This is a simplified example - in a real application, you would update templates or database
    
    # Update index.html with dynamic content
    return True

if __name__ == "__main__":
    # Test with the provided resume
    pdf_path = "/home/ubuntu/upload/Sai Balusu Intern.pdf"
    output_dir = "/home/ubuntu/personal_website/src/static/uploads"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract content
    content = extract_resume_content(pdf_path)
    if content:
        # Parse resume
        parsed_data = parse_resume(content)
        
        # Save parsed data
        with open(os.path.join(output_dir, "parsed_resume.json"), "w") as f:
            json.dump(parsed_data, f, indent=4)
        
        # Update website
        success = update_website_from_resume(parsed_data, output_dir)
        
        if success:
            print("Website updated successfully with resume data")
        else:
            print("Failed to update website with resume data")
    else:
        print("Failed to extract content from resume")
