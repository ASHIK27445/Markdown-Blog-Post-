import json

# File path
BLOGS_FILE = 'blogs.json'

# Keyword-to-group mapping
GROUP_KEYWORDS = {
    "React": "Frontend Development",
    "Theme": "Frontend Design",
    "Python": "Backend Development",
    "Flask": "Backend Development",
    "JavaScript": "Frontend Development"
}

def assign_groups(file_path=BLOGS_FILE):
    try:
        # Load JSON file safely
        with open(file_path, 'r', encoding='utf-8') as f:
            blogs = json.load(f)

        # Assign 'group' if missing
        for blog_id, blog_data in blogs.items():
            if 'group' not in blog_data:
                title = blog_data.get("title", "")
                assigned = False
                for keyword, group_name in GROUP_KEYWORDS.items():
                    if keyword.lower() in title.lower():
                        blog_data["group"] = group_name
                        assigned = True
                        break
                if not assigned:
                    blog_data["group"] = "General"

        # Write back to JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(blogs, f, indent=4, ensure_ascii=False)

        print("✅ All blogs now have a 'group' field safely!")

    except FileNotFoundError:
        print(f"❌ File '{file_path}' not found!")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decoding error: {e}")

# Run the function
assign_groups()
